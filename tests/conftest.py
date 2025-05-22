import pytest
from unittest.mock import MagicMock, patch
import sqlite3
import os
import sys

# Add the src directory to the Python path so we can import modules from there
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

# Mock for MetaTrader5
@pytest.fixture
def mock_mt5():
    with patch('MetaTrader5.initialize') as mock_initialize, \
         patch('MetaTrader5.shutdown') as mock_shutdown, \
         patch('MetaTrader5.login') as mock_login, \
         patch('MetaTrader5.account_info') as mock_account_info, \
         patch('MetaTrader5.symbol_select') as mock_symbol_select, \
         patch('MetaTrader5.symbol_info_tick') as mock_symbol_info_tick, \
         patch('MetaTrader5.order_send') as mock_order_send:

        # Configure the mocks
        mock_initialize.return_value = True
        mock_login.return_value = True

        # Mock account_info
        account_info = MagicMock()
        account_info.trade_allowed = True
        mock_account_info.return_value = account_info

        # Mock symbol_select
        mock_symbol_select.return_value = True

        # Mock symbol_info_tick
        symbol_info_tick = MagicMock()
        symbol_info_tick.ask = 2000.0
        symbol_info_tick.bid = 1999.0
        mock_symbol_info_tick.return_value = symbol_info_tick

        # Mock order_send
        order_result = MagicMock()
        order_result.retcode = 10009  # TRADE_RETCODE_DONE
        order_result.order = 12345
        order_result.volume = 0.01
        order_result.price = 2000.0
        order_result.comment = "Request executed"
        order_result._asdict = lambda: {
            "retcode": 10009,
            "deal": 67890,
            "order": 12345,
            "volume": 0.01,
            "price": 2000.0,
            "bid": 1999.0,
            "ask": 2000.0,
            "comment": "Request executed"
        }
        mock_order_send.return_value = order_result

        yield {
            "initialize": mock_initialize,
            "shutdown": mock_shutdown,
            "login": mock_login,
            "account_info": mock_account_info,
            "symbol_select": mock_symbol_select,
            "symbol_info_tick": mock_symbol_info_tick,
            "order_send": mock_order_send,
            "ORDER_TYPE_BUY": 0,
            "ORDER_TYPE_SELL": 1,
            "TRADE_ACTION_DEAL": 1,
            "ORDER_TIME_GTC": 1,
            "ORDER_FILLING_IOC": 1,
            "TRADE_RETCODE_DONE": 10009
        }

# Mock for Telegram
@pytest.fixture
def mock_telegram():
    with patch('telethon.TelegramClient') as mock_client:
        client_instance = MagicMock()
        mock_client.return_value = client_instance

        # Mock the start method
        client_instance.start.return_value = None

        # Mock the run_until_disconnected method
        client_instance.run_until_disconnected.return_value = None

        yield {
            "client": mock_client,
            "instance": client_instance
        }

# Mock for SQLite database
@pytest.fixture
def mock_db():
    # Create an in-memory SQLite database for testing
    conn = sqlite3.connect(':memory:')
    cursor = conn.cursor()

    # Create the logs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            channel TEXT,
            message TEXT,
            parameters TEXT,
            trade_response TEXT,
            is_valid_trade INTEGER DEFAULT 0,
            exception TEXT,
            created_at TEXT,
            processed_at TEXT,
            failed_at TEXT
        )
    ''')

    # Create the channels table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS channels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER,
            name TEXT,
            enabled INTEGER DEFAULT 1
        )
    ''')

    # Insert some test data
    cursor.execute('''
        INSERT INTO channels (telegram_id, name, enabled)
        VALUES (-1001234567890, 'Test Channel', 1)
    ''')

    conn.commit()

    # Create a fresh connection for each test to avoid "Cannot operate on a closed database" errors
    def get_fresh_connection(*args, **kwargs):
        # Ignore any arguments passed to this function
        new_conn = sqlite3.connect(':memory:')
        # Copy the schema and data from the original connection
        for line in conn.iterdump():
            if line != 'BEGIN;' and line != 'COMMIT;':
                new_conn.execute(line)
        new_conn.commit()
        return new_conn

    # Create a patch for sqlite3.connect
    with patch('sqlite3.connect') as mock_connect:
        # Return a fresh connection each time sqlite3.connect is called
        mock_connect.side_effect = get_fresh_connection
        # For the first call, return the original connection
        mock_connect.return_value = conn

        yield {
            "connect": mock_connect,
            "conn": conn,
            "cursor": cursor,
            "get_fresh_connection": get_fresh_connection
        }

        # We're not closing the connection here to avoid "Cannot operate on a closed database" errors
        # In a real application, we would need to ensure the connection is closed properly

# Mock for environment variables
@pytest.fixture
def mock_env():
    env_vars = {
        'TELEGRAM_API_ID': '12345',
        'TELEGRAM_API_HASH': 'abcdef1234567890',
        'TELEGRAM_SESSION_STRING': 'test_session_string',
        'MT5_ACCOUNT': '12345',
        'MT5_PASSWORD': 'password',
        'MT5_SERVER': 'Test-Server'
    }

    with patch.dict('os.environ', env_vars), \
         patch('dotenv.load_dotenv') as mock_load_dotenv:
        mock_load_dotenv.return_value = True
        yield env_vars
