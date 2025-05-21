import sqlite3
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Connect to the database
conn = sqlite3.connect('telegram_mt5_logs.db')
cursor = conn.cursor()

# Get table structure for logs table
cursor.execute("PRAGMA table_info(logs)")
columns = cursor.fetchall()

logging.info("Logs table structure:")
for column in columns:
    logging.info(f"  - {column[1]} ({column[2]})")

# Get a sample row from logs table
cursor.execute("SELECT * FROM logs LIMIT 1")
sample_row = cursor.fetchone()

if sample_row:
    logging.info(f"Sample row from logs table (columns: {len(sample_row)}, values: {len(columns)}):")
    for i, column in enumerate(columns):
        if i < len(sample_row):
            logging.info(f"  - {column[1]}: {sample_row[i]}")
        else:
            logging.info(f"  - {column[1]}: <missing value>")
else:
    logging.warning("No rows found in logs table")

# Close the connection
conn.close()
