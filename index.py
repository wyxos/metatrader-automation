from telethon import TelegramClient, events
from telethon.sessions import StringSession
import logging
import subprocess
import json
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Configure logging to show INFO level messages
logging.basicConfig(level=logging.INFO)

# Get the variables from the environment
api_id = int(os.getenv('API_ID'))
api_hash = os.getenv('API_HASH')
session_string = os.getenv('SESSION_STRING')

# Create the Telegram client
client = TelegramClient(StringSession(session_string), api_id, api_hash)

from_chats = [
    {"id": 1882105856, "name": "CAC40 + FRA40 TRADING SIGNALS"},
    {"id": 1316632057, "name": "COMMITMENTS OF TRADER"},
    {"id": 1925709440, "name": "Forex Signal Factory (free)"},
    {"id": 1622798974, "name": "Forex US"},
    {"id": 1619062611, "name": "GBPUSD FX SIGNALS(firepips signal"},
    {"id": 2069311392, "name": "Gold Xpert"},
    {"id": 1986643106, "name": "ICT CHARTIST"},
    {"id": 1945187058, "name": "ICT OFFICIAL ACADEMY"},
    {"id": 1792592079, "name": "KR CAPITALS"},
    {"id": 1753932904, "name": "META TRADER 4&5 FOREX SIGNALS"},
    {"id": 1447871772, "name": "Market Makers FX"},
    {"id": 1240559594, "name": "Meta Trader 4 Signals (Free)"},
    {"id": 1924713375, "name": "Mr. Gold | Forex Signals (Free)"},
    {"id": 1972491378, "name": "NAS100 FOREX TRADING SIGNALS"},
    {"id": 1840185808, "name": "Smart Money Trader"},
    {"id": 1569743424, "name": "Snipers FX"},
    {"id": 1594662743, "name": "Trade with DD"},
    {"id": 1894282005, "name": "UKOIL + US30 SIGNAL"},
    {"id": 1898607875, "name": "US30 DOW JONES"},
    {"id": 1633769909, "name": "US30 Eagle"},
    {"id": 1253126344, "name": "US30 EMPIRE FREE FOREX SIGNALS"},
    {"id": 1206081401, "name": "VANTAGE FOREX SIGNALS OFFICIAL"},
    {"id": 1835439118, "name": "BTCUSD SIGNALS (FREE)"},
    {"id": 1967476990, "name": "FOXYICTRADER (P.G)"},
    {"id": 1983270625, "name": "BTCUSD FREE FOREX SIGNALS"},
    {"id": 1555470470, "name": "US30 KINGDOM"},
    {"id": 1799805861, "name": "Pro Forex System"},
    {"id": 2041761858, "name": "OKAKO (VIP)"},
    {"id": 1452557919, "name": "XAUUSD SIGNAL"}
]

# Define the destination chat
to_chat = -1001979329330  # Metatrader test

# Function to call the Node.js script
def process_message_with_node(message):
    try:
        result = subprocess.run(
            ['node', 'reformatTradeMessages.mjs'],
            input=message.encode('utf-8'),
            capture_output=True,
            text=True
        )
        logging.info(f"Node.js script output: {result.stdout}")
        logging.error(f"Node.js script error: {result.stderr}")

        if result.returncode == 0 and result.stdout.strip():
            try:
                return json.loads(result.stdout)
            except json.JSONDecodeError as e:
                logging.error(f"JSON decode error: {e}")
                return None
        else:
            logging.error(f"Node.js script returned non-zero exit code or empty output: {result.returncode}")
            return None
    except Exception as e:
        logging.error(f"Exception in process_message_with_node: {e}")
        return None

# Define the event handler for new messages
@client.on(events.NewMessage)
async def my_event_handler(event):
    chat = await event.get_chat()

    # Log the ID and content of the received message
    logging.info(f"Received message from chat ID {chat.id} ({chat.title}) : {event.message.text}")

    # Check if the message was received from any of the source chats
    for source_chat in from_chats:
        if chat.id == source_chat["id"]:
            # Process the message with the Node.js script
            processed_message = process_message_with_node(event.message.text)
            if processed_message:
                # Send the processed message to Metatrader using mql5 (this part will depend on how you plan to send it)
                logging.info(f"Processed message: {processed_message}")
                # Here you can send the processed message to Metatrader
            break

# Define the main coroutine
async def main():
    # Log that the bot is running
    logging.info("Bot is running...")
    # Run the client until disconnected
    await client.run_until_disconnected()

# Start the client and run the main coroutine
if __name__ == "__main__":
    logging.info("Starting the client...")
    client.start()  # Ensure the client is started
    client.loop.run_until_complete(main())