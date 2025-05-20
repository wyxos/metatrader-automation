import pytest
from unittest.mock import patch, MagicMock
import json
import os
import sys
from flask import Flask

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

# Import the app module
from app import app as flask_app

# Test cases for app.py
@pytest.fixture
def client():
    """Create a test client for the Flask app"""
    flask_app.config['TESTING'] = True
    with flask_app.test_client() as client:
        yield client

class TestApp:

    def test_index_route(self, client, monkeypatch):
        """Test the index route returns the correct HTML"""
        # Mock the is_dev variable to be False
        monkeypatch.setattr('app.is_dev', False)

        # Make a request to the index route
        response = client.get('/')

        # Check that the response is successful
        assert response.status_code == 200

        # Check that the response contains expected HTML elements
        assert b'<!DOCTYPE html>' in response.data
        assert b'<div id="app"></div>' in response.data

    def test_index_route_dev_mode(self, client, monkeypatch):
        """Test the index route in dev mode"""
        # Mock the is_dev variable to be True
        monkeypatch.setattr('app.is_dev', True)

        # Make a request to the index route
        response = client.get('/')

        # Check that the response is successful
        assert response.status_code == 200

        # Check that the response contains expected HTML elements for dev mode
        assert b'<!DOCTYPE html>' in response.data
        assert b'<script type="module" src="http://localhost:5174/src/main.js"></script>' in response.data

    def test_get_logs_route(self, client, mock_db):
        """Test the /logs route returns the correct JSON data"""
        # Insert test data into the mock database
        mock_db["cursor"].execute('''
            INSERT INTO logs (channel, message, parameters, trade_response, is_valid_trade, exception, created_at, processed_at, failed_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', ("Test Channel", "Test Message", '{"signal":"buy"}', '{"success":true}', 1, None, "2025-01-01 12:00:00", "2025-01-01 12:00:01", None))
        mock_db["conn"].commit()

        # Make a request to the logs route
        response = client.get('/logs')

        # Check that the response is successful
        assert response.status_code == 200

        # Parse the JSON response
        data = json.loads(response.data)

        # Check that the response contains the expected data
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]['channel'] == "Test Channel"
        assert data[0]['message'] == "Test Message"
        assert data[0]['is_valid_trade'] == 1
        assert data[0]['created_at'] == "2025-01-01 12:00:00"

    def test_get_channels_route(self, client, mock_db):
        """Test the /channels route returns the correct JSON data"""
        # Insert test data into the mock database
        mock_db["cursor"].execute('''
            INSERT INTO channels (telegram_id, name, enabled)
            VALUES (?, ?, ?)
        ''', (-1001234567890, "Test Channel", 1))
        mock_db["conn"].commit()

        # Make a request to the channels route
        response = client.get('/channels')

        # Check that the response is successful
        assert response.status_code == 200

        # Parse the JSON response
        data = json.loads(response.data)

        # Check that the response contains the expected data
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]['telegram_id'] == -1001234567890
        assert data[0]['name'] == "Test Channel"
        assert data[0]['enabled'] == 1

    def test_update_channel_route(self, client, mock_db):
        """Test the /channel PATCH route updates the channel correctly"""
        # Insert test data into the mock database
        mock_db["cursor"].execute('''
            INSERT INTO channels (telegram_id, name, enabled)
            VALUES (?, ?, ?)
        ''', (-1001234567890, "Test Channel", 1))
        mock_db["conn"].commit()

        # Get the ID of the inserted channel
        mock_db["cursor"].execute("SELECT id FROM channels WHERE telegram_id = ?", (-1001234567890,))
        channel_id = mock_db["cursor"].fetchone()[0]

        # Make a PATCH request to update the channel
        response = client.patch('/channel', json={'id': channel_id})

        # Check that the response is successful
        assert response.status_code == 200

        # Parse the JSON response
        data = json.loads(response.data)

        # Check that the response contains the expected message
        assert data['message'] == "Channel updated successfully"

        # Verify that the channel was updated in the database
        mock_db["cursor"].execute("SELECT enabled FROM channels WHERE id = ?", (channel_id,))
        enabled = mock_db["cursor"].fetchone()[0]
        assert enabled == 0  # Should be toggled from 1 to 0

    def test_bulk_update_channels_route(self, client, mock_db):
        """Test the /channels PATCH route updates multiple channels correctly"""
        # Insert test data into the mock database
        mock_db["cursor"].execute('''
            INSERT INTO channels (telegram_id, name, enabled)
            VALUES (?, ?, ?)
        ''', (-1001234567890, "Test Channel 1", 1))
        mock_db["cursor"].execute('''
            INSERT INTO channels (telegram_id, name, enabled)
            VALUES (?, ?, ?)
        ''', (-1001234567891, "Test Channel 2", 1))
        mock_db["conn"].commit()

        # Get the IDs of the inserted channels
        mock_db["cursor"].execute("SELECT id FROM channels")
        channel_ids = [row[0] for row in mock_db["cursor"].fetchall()]

        # Make a PATCH request to update the channels
        response = client.patch('/channels', json={'ids': channel_ids, 'enabled': 0})

        # Check that the response is successful
        assert response.status_code == 200

        # Parse the JSON response
        data = json.loads(response.data)

        # Check that the response contains the expected message
        assert data['message'] == "Channels updated successfully"

        # Verify that the channels were updated in the database
        mock_db["cursor"].execute("SELECT enabled FROM channels WHERE id IN ({})".format(','.join(['?'] * len(channel_ids))), channel_ids)
        enabled_values = [row[0] for row in mock_db["cursor"].fetchall()]
        assert all(enabled == 0 for enabled in enabled_values)

    @patch('app.asyncio.run')
    @patch('app.subprocess.Popen')
    def test_app_initialization(self, mock_popen, mock_asyncio_run, monkeypatch):
        """Test that the app initializes correctly"""
        # Mock the initialization functions
        mock_asyncio_run.return_value = None
        mock_popen.return_value = None

        # Mock the initialize_database function
        monkeypatch.setattr('app.initialize_database', lambda: None)

        # Import the app module again to trigger initialization
        import importlib
        importlib.reload(__import__('app'))

        # Verify that the initialization functions were called
        mock_asyncio_run.assert_called_once()
        mock_popen.assert_called_once_with(["python", "src/index.py"])
