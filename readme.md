# A.U.T.O. - Automated Uptake of Telegram Orders

A Python application that integrates Telegram with MetaTrader 5 for automated trading based on signals received from Telegram channels.

## Features

- **Telegram Integration**: Monitor Telegram channels for trading signals
- **Signal Parsing**: Automatically parse and validate trading signals in various formats
- **MetaTrader 5 Integration**: Send orders directly to MetaTrader 5
- **Multi-Account Support**: Send trades to multiple MetaTrader accounts simultaneously
- **Web Interface**: Monitor and configure the system through a user-friendly web interface
- **Channel Management**: Enable/disable channels, filter by various criteria
- **Account Management**: Add, edit, and delete MetaTrader accounts
- **Channel-Account Mapping**: Map specific Telegram channels to specific MetaTrader accounts
- **Detailed Logging**: Track all signals, trades, and responses
- **Error Handling**: Robust error handling and reporting

## Requirements

- Python 3.8+
- MetaTrader 5
- Telegram account
- Node.js and npm (for UI development)

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/metatrader-telegram.git
cd metatrader-telegram
```

2. Install Python dependencies:

```bash
pip install -r requirements.txt
```

3. Install UI dependencies (optional, for development):

```bash
cd ui
npm install
```

4. Create a `.env` file with your credentials (see `.env.example` for reference):

```bash
cp .env.example .env
```

Then edit the `.env` file with your actual credentials.

## Configuration

The application uses environment variables for configuration. Key variables include:

### Telegram Configuration

- `TELEGRAM_API_ID`: Your Telegram API ID
- `TELEGRAM_API_HASH`: Your Telegram API Hash
- `TELEGRAM_SESSION_STRING`: Your Telegram session string

To obtain API credentials from Telegram:

1. Go to [https://my.telegram.org/auth](https://my.telegram.org/auth)
2. Log in with your phone number
3. Go to "API development tools"
4. Create a new application
5. Copy the API ID and API Hash to your `.env` file

### MetaTrader 5 Configuration

- `MT5_PATH`: Path to your MetaTrader 5 terminal executable (e.g., `C:/Program Files/MetaTrader 5/terminal64.exe`)

### Application Configuration

- `FRONTEND_ENV`: Set to `dev` for development mode, `prod` for production
- `APP_DEBUG`: Set to `true` to enable debug mode, `false` to disable

## Usage

1. Start the application:

```bash
python src/app.py
```

2. Open your web browser and navigate to `http://localhost:8000`

3. The web interface has three main tabs:
   - **Logs**: View all trading signals and their outcomes
   - **Channels**: Configure which Telegram channels to monitor
   - **Accounts**: Manage your MetaTrader 5 accounts

4. To set up a new channel:
   - Go to the Channels tab
   - The application will automatically detect available channels
   - Enable the channels you want to monitor
   - Optionally, map each channel to a specific MetaTrader account

5. To set up a new MetaTrader account:
   - Go to the Accounts tab
   - Click "Add Account"
   - Enter the account details (name, server, login ID, password)
   - Click "Save"

6. The application will automatically process trading signals from the enabled channels and send orders to the configured MetaTrader accounts.

## Project Structure

- `src/`: Source code
  - `app.py`: Main application (Flask web server)
  - `index.py`: Telegram client for monitoring channels
  - `processMessage.py`: Process messages from Telegram
  - `validateOrder.py`: Validate and parse trading signals
  - `sendOrder.py`: Send orders to MetaTrader 5
  - `cleanMessage.py`: Clean and format messages
  - `currencies.py`: Currency symbols and mappings
  - `init_db.py`: Database initialization
  - `fetchChannels.py`: Fetch available Telegram channels
- `tests/`: Test files
  - `conftest.py`: Common test fixtures
  - `test_*.py`: Test files for each module
- `ui/`: User interface files
  - `src/`: Vue.js source files
  - `dist/`: Compiled UI files (production)
- `logs/`: Log files

## Testing

This project includes a comprehensive test suite. To run the tests:

```bash
# Install test dependencies
pip install -r requirements-test.txt

# Run all tests
pytest

# Run tests with coverage report
pytest --cov=src
```

## Troubleshooting

### MetaTrader 5 Connection Issues

If you encounter "Initialization failed" errors:

1. Ensure the `MT5_PATH` in your `.env` file is correct
2. Make sure MetaTrader 5 is installed and can be launched manually
3. Check that your account credentials are correct
4. Ensure AutoTrading is enabled in MetaTrader 5

### Telegram Connection Issues

If you have issues connecting to Telegram:

1. Verify your API credentials in the `.env` file
2. Ensure your Telegram session is valid
3. Check your internet connection

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
