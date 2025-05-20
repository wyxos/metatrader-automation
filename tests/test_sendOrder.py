import pytest
from unittest.mock import patch, MagicMock
import json
from sendOrder import sendOrder

# Test cases for sendOrder function
@pytest.mark.usefixtures("mock_mt5")
class TestSendOrder:

    def test_send_buy_order_success(self, mock_mt5):
        # Test sending a successful buy order
        order_data = {
            "signal": "buy",
            "symbol": "XAUUSD",
            "price": 2000.0,
            "sl": 1990.0,
            "tp": [2010.0, 2020.0]
        }

        # Call the function with the first TP value and explicit shutdown
        result = sendOrder(order_data, order_data["tp"][0], shutdown_after=True)

        # Verify the result
        assert result["success"] is True
        assert "result" in result
        assert result["result"]["retcode"] == 10009  # TRADE_RETCODE_DONE

        # Verify that the MetaTrader functions were called correctly
        mock_mt5["initialize"].assert_called_once()
        mock_mt5["account_info"].assert_called_once()
        mock_mt5["symbol_select"].assert_called_once_with("XAUUSD", True)
        mock_mt5["symbol_info_tick"].assert_called_once_with("XAUUSD")
        mock_mt5["order_send"].assert_called_once()
        mock_mt5["shutdown"].assert_called_once()

        # Verify the order request parameters
        order_request = mock_mt5["order_send"].call_args[0][0]
        assert order_request["symbol"] == "XAUUSD"
        assert order_request["type"] == mock_mt5["ORDER_TYPE_BUY"]
        assert order_request["sl"] == 1990.0
        assert order_request["tp"] == 2010.0
        assert order_request["volume"] == 0.01

    def test_send_sell_order_success(self, mock_mt5):
        # Test sending a successful sell order
        order_data = {
            "signal": "sell",
            "symbol": "XAUUSD",
            "price": 2000.0,
            "sl": 2010.0,
            "tp": [1990.0]
        }

        # Call the function with explicit shutdown
        result = sendOrder(order_data, order_data["tp"][0], shutdown_after=True)

        # Verify the result
        assert result["success"] is True
        assert "result" in result

        # Verify that the MetaTrader functions were called correctly
        mock_mt5["initialize"].assert_called_once()
        mock_mt5["order_send"].assert_called_once()

        # Verify the order request parameters
        order_request = mock_mt5["order_send"].call_args[0][0]
        assert order_request["symbol"] == "XAUUSD"
        assert order_request["type"] == mock_mt5["ORDER_TYPE_SELL"]
        assert order_request["sl"] == 2010.0
        assert order_request["tp"] == 1990.0

    def test_initialization_failure(self, mock_mt5):
        # Test handling of MetaTrader initialization failure
        mock_mt5["initialize"].return_value = False

        order_data = {
            "signal": "buy",
            "symbol": "XAUUSD",
            "price": 2000.0,
            "sl": 1990.0,
            "tp": [2010.0]
        }

        # Call the function
        result = sendOrder(order_data, order_data["tp"][0], shutdown_after=True)

        # Verify the result
        assert result["success"] is False
        assert "error" in result
        assert "Initialization failed" in result["error"]

        # Verify that only initialize was called
        mock_mt5["initialize"].assert_called_once()
        mock_mt5["account_info"].assert_not_called()
        mock_mt5["order_send"].assert_not_called()

    def test_account_info_failure(self, mock_mt5):
        # Test handling of account info retrieval failure
        mock_mt5["account_info"].return_value = None

        order_data = {
            "signal": "buy",
            "symbol": "XAUUSD",
            "price": 2000.0,
            "sl": 1990.0,
            "tp": [2010.0]
        }

        # Call the function
        result = sendOrder(order_data, order_data["tp"][0], shutdown_after=True)

        # Verify the result
        assert result["success"] is False
        assert "error" in result
        assert "Account information retrieval failed" in result["error"]

        # Verify that initialize and account_info were called, but not order_send
        mock_mt5["initialize"].assert_called_once()
        mock_mt5["account_info"].assert_called_once()
        mock_mt5["order_send"].assert_not_called()
        mock_mt5["shutdown"].assert_called_once()

    def test_autotrading_disabled(self, mock_mt5):
        # Test handling of disabled autotrading
        account_info = MagicMock()
        account_info.trade_allowed = False
        mock_mt5["account_info"].return_value = account_info

        order_data = {
            "signal": "buy",
            "symbol": "XAUUSD",
            "price": 2000.0,
            "sl": 1990.0,
            "tp": [2010.0]
        }

        # Call the function
        result = sendOrder(order_data, order_data["tp"][0], shutdown_after=True)

        # Verify the result
        assert result["success"] is False
        assert "error" in result
        assert "AutoTrading is disabled" in result["error"]

        # Verify that initialize and account_info were called, but not order_send
        mock_mt5["initialize"].assert_called_once()
        mock_mt5["account_info"].assert_called_once()
        mock_mt5["order_send"].assert_not_called()
        mock_mt5["shutdown"].assert_called_once()

    def test_invalid_signal(self, mock_mt5):
        # Test handling of invalid signal
        order_data = {
            "signal": "invalid",  # Not "buy" or "sell"
            "symbol": "XAUUSD",
            "price": 2000.0,
            "sl": 1990.0,
            "tp": [2010.0]
        }

        # Call the function
        result = sendOrder(order_data, order_data["tp"][0])

        # Verify the result
        assert result["success"] is False
        assert "error" in result
        assert "Invalid signal" in result["error"]

        # Verify that initialize and account_info were called, but not order_send
        mock_mt5["initialize"].assert_called_once()
        mock_mt5["account_info"].assert_called_once()
        mock_mt5["order_send"].assert_not_called()
        mock_mt5["shutdown"].assert_called_once()

    def test_symbol_select_failure(self, mock_mt5):
        # Test handling of symbol selection failure
        mock_mt5["symbol_select"].return_value = False

        order_data = {
            "signal": "buy",
            "symbol": "XAUUSD",
            "price": 2000.0,
            "sl": 1990.0,
            "tp": [2010.0]
        }

        # Call the function
        result = sendOrder(order_data, order_data["tp"][0])

        # Verify the result
        assert result["success"] is False
        assert "error" in result
        assert "Symbol XAUUSD not available" in result["error"]

        # Verify that initialize, account_info, and symbol_select were called, but not order_send
        mock_mt5["initialize"].assert_called_once()
        mock_mt5["account_info"].assert_called_once()
        mock_mt5["symbol_select"].assert_called_once_with("XAUUSD", True)
        mock_mt5["order_send"].assert_not_called()
        mock_mt5["shutdown"].assert_called_once()

    def test_symbol_info_tick_failure(self, mock_mt5):
        # Test handling of symbol info tick failure
        mock_mt5["symbol_info_tick"].return_value = None

        order_data = {
            "signal": "buy",
            "symbol": "XAUUSD",
            "price": 2000.0,
            "sl": 1990.0,
            "tp": [2010.0]
        }

        # Call the function
        result = sendOrder(order_data, order_data["tp"][0])

        # Verify the result
        assert result["success"] is False
        assert "error" in result
        assert "Tick information for symbol XAUUSD unavailable" in result["error"]

        # Verify that initialize, account_info, symbol_select, and symbol_info_tick were called, but not order_send
        mock_mt5["initialize"].assert_called_once()
        mock_mt5["account_info"].assert_called_once()
        mock_mt5["symbol_select"].assert_called_once_with("XAUUSD", True)
        mock_mt5["symbol_info_tick"].assert_called_once_with("XAUUSD")
        mock_mt5["order_send"].assert_not_called()
        mock_mt5["shutdown"].assert_called_once()

    def test_order_send_failure(self, mock_mt5):
        # Test handling of order send failure
        order_result = MagicMock()
        order_result.retcode = 10016  # Some error code
        order_result._asdict = lambda: {
            "retcode": 10016,
            "comment": "Order failed"
        }
        mock_mt5["order_send"].return_value = order_result

        order_data = {
            "signal": "buy",
            "symbol": "XAUUSD",
            "price": 2000.0,
            "sl": 1990.0,
            "tp": [2010.0]
        }

        # Call the function
        result = sendOrder(order_data, order_data["tp"][0])

        # Verify the result
        assert result["success"] is False
        assert "error" in result
        assert "Order failed with retcode 10016" in result["error"]

        # Verify that all functions were called
        mock_mt5["initialize"].assert_called_once()
        mock_mt5["account_info"].assert_called_once()
        mock_mt5["symbol_select"].assert_called_once_with("XAUUSD", True)
        mock_mt5["symbol_info_tick"].assert_called_once_with("XAUUSD")
        mock_mt5["order_send"].assert_called_once()
        mock_mt5["shutdown"].assert_called_once()
