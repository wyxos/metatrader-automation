import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession
from dotenv import load_dotenv
import os
import sqlite3

# Load environment variables
load_dotenv()

# Telegram API credentials
api_id = os.getenv('TELEGRAM_API_ID')
api_hash = os.getenv('TELEGRAM_API_HASH')
session_string = os.getenv('TELEGRAM_SESSION_STRING')

# Database setup
db_file = 'telegram_mt5_logs.db'
conn = sqlite3.connect(db_file)
cursor = conn.cursor()

# Create the channels table if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS channels (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id INTEGER UNIQUE,
        name TEXT,
        enabled BOOLEAN DEFAULT 0
    )
''')
conn.commit()

async def list_and_save_channels():
    async with TelegramClient(StringSession(session_string), api_id, api_hash) as client:
        # Get all dialogs (chats, groups, channels)
        dialogs = await client.get_dialogs()

        # Filter only channels and insert them into the database
        print("Listing and saving all channels:")
        for dialog in dialogs:
            if dialog.is_channel:
                telegram_id = dialog.id
                name = dialog.title

                # Check if the channel already exists in the database
                cursor.execute('SELECT telegram_id FROM channels WHERE telegram_id = ?', (telegram_id,))
                exists = cursor.fetchone()

                if not exists:
                    # Insert the channel into the database
                    cursor.execute(
                        'INSERT INTO channels (telegram_id, name) VALUES (?, ?)',
                        (telegram_id, name)
                    )
#                     print(f"Saved Channel: ID {telegram_id}, Name {name}")
#                 else:
#                     print(f"Channel already exists: ID {telegram_id}, Name {name}")

        # Commit the changes
        conn.commit()

# Run the script
if __name__ == "__main__":
    try:
        asyncio.run(list_and_save_channels())
        print("Channels have been saved to the database.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()
        input("Press Enter to exit...")
