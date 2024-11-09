import unittest
import json
from validate_trade_signal import validate_trade_signal

class TestProcessString(unittest.TestCase):
    def test_process_string(self):
        input_str = "Hello, this is a test string."
        expected_output = {
            "original_string": input_str,
            "word_count": 6,
            "char_count": 29
        }

        result_json = validate_trade_signal(input_str)
        result_dict = json.loads(result_json)

        self.assertEqual(result_dict, expected_output)

    def test_empty_string(self):
        input_str = ""
        expected_output = {
            "original_string": input_str,
            "word_count": 0,
            "char_count": 0
        }

        result_json = validate_trade_signal(input_str)
        result_dict = json.loads(result_json)

        self.assertEqual(result_dict, expected_output)

    def test_string_with_only_spaces(self):
        input_str = "     "
        expected_output = {
            "original_string": input_str,
            "word_count": 0,
            "char_count": 5
        }

        result_json = validate_trade_signal(input_str)
        result_dict = json.loads(result_json)

        self.assertEqual(result_dict, expected_output)

if __name__ == "__main__":
    unittest.main()
