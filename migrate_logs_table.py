import sqlite3
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Database file
DB_FILE = 'telegram_mt5_logs.db'

def migrate_logs_table():
    """
    Migrate the logs table to remove the account_name column.
    SQLite doesn't support directly dropping columns, so we need to:
    1. Create a new table without the column
    2. Copy the data
    3. Drop the old table
    4. Rename the new table
    """
    logging.info("Starting migration of logs table to remove account_name column")

    # Connect to the database
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    try:
        # Check if account_name column exists
        cursor.execute("PRAGMA table_info(logs)")
        columns = cursor.fetchall()
        column_names = [column[1] for column in columns]

        if 'account_name' not in column_names:
            logging.info("account_name column doesn't exist in logs table. No migration needed.")
            return

        logging.info("Creating new logs table without account_name column")

        # Create a new table without the account_name column
        cursor.execute('''
            CREATE TABLE logs_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                channel TEXT,
                message TEXT,
                parameters TEXT,
                trade_response TEXT,
                is_valid_trade INTEGER,
                exception TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                processed_at TEXT,
                failed_at TEXT
            )
        ''')

        # Copy data from the old table to the new table
        logging.info("Copying data from logs to logs_new")
        cursor.execute('''
            INSERT INTO logs_new (id, channel, message, parameters, trade_response, is_valid_trade, exception, created_at, processed_at, failed_at)
            SELECT id, channel, message, parameters, trade_response, is_valid_trade, exception, created_at, processed_at, failed_at
            FROM logs
        ''')

        # Get the number of rows copied
        cursor.execute("SELECT COUNT(*) FROM logs_new")
        new_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM logs")
        old_count = cursor.fetchone()[0]

        logging.info(f"Copied {new_count} rows from logs table (original had {old_count} rows)")

        # Drop the old table
        logging.info("Dropping old logs table")
        cursor.execute("DROP TABLE logs")

        # Rename the new table
        logging.info("Renaming logs_new to logs")
        cursor.execute("ALTER TABLE logs_new RENAME TO logs")

        # Commit the changes
        conn.commit()
        logging.info("Migration completed successfully")

    except Exception as e:
        conn.rollback()
        logging.error(f"Error during migration: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_logs_table()
