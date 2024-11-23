import unittest
from unittest.mock import patch, MagicMock
import time
import json
import logging
from index import mt5_initialize, place_order
import MetaTrader5 as mt5

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class TestTelegramMT5(unittest.TestCase):

    @patch('index.validate_trade_signal')
    @patch('index.mt5.order_send')
    @patch('index.time.strftime', side_effect=lambda fmt: '2024-11-10 10:00:00')
    def test_validate_trade_signal_and_place_order(self, mock_strftime, mock_order_send, mock_validate_trade_signal):
        # Mocking inputs
        message = 'GOLD BUY NOW @2730-2727\nSL 2724\nTP 2732.54\nTP 2737.95\nLayering slowly use proper lot size'
        mock_validate_trade_signal.return_value = {
            'symbol': 'GOLD',
            'action': 'BUY',
            'price': 2730,
            'sl': 2724,
            'tp': [2732.54, 2737.95],
            'id': 1
        }
        mock_order_send.return_value = MagicMock(retcode=mt5.TRADE_RETCODE_DONE)

        # Testing validate_trade_signal and place_order
        signal = mock_validate_trade_signal(message)
        try:
            place_order(signal)
            logging.info("Order placed successfully.")
        except Exception as e:
            self.fail(f"place_order raised an exception unexpectedly: {e}")

        # Assert
        mock_validate_trade_signal.assert_called_once_with(message)
        mock_order_send.assert_called_once()

    @patch('index.mt5.initialize', side_effect=lambda timeout: False)
    @patch('index.time.sleep', return_value=None)  # Mock time.sleep for fast tests
    def test_mt5_initialize_fail(self, mock_sleep, mock_mt5_initialize):
        # Test MetaTrader 5 initialization failure
        result = mt5_initialize()
        self.assertFalse(result, "MetaTrader 5 should not initialize successfully.")

    @patch('index.mt5.order_send')
    def test_place_order_failure(self, mock_order_send):
        # Mock failure response from MetaTrader 5 order send
        mock_order_send.return_value = MagicMock(retcode=mt5.TRADE_RETCODE_INVALID_PRICE)
        signal = {
            'symbol': 'GOLD',
            'action': 'SELL',
            'price': 2730,
            'tp': [2732.54, 2737.95],
            'sl': 2724,
            'id': 2
        }

        # Assert exception is raised for failed order
        with self.assertRaises(Exception):
            place_order(signal)
            logging.info("Place order failed as expected.")

if __name__ == '__main__':
    unittest.main()
