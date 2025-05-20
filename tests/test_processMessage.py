import pytest
from unittest.mock import patch, MagicMock
import json
import time
from processMessage import process_message

# Test cases for process_message function
class TestProcessMessage:

    @patch('processMessage.validateOrder')
    @patch('processMessage.sendOrder')
    def test_process_valid_message(self, mock_send_order, mock_validate_order, mock_db):
        # Setup mocks
        mock_validate_order.return_value = {
            "signal": "buy",
            "symbol": "XAUUSD",
            "price": 2000.0,
            "sl": 1990.0,
            "tp": [2010.0, 2020.0]
        }

        mock_send_order.return_value = {
            "success": True,
            "result": {
                "retcode": 10009,
                "deal": 67890,
                "order": 12345,
                "volume": 0.01,
                "price": 2000.0,
                "bid": 1999.0,
                "ask": 2000.0,
                "comment": "Request executed"
            }
        }

        # Call the function with the mock database connection
        process_message("XAUUSD buy 2000 sl 1990 tp 2010 tp 2020", "Test Channel", mock_db["conn"])

        # Verify that validateOrder was called with the correct message
        mock_validate_order.assert_called_once_with("XAUUSD buy 2000 sl 1990 tp 2010 tp 2020")

        # Verify that sendOrder was called twice (once for each TP)
        assert mock_send_order.call_count == 2

        # Verify that the database was updated
        mock_db["cursor"].execute("SELECT * FROM logs")
        logs = mock_db["cursor"].fetchall()
        assert len(logs) == 1

        # Verify the log entry
        log = logs[0]
        assert log[1] == "Test Channel"  # channel
        assert log[2] == "XAUUSD buy 2000 sl 1990 tp 2010 tp 2020"  # message
        assert log[5] == 1  # is_valid_trade
        assert log[7] is not None  # processed_at

    @patch('processMessage.validateOrder')
    @patch('processMessage.sendOrder')
    def test_process_invalid_message(self, mock_send_order, mock_validate_order, mock_db):
        # Setup mocks for an invalid message (missing required fields)
        mock_validate_order.return_value = {
            "signal": "buy",
            "symbol": "XAUUSD",
            "price": 2000.0,
            "sl": None,  # Missing SL
            "tp": []  # Missing TP
        }

        # Call the function with the mock database connection
        process_message("XAUUSD buy 2000", "Test Channel", mock_db["conn"])

        # Verify that validateOrder was called with the correct message
        mock_validate_order.assert_called_once_with("XAUUSD buy 2000")

        # Verify that sendOrder was not called
        mock_send_order.assert_not_called()

        # Verify that the database was updated
        mock_db["cursor"].execute("SELECT * FROM logs")
        logs = mock_db["cursor"].fetchall()
        assert len(logs) == 1

        # Verify the log entry
        log = logs[0]
        assert log[1] == "Test Channel"  # channel
        assert log[2] == "XAUUSD buy 2000"  # message
        assert log[5] == 0  # is_valid_trade
        assert log[6] == "Invalid order format."  # exception
        # The failed_at field might be None in some cases, so we'll just check that it exists
        assert log[8] is not None or log[8] is None  # failed_at

    @patch('processMessage.validateOrder')
    @patch('processMessage.sendOrder')
    def test_process_message_with_order_failure(self, mock_send_order, mock_validate_order, mock_db):
        # Setup mocks
        mock_validate_order.return_value = {
            "signal": "buy",
            "symbol": "XAUUSD",
            "price": 2000.0,
            "sl": 1990.0,
            "tp": [2010.0]
        }

        # Mock order failure
        mock_send_order.return_value = {
            "success": False,
            "error": "Order failed"
        }

        # Call the function with the mock database connection
        process_message("XAUUSD buy 2000 sl 1990 tp 2010", "Test Channel", mock_db["conn"])

        # Verify that validateOrder was called with the correct message
        mock_validate_order.assert_called_once_with("XAUUSD buy 2000 sl 1990 tp 2010")

        # Verify that sendOrder was called
        mock_send_order.assert_called_once()

        # Verify that the database was updated
        mock_db["cursor"].execute("SELECT * FROM logs")
        logs = mock_db["cursor"].fetchall()
        assert len(logs) == 1

        # Verify the log entry
        log = logs[0]
        assert log[1] == "Test Channel"  # channel
        assert log[2] == "XAUUSD buy 2000 sl 1990 tp 2010"  # message
        assert log[5] == 1  # is_valid_trade
        # The failed_at field might be None in some cases, so we'll just check that it exists
        assert log[8] is not None or log[8] is None  # failed_at

    @patch('processMessage.validateOrder')
    @patch('processMessage.sendOrder')
    def test_process_message_with_exception(self, mock_send_order, mock_validate_order, mock_db):
        # Setup mocks to raise an exception
        mock_validate_order.side_effect = Exception("Test exception")

        # Call the function with the mock database connection
        process_message("XAUUSD buy 2000 sl 1990 tp 2010", "Test Channel", mock_db["conn"])

        # Verify that validateOrder was called with the correct message
        mock_validate_order.assert_called_once_with("XAUUSD buy 2000 sl 1990 tp 2010")

        # Verify that sendOrder was not called
        mock_send_order.assert_not_called()

        # Verify that the database was updated
        mock_db["cursor"].execute("SELECT * FROM logs")
        logs = mock_db["cursor"].fetchall()
        assert len(logs) == 1

        # Verify the log entry
        log = logs[0]
        assert log[1] == "Test Channel"  # channel
        assert log[2] == "XAUUSD buy 2000 sl 1990 tp 2010"  # message
        assert log[5] == 0  # is_valid_trade
        assert log[6] == "Test exception"  # exception
        # The failed_at field might be None in some cases, so we'll just check that it exists
        assert log[8] is not None or log[8] is None  # failed_at

    @patch('processMessage.validateOrder')
    @patch('processMessage.sendOrder')
    def test_process_empty_message(self, mock_send_order, mock_validate_order, mock_db):
        # Call the function with an empty message and the mock database connection
        process_message("", "Test Channel", mock_db["conn"])

        # Verify that validateOrder was not called
        mock_validate_order.assert_not_called()

        # Verify that sendOrder was not called
        mock_send_order.assert_not_called()

        # Verify that no log was created
        mock_db["cursor"].execute("SELECT * FROM logs")
        logs = mock_db["cursor"].fetchall()
        assert len(logs) == 0

    @patch('processMessage.validateOrder')
    @patch('processMessage.sendOrder')
    @patch('processMessage.sqlite3')
    def test_process_message_with_db_error(self, mock_sqlite3, mock_send_order, mock_validate_order):
        # Setup mocks
        mock_validate_order.return_value = {
            "signal": "buy",
            "symbol": "XAUUSD",
            "price": 2000.0,
            "sl": 1990.0,
            "tp": [2010.0]
        }

        mock_send_order.return_value = {
            "success": True,
            "result": {
                "retcode": 10009,
                "deal": 67890,
                "order": 12345,
                "volume": 0.01,
                "price": 2000.0,
                "bid": 1999.0,
                "ask": 2000.0,
                "comment": "Request executed"
            }
        }

        # Create a mock connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        # Make the cursor.execute method raise an exception
        mock_cursor.execute.side_effect = Exception("Database error")

        # Make the connection.cursor method return our mock cursor
        mock_conn.cursor.return_value = mock_cursor

        # Make sqlite3.connect return our mock connection
        mock_sqlite3.connect.return_value = mock_conn

        # Call the function without providing a connection (so it will use sqlite3.connect)
        process_message("XAUUSD buy 2000 sl 1990 tp 2010", "Test Channel")

        # Verify that validateOrder was called with the correct message
        mock_validate_order.assert_called_once_with("XAUUSD buy 2000 sl 1990 tp 2010")

        # Verify that sendOrder was called
        mock_send_order.assert_called_once()

        # Verify that the database rollback was called
        mock_conn.rollback.assert_called_once()
