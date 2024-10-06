import unittest
from unittest.mock import patch, MagicMock
from index import parse_signal, place_order, mt5_initialize

class TestTelegramMT5Bot(unittest.TestCase):

    def test_parse_signal_valid_message(self):
        message = "BUY NOW EURUSD 1.1234 TP 1.1300 SL 1.1200"
        expected = {
            'action': 'BUY',
            'symbol': 'EURUSD',
            'price': 1.1234,
            'tp': 1.1300,
            'sl': 1.1200
        }
        result = parse_signal(message)
        self.assertEqual(result, expected)

    def test_parse_signal_invalid_message(self):
        message = "INVALID MESSAGE"
        result = parse_signal(message)
        self.assertIsNone(result)

    @patch('index.mt5')
    def test_place_order(self, mock_mt5):
        # Mock the mt5.order_send response
        mock_result = MagicMock()
        mock_result.retcode = mock_mt5.TRADE_RETCODE_DONE
        mock_mt5.order_send.return_value = mock_result

        signal = {
            'action': 'BUY',
            'symbol': 'EURUSD',
            'price': 1.1234,
            'tp': 1.1300,
            'sl': 1.1200
        }
        place_order(signal)

        # Assert mt5.order_send was called once with expected params
        mock_mt5.order_send.assert_called_once()

    @patch('index.mt5')
    def test_mt5_initialize(self, mock_mt5):
        # Mock successful initialization and login
        mock_mt5.initialize.return_value = True
        mock_mt5.login.return_value = True

        result = mt5_initialize()
        self.assertTrue(result)
        mock_mt5.initialize.assert_called_once()
        mock_mt5.login.assert_called_once()

if __name__ == '__main__':
    unittest.main()