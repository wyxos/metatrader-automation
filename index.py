import re
from telethon import TelegramClient, events
from telethon.sessions import StringSession
import MetaTrader5 as mt5
import os
from dotenv import load_dotenv, set_key
import asyncio
import sqlite3
import json
import time
import requests
import logging

# Load environment variables
load_dotenv()

# Telegram API credentials
api_id = os.getenv('TELEGRAM_API_ID')
api_hash = os.getenv('TELEGRAM_API_HASH')
session_string = os.getenv('TELEGRAM_SESSION_STRING')

# MetaTrader 5 login credentials
mt5_account = int(os.getenv('MT5_ACCOUNT'))  # Your MetaTrader Account Number
mt5_password = os.getenv('MT5_PASSWORD')
mt5_server = os.getenv('MT5_SERVER')

# Ollama API configuration
OLLAMA_API_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL_NAME = "llama3.2"

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

client = None

# SQLite database setup
db_file = 'telegram_mt5_logs.db'
conn = sqlite3.connect(db_file)
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        channel TEXT,
        message TEXT,
        created_at TEXT,
        is_valid_trade INTEGER,
        parameters TEXT,
        processed_at TEXT,
        failed_at TEXT,
        exception TEXT
    )
''')
conn.commit()

# Function to generate a new session string and update .env
async def regenerate_session():
    async with TelegramClient(StringSession(), api_id, api_hash) as new_client:
        await new_client.start()
        new_session_string = new_client.session.save()
        set_key('.env', 'TELEGRAM_SESSION_STRING', new_session_string)
        return new_session_string

# Initialize Telegram client
async def initialize_telegram_client():
    global client, session_string
    try:
        client = TelegramClient(StringSession(session_string), api_id, api_hash)
        await client.start()
        logging.info("Successfully connected to Telegram.")
    except Exception as e:
        session_string = await regenerate_session()
        client = TelegramClient(StringSession(session_string), api_id, api_hash)
        await client.start()
        logging.info("Successfully connected to Telegram after regenerating session string.")

# Initialize MetaTrader 5 connection
RETRY_LIMIT = 5

def mt5_initialize():
    retries = 0
    while retries < RETRY_LIMIT:
        if mt5.initialize(timeout=5000):
            login = mt5.login(mt5_account, password=mt5_password, server=mt5_server)
            if login:
                logging.info("Successfully connected to MetaTrader 5.")
                return True
            else:
                retries += 1
                time.sleep(5)
        else:
            retries += 1
            time.sleep(5)

    mt5.shutdown()
    logging.error("Failed to initialize MetaTrader 5 after multiple attempts.")
    return False

# Function to validate trade signal using Ollama LLM
def validate_trade_signal(message):
    payload = {
        "model": OLLAMA_MODEL_NAME,
        "prompt": f"Is the following message a valid trade signal? If yes, extract the action, symbol, price, tp, and sl as a JSON object. Message: '{message}'"
    }
    try:
        response = requests.post(OLLAMA_API_URL, json=payload)
        response.raise_for_status()
        data = response.json()
        if 'text' in data:
            return json.loads(data['text'])
    except requests.exceptions.RequestException as e:
        logging.error(f"Error communicating with Ollama API: {e}")
    except json.JSONDecodeError as e:
        logging.error(f"Error decoding Ollama API response: {e}")
    return None

# Place order in MetaTrader 5
def place_order(signal):
    symbol = signal['symbol']
    action = signal['action']
    price = signal['price']
    tp = signal['tp']
    sl = signal['sl']

    order_type = mt5.ORDER_TYPE_BUY if action == 'BUY' else mt5.ORDER_TYPE_SELL

    # Define order request
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": 0.1,  # Set your desired volume
        "type": order_type,
        "price": price,
        "sl": sl,
        "tp": tp,
        "deviation": 20,
        "magic": 234000,  # Magic number to identify orders
        "comment": "Telegram Signal",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    # Send the order
    result = mt5.order_send(request)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        raise Exception(f"Failed to place order: {result.retcode}. Error: {result.comment}")
    else:
        logging.info(f"Order placed successfully for record with ID {signal['id']} at {time.strftime('%Y-%m-%d %H:%M:%S')}.")

# List of specific channel IDs to monitor
from_chats = [
   1001835439118, 1001929659163, 1001967476990, 1001433646525, 1001452557919,
    1001945187058, 1001206081401, 1001240559594, 1001388233385, 1001792592079,
    1001622798974, 1001555470470, 1001925709440, 1001230054900, 1001610297526,
    1001569845383, 1001891409421, 1001894282005, 1001807278108, 1001972491378,
    1001253126344, 1001092443297, 1001799805861, 1001983270625, 1002188561438,
    1001898607875, 1002041761858, 1001986643106, 1001633769909, 1001924713375
]

# Listen for new messages from specific Telegram channels
async def start_telegram_client():
    @client.on(events.NewMessage(chats=from_chats))
    async def handler(event):
        chat = await event.get_chat()
        message = event.message.message
        created_at = time.strftime('%Y-%m-%d %H:%M:%S')
        is_valid_trade = 0
        parameters = None
        processed_at = None
        failed_at = None
        exception = None

        try:
            signal = validate_trade_signal(message)
            if signal:
                is_valid_trade = 1
                parameters = json.dumps(signal)
                place_order(signal)
                processed_at = time.strftime('%Y-%m-%d %H:%M:%S')
        except Exception as e:
            failed_at = time.strftime('%Y-%m-%d %H:%M:%S')
            exception = json.dumps({'error': str(e)})

        cursor.execute('''
            INSERT INTO logs (channel, message, created_at, is_valid_trade, parameters, processed_at, failed_at, exception)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (chat.title, message, created_at, is_valid_trade, parameters, processed_at, failed_at, exception))
        conn.commit()

    await client.run_until_disconnected()

# Main function
if __name__ == "__main__":
    # Start MetaTrader 5
    if mt5_initialize():
        # Start Telegram client
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(initialize_telegram_client())
        loop.run_until_complete(start_telegram_client())
    else:
        cursor.execute('''
            INSERT INTO logs (channel, message, created_at, is_valid_trade, parameters, processed_at, failed_at, exception)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', ('System', 'MT5 initialization failed', time.strftime('%Y-%m-%d %H:%M:%S'), 0, None, None, time.strftime('%Y-%m-%d %H:%M:%S'), json.dumps({'error': 'MT5 initialization failed after multiple attempts.'})))
        conn.commit()

# Close SQLite connection
conn.close()