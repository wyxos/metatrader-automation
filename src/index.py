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

# Function to fetch enabled channels from the database
def get_enabled_channels():
    conn = sqlite3.connect('telegram_mt5_logs.db')
    cursor = conn.cursor()
    cursor.execute('SELECT telegram_id FROM channels WHERE enabled = 1')
    rows = cursor.fetchall()
    conn.close()
    return [abs(row[0]) for row in rows]


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

async def start_telegram_client():
    from_chats = get_enabled_channels()  # Fetch enabled channel IDs dynamically

    if not from_chats:
        logging.warning("No enabled channels found. Please enable channels in the database.")
        return

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
            process_message(message, chat_title)
        else:
            logging.info('No message found.')

    await client.run_until_disconnected()

# Main async function that combines client startup and message listening
async def main():
    await initialize_telegram_client()
    try:
        await start_telegram_client()
    except asyncio.CancelledError:
        pass
    finally:
        if client and client.is_connected():
            await client.disconnect()

# Main function
if __name__ == "__main__":
    # Clear terminal on Windows
    os.system('cls')

    try:
        # Use asyncio.run for clean startup and shutdown
        asyncio.run(main())
    except KeyboardInterrupt:
        # Handle graceful shutdown on user interrupt (CTRL+C)
        logging.info("Interrupted by user. Shutting down...")
