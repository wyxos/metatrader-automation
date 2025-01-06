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
from fetchChannels import list_and_save_channels

# Properly run the async coroutine
asyncio.run(list_and_save_channels())

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

def get_enabled_channels():
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    # Use REPLACE to remove '-' from telegram_id
    cursor.execute("SELECT REPLACE(telegram_id, '-', '') AS cleaned_id FROM channels WHERE enabled = 1")
    rows = cursor.fetchall()
    conn.close()
    return [int(row[0]) for row in rows]  # Convert to integers if necessary

async def start_telegram_client():
#     @client.on(events.NewMessage(chats=from_chats))  # Automatically filters messages by `from_chats`
    async def handler(event):
        # Extract the chat and message details
        enabled_channels = get_enabled_channels()
        print("Enabled channels without '-' sign:", enabled_channels)
        chat = await event.get_chat()
        if chat.id not in enabled_channels:
            return
        message = event.message.message  # Get the actual message text
        chat_id = chat.id  # Get the chat ID
        chat_title = chat.title  # Get the chat title

        # Format the message details into a single line
        log_line = f"Chat ID: {chat_id}, Chat Title: {chat_title}, Message: {message}"

        # Display the formatted message details
        logging.info(log_line)

        # Only process messages if there's a valid message text
        if message:
            process_message(message, chat_title)
        else:
            logging.info('No message found.')

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
