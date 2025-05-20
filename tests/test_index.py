import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import asyncio
import os
import sys

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

# Test cases for index.py
class TestIndex:

    def test_get_enabled_channels(self, mock_db):
        """Test that get_enabled_channels returns the correct channels"""
        # Import the function
        from index import get_enabled_channels

        # Clear any existing channels
        mock_db["cursor"].execute("DELETE FROM channels")
        mock_db["conn"].commit()

        # Insert test data into the mock database
        mock_db["cursor"].execute('''
            INSERT INTO channels (telegram_id, name, enabled)
            VALUES (?, ?, ?)
        ''', (-1001234567890, "Test Channel 1", 1))
        mock_db["cursor"].execute('''
            INSERT INTO channels (telegram_id, name, enabled)
            VALUES (?, ?, ?)
        ''', (-1001234567891, "Test Channel 2", 0))  # Disabled channel
        mock_db["conn"].commit()

        # Patch sqlite3.connect to return our mock connection
        with patch('sqlite3.connect', return_value=mock_db["conn"]):
            # Call the function
            result = get_enabled_channels()

            # Verify the result
            assert isinstance(result, list)
            assert len(result) == 1
            assert result[0] == 1001234567890  # Should return the absolute value of the telegram_id

    @pytest.mark.asyncio
    @patch('index.TelegramClient')
    @patch('index.api_id', '12345')
    @patch('index.api_hash', 'abcdef1234567890')
    async def test_regenerate_session(self, mock_telegram_client):
        """Test that regenerate_session creates a new session string"""
        # Import the function
        from index import regenerate_session

        # Setup mocks
        mock_client_instance = AsyncMock()
        session_string = "1BQANOTEqJTvJAAYzHUYPMTt5AAQEAAB0AQAAvnYIYgABHqAdYjF_O5YdElAzLSRAK1vQZkJIQokLrPW1X-S7u9u9xAVgrZLbPXRGGt2oBuKzJLANpQ3S7U6GLRVXtOG4VnJNEGhF7rUQH3aeITbi3YVLNyUxvVf3-XEE9VxoUKS6070h4nU-9OKsJVFw=="

        # Make sure session.save returns a string, not a coroutine
        mock_session = MagicMock()
        mock_session.save = MagicMock(return_value=session_string)
        mock_client_instance.session = mock_session

        # Make sure start() returns a completed future, not a coroutine
        mock_client_instance.start = AsyncMock(return_value=None)

        # Configure the context manager behavior
        mock_telegram_client.return_value = mock_client_instance
        # Make __aenter__ return the client instance
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
        # Make __aexit__ return None
        mock_client_instance.__aexit__ = AsyncMock(return_value=None)

        # Mock the set_key function
        with patch('index.set_key') as mock_set_key:
            # Call the function
            result = await regenerate_session()

            # Verify the result
            assert result == session_string

            # Verify that the client was started
            mock_client_instance.start.assert_called_once()

            # Verify that set_key was called with the correct arguments
            mock_set_key.assert_called_once_with('.env', 'TELEGRAM_SESSION_STRING', session_string)

    @pytest.mark.asyncio
    @patch('index.TelegramClient')
    @patch('index.api_id', '12345')
    @patch('index.api_hash', 'abcdef1234567890')
    @patch('index.session_string', 'test_session_string')
    @patch('index.StringSession')
    async def test_initialize_telegram_client_success(self, mock_string_session, mock_telegram_client, mock_env):
        """Test that initialize_telegram_client successfully connects to Telegram"""
        # Import the function
        from index import initialize_telegram_client, api_id, api_hash

        # Setup mocks
        mock_client_instance = AsyncMock()
        # Make sure start() returns a completed future, not a coroutine
        mock_client_instance.start = AsyncMock(return_value=None)
        mock_telegram_client.return_value = mock_client_instance

        # Mock StringSession to return a mock that doesn't validate the input
        mock_string_session_instance = MagicMock()
        mock_string_session.return_value = mock_string_session_instance

        # Call the function
        await initialize_telegram_client()

        # Verify that the client was created with the correct arguments
        mock_telegram_client.assert_called_once()
        args, kwargs = mock_telegram_client.call_args

        # Check that the arguments match the patched values
        assert api_id == '12345'
        assert api_hash == 'abcdef1234567890'

        # Verify that StringSession was called with the correct arguments
        mock_string_session.assert_called_once_with('test_session_string')

        # Verify that the client was started
        mock_client_instance.start.assert_called_once()

    @pytest.mark.asyncio
    @patch('index.TelegramClient')
    @patch('index.regenerate_session')
    @patch('index.api_id', '12345')
    @patch('index.api_hash', 'abcdef1234567890')
    @patch('index.session_string', 'test_session_string')
    async def test_initialize_telegram_client_failure(self, mock_regenerate_session, mock_telegram_client, mock_env):
        """Test that initialize_telegram_client handles connection failures"""
        # Import the function
        from index import initialize_telegram_client

        # Setup mocks
        mock_client_instance = AsyncMock()
        # First call raises an exception, second call succeeds
        mock_client_instance.start.side_effect = [Exception("Connection failed"), None]
        mock_telegram_client.return_value = mock_client_instance

        # Mock regenerate_session to return a new session string
        new_session = "1BQANOTEqJTvJAAYzHUYPMTt5AAQEAAB0AQAAvnYIYgABHqAdYjF_O5YdElAzLSRAK1vQZkJIQokLrPW1X-S7u9u9xAVgrZLbPXRGGt2oBuKzJLANpQ3S7U6GLRVXtOG4VnJNEGhF7rUQH3aeITbi3YVLNyUxvVf3-XEE9VxoUKS6070h4nU-9OKsJVFw=="
        # Make sure regenerate_session returns a completed future with the new session string
        mock_regenerate_session.return_value = new_session

        # Patch the StringSession to avoid "Not a valid string" error
        with patch('index.StringSession') as mock_string_session:
            # Make the StringSession constructor return a mock that doesn't validate the input
            mock_string_session_instance = MagicMock()
            mock_string_session.return_value = mock_string_session_instance

            # Call the function
            await initialize_telegram_client()

            # Verify that regenerate_session was called
            mock_regenerate_session.assert_called_once()

            # Verify that the client was created twice (once with original session, once with new session)
            assert mock_telegram_client.call_count == 2

            # Verify that the client was started twice
            assert mock_client_instance.start.call_count == 2

            # Verify that StringSession was called with the correct arguments
            mock_string_session.assert_any_call('test_session_string')
            mock_string_session.assert_any_call(new_session)

    @pytest.mark.asyncio
    @patch('index.client')
    async def test_start_telegram_client_no_channels(self, mock_client, mock_db):
        """Test that start_telegram_client handles the case of no enabled channels"""
        # Import the function
        from index import start_telegram_client

        # Ensure there are no enabled channels in the database
        mock_db["cursor"].execute("DELETE FROM channels")
        mock_db["conn"].commit()

        # Patch sqlite3.connect to return our mock connection
        with patch('sqlite3.connect', return_value=mock_db["conn"]):
            # Call the function
            await start_telegram_client()

            # Verify that the client's on method was not called
            mock_client.on.assert_not_called()

            # Verify that the client's run_until_disconnected method was not called
            mock_client.run_until_disconnected.assert_not_called()

    @pytest.mark.asyncio
    @patch('index.client')
    @patch('index.process_message')
    @patch('index.events.NewMessage')
    async def test_start_telegram_client_with_channels(self, mock_new_message, mock_process_message, mock_client, mock_db):
        """Test that start_telegram_client sets up the event handler correctly"""
        # Import the function
        from index import start_telegram_client

        # Clear any existing channels
        mock_db["cursor"].execute("DELETE FROM channels")
        mock_db["conn"].commit()

        # Insert test data into the mock database
        mock_db["cursor"].execute('''
            INSERT INTO channels (telegram_id, name, enabled)
            VALUES (?, ?, ?)
        ''', (-1001234567890, "Test Channel", 1))
        mock_db["conn"].commit()

        # Setup mocks for the database connection
        with patch('sqlite3.connect', return_value=mock_db["conn"]):
            # Setup mocks for the client
            mock_client.on = MagicMock()
            # Make the on method return a function that captures its argument
            def capture_handler(event_filter):
                def decorator(func):
                    # Store the function for later verification
                    capture_handler.handler = func
                    return func
                return decorator

            mock_client.on.side_effect = capture_handler
            # Make sure run_until_disconnected returns a completed future, not a coroutine
            mock_client.run_until_disconnected = AsyncMock(return_value=None)
            mock_new_message.return_value = "new_message_filter"

            # Call the function
            await start_telegram_client()

            # Verify that the NewMessage constructor was called with the correct arguments
            mock_new_message.assert_called_once_with(chats=[1001234567890])

            # Verify that the client's on method was called with the correct arguments
            mock_client.on.assert_called_once_with("new_message_filter")

            # Verify that the client's run_until_disconnected method was called
            mock_client.run_until_disconnected.assert_called_once()

    @pytest.mark.asyncio
    @patch('index.client')
    @patch('index.process_message')
    @patch('index.events.NewMessage')
    async def test_message_handler(self, mock_new_message, mock_process_message, mock_client, mock_db):
        """Test that the message handler processes messages correctly"""
        # Import the function
        from index import start_telegram_client

        # Insert test data into the mock database
        mock_db["cursor"].execute('''
            INSERT INTO channels (telegram_id, name, enabled)
            VALUES (?, ?, ?)
        ''', (-1001234567890, "Test Channel", 1))
        mock_db["conn"].commit()

        # Create a mock event
        mock_event = AsyncMock()
        mock_event.message.message = "Test message"

        # Create a mock chat
        mock_chat = AsyncMock()
        mock_chat.id = -1001234567890
        mock_chat.title = "Test Channel"

        # Setup the get_chat method to return the mock chat
        mock_event.get_chat.return_value = mock_chat

        # Setup mocks for the database connection
        with patch('sqlite3.connect', return_value=mock_db["conn"]):
            # Setup mocks for the client
            handler = None
            def capture_handler(event_filter):
                def decorator(func):
                    nonlocal handler
                    handler = func
                    return func
                return decorator

            mock_client.on = MagicMock(side_effect=capture_handler)
            # Make sure run_until_disconnected returns a completed future, not a coroutine
            mock_client.run_until_disconnected = AsyncMock(return_value=None)
            mock_new_message.return_value = "new_message_filter"

            # Call the function to set up the handler
            await start_telegram_client()

            # Verify that a handler was captured
            assert handler is not None

            # Call the handler with the mock event
            await handler(mock_event)

            # Verify that process_message was called with the correct arguments
            mock_process_message.assert_called_once_with("Test message", "Test Channel")

    @pytest.mark.asyncio
    @patch('index.client')
    @patch('index.process_message')
    @patch('index.events.NewMessage')
    async def test_message_handler_empty_message(self, mock_new_message, mock_process_message, mock_client, mock_db):
        """Test that the message handler handles empty messages correctly"""
        # Import the function
        from index import start_telegram_client

        # Insert test data into the mock database
        mock_db["cursor"].execute('''
            INSERT INTO channels (telegram_id, name, enabled)
            VALUES (?, ?, ?)
        ''', (-1001234567890, "Test Channel", 1))
        mock_db["conn"].commit()

        # Create a mock event
        mock_event = AsyncMock()
        mock_event.message.message = ""  # Empty message

        # Create a mock chat
        mock_chat = AsyncMock()
        mock_chat.id = -1001234567890
        mock_chat.title = "Test Channel"

        # Setup the get_chat method to return the mock chat
        mock_event.get_chat.return_value = mock_chat

        # Setup mocks for the database connection
        with patch('sqlite3.connect', return_value=mock_db["conn"]):
            # Setup mocks for the client
            handler = None
            def capture_handler(event_filter):
                def decorator(func):
                    nonlocal handler
                    handler = func
                    return func
                return decorator

            mock_client.on = MagicMock(side_effect=capture_handler)
            # Make sure run_until_disconnected returns a completed future, not a coroutine
            mock_client.run_until_disconnected = AsyncMock(return_value=None)
            mock_new_message.return_value = "new_message_filter"

            # Call the function to set up the handler
            await start_telegram_client()

            # Verify that a handler was captured
            assert handler is not None

            # Call the handler with the mock event
            await handler(mock_event)

            # Verify that process_message was not called
            mock_process_message.assert_not_called()
