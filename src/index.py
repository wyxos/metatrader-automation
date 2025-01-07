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
from processMessage import process_message

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
   1001983270625, 1001580359379, 1001488732903, 1001684531470,
    1002108856565, 1001792592079, 1001940215945, 1001555470470,
    1001238584294, 1001668608165, 1001569845383, 1001813129462,
    1001370304351, 1001188734330, 1001483307206, 1001929659163,
    1002092887262, 1001388233385, 1001574762382, 1001230054900,
    1001925709440, 1001835439118, 1001253126344, 1001206081401,
    1001601511971, 1001891409421, 1001726348724, 1001945187058,
    1001726182732, 1001398522723, 1002097748442, 1001251070444,
    1001680297592, 1001543568673, 1001348564602, 1001473647097,
    1001192305307, 1001861135634, 1001510505546, 1001519922009,
    1001765226347, 1001240559594, 1001622798974, 1001452557919,
    1001807278108, 1001295992076, 1001967476990, 1001388562823,
    1001314533292, 1001610297526, 1001569743424, 1001293333388,
    1001092443297, 1001612126892, 1001986643106, 1001799805861,
    1001151289381, 1001894282005, 1002041761858, 1001898607875,
    1001713300969, 1001633769909, 1001924713375
]

async def start_telegram_client():
    @client.on(events.NewMessage(chats=from_chats))  # Automatically filters messages by `from_chats`
    async def handler(event):
        # Extract the chat and message details
        chat = await event.get_chat()  # Get the chat object (contains chat details)
        message = event.message.message  # Get the actual message text
        chat_id = chat.id  # Get the chat ID
        chat_title = chat.title  # Get the chat title

        # Format the message details into a single line
        log_line = f"Chat ID: {chat_id}, Chat Title: {chat_title}, Message: {message}"

        # Display the formatted message details
        logging.info(log_line)

        # Only process messages if there's a valid message text
        if message:
            process_message(message)
        else:
            logging.info('No message found.')

    await client.run_until_disconnected()

# Main function
if __name__ == "__main__":
    # clear terminal on Windows
    os.system('cls')
    # Start Telegram client
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(initialize_telegram_client())
    loop.run_until_complete(start_telegram_client())

# Close SQLite connection
conn.close()
