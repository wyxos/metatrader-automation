import sqlite3
import logging
import time
import json
import sys
import os

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from processMessage import process_message

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Test message
test_message = "XAUUSD buy 3301 sl 3294 tp 3304 tp 3307 tp 3310 tp 3313"
test_channel = "Trade with DD"  # Replace with a channel name that exists in your database

# Process the message
logging.info(f"Processing test message: {test_message}")
logging.info(f"Using channel: {test_channel}")
process_message(test_message, test_channel)

# Connect to the database
conn = sqlite3.connect('telegram_mt5_logs.db')
cursor = conn.cursor()

# Get the latest log entry
cursor.execute("SELECT id, channel, account_name, parameters, trade_response FROM logs ORDER BY id DESC LIMIT 1")
log = cursor.fetchone()

if log:
    logging.info(f"Latest log entry:")
    logging.info(f"  - ID: {log[0]}")
    logging.info(f"  - Channel: {log[1]}")
    logging.info(f"  - Account Name: {log[2]}")
    logging.info(f"  - Parameters: {log[3]}")
    logging.info(f"  - Trade Response: {log[4]}")

    if log[2] == "default":
        logging.error("Account name is still 'default'")
    else:
        logging.info(f"Account name is correctly set to: {log[2]}")
else:
    logging.warning("No log entries found")

# Close the connection
conn.close()
