import unittest
import json
from validate_trade_signal import validate_trade_signal

class TestProcessString(unittest.TestCase):
    def test_process_string(self):
        input_str = "Hello, this is a test string."
        expected_output = {
            "symbol": ""
        }

        result_json = validate_trade_signal(input_str)
        result_dict = json.loads(result_json)

        self.assertEqual(result_dict, expected_output)

    def test_trade_signal_gold(self):
        input_str = "GOLD BUY NOW @2730-2727\n\nSL 2724\n\nTP 2732.54\nTP 2737.95\n\nLayering slowly use proper lot size"
        expected_output = {
            "symbol": "GOLD"
        }

        result_json = validate_trade_signal(input_str)
        result_dict = json.loads(result_json)

        self.assertEqual(result_dict, expected_output)

    def test_trade_signal_gbpjpy(self):
        input_str = "GBPJPY BUY @197.250\n\nSL  196.500\n\nTP 198.100"
        expected_output = {
            "symbol": "GBPJPY"
        }

        result_json = validate_trade_signal(input_str)
        result_dict = json.loads(result_json)

        self.assertEqual(result_dict, expected_output)

if __name__ == "__main__":
    unittest.main()
