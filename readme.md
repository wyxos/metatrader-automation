# MetaTrader-Telegram Integration

A Python application that integrates Telegram with MetaTrader 5 for automated trading based on signals received from Telegram channels.

## Features

- Monitor Telegram channels for trading signals
- Parse and validate trading signals
- Send orders to MetaTrader 5
- Web interface for monitoring and configuration
- Logging of trades and signals

## Requirements

- Python 3.8+
- MetaTrader 5
- Telegram account
- Flask (for web interface)

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/metatrader-telegram.git
cd metatrader-telegram
```

2. Install the dependencies:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file with your credentials (see `.env.example` for reference):

```bash
cp .env.example .env
```

Then edit the `.env` file with your actual credentials.

## Usage

1. Start the application:

```bash
python src/app.py
```

2. Open your web browser and navigate to `http://localhost:8000`

3. Configure the Telegram channels you want to monitor

4. The application will automatically process trading signals from the enabled channels

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
- `logs/`: Log files

## Testing

This project includes a comprehensive test suite. See [tests/README.md](tests/README.md) for detailed testing instructions.

To run the tests:

```bash
# Install test dependencies
pip install -r requirements-test.txt

# Run all tests
pytest

# Run tests with coverage report
pytest --cov=src
```

## Configuration

The application uses environment variables for configuration. See `.env.example` for the required variables.

### Telegram Configuration

You need to obtain API credentials from Telegram:

1. Go to [https://my.telegram.org/auth](https://my.telegram.org/auth)
2. Log in with your phone number
3. Go to "API development tools"
4. Create a new application
5. Copy the API ID and API Hash to your `.env` file

### MetaTrader 5 Configuration

You need to provide your MetaTrader 5 account credentials:

1. Open MetaTrader 5
2. Go to Account -> Account Details
3. Copy your account number, password, and server to your `.env` file

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
