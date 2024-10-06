import re
from telethon import TelegramClient, events
from telethon.sessions import StringSession
import MetaTrader5 as mt5
import os
from dotenv import load_dotenv, set_key
import asyncio
import logging

# Load environment variables
load_dotenv()

# Configure logging to show INFO level messages
logging.basicConfig(level=logging.INFO)

# Telegram API credentials
api_id = os.getenv('TELEGRAM_API_ID')
api_hash = os.getenv('TELEGRAM_API_HASH')
session_string = os.getenv('TELEGRAM_SESSION_STRING')

# MetaTrader 5 login credentials
mt5_account = int(os.getenv('MT5_ACCOUNT'))  # Your MetaTrader Account Number
mt5_password = os.getenv('MT5_PASSWORD')
mt5_server = os.getenv('MT5_SERVER')

client = None

# Function to generate a new session string and update .env
async def regenerate_session():
    async with TelegramClient(StringSession(), api_id, api_hash) as new_client:
        await new_client.start()
        new_session_string = new_client.session.save()
        set_key('.env', 'TELEGRAM_SESSION_STRING', new_session_string)
        logging.info(f"Session string regenerated and saved to .env: {new_session_string[:10]}... (truncated)")
        return new_session_string

# Initialize Telegram client
async def initialize_telegram_client():
    global client, session_string
    try:
        client = TelegramClient(StringSession(session_string), api_id, api_hash)
        await client.start()
    except Exception as e:
        logging.error(f"Error: {e}. Regenerating session string...")
        session_string = await regenerate_session()
        client = TelegramClient(StringSession(session_string), api_id, api_hash)
        await client.start()

# Channel IDs to monitor
channel_ids = [1882105856, 1316632057]

# Initialize MetaTrader 5 connection
def mt5_initialize():
    if not mt5.initialize():
        logging.error("MetaTrader5 initialization failed. Error code: %s", mt5.last_error())
        mt5.shutdown()
    login = mt5.login(mt5_account, password=mt5_password, server=mt5_server)
    if not login:
        logging.error("Failed to connect to MT5 account. Error code: %s", mt5.last_error())
    else:
        logging.info("Connected to MT5 account")

# Process message to extract trade details
def parse_signal(message):
    pattern = r'(BUY|SELL)\s+(NOW\s+)?([A-Z]+|[A-Z]+/[A-Z]+|[A-Z]+\d+)\s+(\d+(\.\d+)?)\s+TP\s+(\d+(\.\d+)?)\s+SL\s+(\d+(\.\d+)?)'
    match = re.search(pattern, message, re.IGNORECASE)
    if match:
        action = match.group(1).upper()
        symbol = match.group(3).upper()
        price = float(match.group(4))
        tp = float(match.group(6))
        sl = float(match.group(8))
        return {
            'action': action,
            'symbol': symbol,
            'price': price,
            'tp': tp,
            'sl': sl
        }
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
        logging.error(f"Failed to place order: {result.retcode}. Error: {result.comment}")
    else:
        logging.info(f"Order placed successfully for {symbol}")

# Listen for new messages from specific Telegram channels
async def start_telegram_client():
    @client.on(events.NewMessage(chats=channel_ids))
    async def handler(event):
        message = event.message.message
        logging.info(f"Received message: {message}")
        signal = parse_signal(message)
        if signal:
            logging.info(f"Received signal: {signal}")
            place_order(signal)

    await client.run_until_disconnected()

# Main function
if __name__ == "__main__":
    # Start MetaTrader 5
    mt5_initialize()

    # Start Telegram client
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(initialize_telegram_client())
    loop.run_until_complete(start_telegram_client())