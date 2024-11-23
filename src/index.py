import re
from telethon import TelegramClient, events
from telethon.sessions import StringSession
import os
from dotenv import load_dotenv, set_key
import asyncio
import sqlite3
import time
import logging
import json
from cleanMessage import cleanMessage
from validateOrder import validateOrder
from sendOrder import sendOrder

# Load environment variables
load_dotenv()

# Telegram API credentials
api_id = os.getenv('TELEGRAM_API_ID')
api_hash = os.getenv('TELEGRAM_API_HASH')
session_string = os.getenv('TELEGRAM_SESSION_STRING')

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
        parameters TEXT,
        trade_response TEXT,
        exception TEXT,
        created_at TEXT
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

# List of specific channel IDs to monitor
from_chats = [
   1001835439118, 1001929659163, 1001967476990, 1001452557919,
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
        message = event.message.message
        if not message:
            logging.info('No message found.')
            return

        # Process the message
        process_message(message)

    await client.run_until_disconnected()

# Main function
if __name__ == "__main__":
    # Start Telegram client
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(initialize_telegram_client())
    loop.run_until_complete(start_telegram_client())

# Close SQLite connection
conn.close()
