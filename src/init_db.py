import sqlite3

DB_FILE = 'telegram_mt5_logs.db'

def initialize_database():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            channel TEXT,
            message TEXT,
            parameters TEXT,
            trade_response TEXT,
            is_valid_trade INTEGER,
            exception TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            processed_at TEXT,
            failed_at TEXT,
            account_name TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS channels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER,
            name TEXT,
            enabled INTEGER DEFAULT 1
        )
    ''')

    # Create table for MetaTrader accounts
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mt_accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_name TEXT NOT NULL,
            server_name TEXT NOT NULL,
            login_id TEXT NOT NULL,
            password TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Create table for channel-to-account mappings
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS channel_account_mappings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            channel_id INTEGER NOT NULL,
            account_id INTEGER NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (channel_id) REFERENCES channels (id) ON DELETE CASCADE,
            FOREIGN KEY (account_id) REFERENCES mt_accounts (id) ON DELETE CASCADE
        )
    ''')

    conn.commit()
    conn.close()
