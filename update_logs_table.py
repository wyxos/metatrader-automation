import sqlite3
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Connect to the database
conn = sqlite3.connect('telegram_mt5_logs.db')
cursor = conn.cursor()

# Check if account_name column exists
cursor.execute("PRAGMA table_info(logs)")
columns = cursor.fetchall()
column_names = [column[1] for column in columns]

if 'account_name' not in column_names:
    logging.info("Adding account_name column to logs table...")
    cursor.execute("ALTER TABLE logs ADD COLUMN account_name TEXT")
    conn.commit()
    logging.info("account_name column added successfully")
else:
    logging.info("account_name column already exists in logs table")

# Verify the table structure
cursor.execute("PRAGMA table_info(logs)")
columns = cursor.fetchall()
logging.info("Updated logs table structure:")
for column in columns:
    logging.info(f"  - {column[1]} ({column[2]})")

# Close the connection
conn.close()

logging.info("Database update completed")
