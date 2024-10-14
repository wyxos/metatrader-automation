from telethon import TelegramClient
import os
from dotenv import load_dotenv
import asyncio

# Load environment variables from .env file
load_dotenv()

# Replace `YOUR_API_ID`, `YOUR_API_HASH`, and `YOUR_SESSION_STRING` with your actual values from the environment
api_id = os.getenv('TELEGRAM_API_ID')
api_hash = os.getenv('TELEGRAM_API_HASH')
session_string = os.getenv('TELEGRAM_SESSION_STRING')

# Create a Telegram client session
client = TelegramClient('anon', api_id, api_hash)

async def main():
    # Iterate through all the dialogs
    async for dialog in client.iter_dialogs():
        # Printing the name and ID of each dialog
        print(dialog.name, 'has ID', dialog.id)

# Running the client
if __name__ == '__main__':
    with client:
        client.loop.run_until_complete(main())