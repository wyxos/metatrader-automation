import unittest
from unittest.mock import patch, MagicMock
import subprocess
import json
import logging

# Assume process_message_with_node is imported from index.py
from index import process_message_with_node

class TestProcessMessageWithNode(unittest.TestCase):

    @patch('subprocess.run')
    def test_process_message_with_node_success(self, mock_subprocess_run):
        # Set up the mock to return a successful result
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps({"processed": "message"})
        mock_result.stderr = ""
        mock_subprocess_run.return_value = mock_result

        message = "test message"
        result = process_message_with_node(message)

        self.assertIsNotNone(result)
        self.assertEqual(result, {"processed": "message"})
        logging.info(f"Test successful result: {result}")

    @patch('subprocess.run')
    def test_process_message_with_node_failure(self, mock_subprocess_run):
        # Set up the mock to return a failure result
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "error"
        mock_subprocess_run.return_value = mock_result

        message = "test message"
        result = process_message_with_node(message)

        self.assertIsNone(result)
        logging.info(f"Test failure result: {result}")

    @patch('subprocess.run')
    def test_process_message_with_node_invalid_json(self, mock_subprocess_run):
        # Set up the mock to return invalid JSON
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "invalid json"
        mock_result.stderr = ""
        mock_subprocess_run.return_value = mock_result

        message = "test message"
        result = process_message_with_node(message)

        self.assertIsNone(result)
        logging.info(f"Test invalid JSON result: {result}")

if __name__ == '__main__':
    unittest.main()
