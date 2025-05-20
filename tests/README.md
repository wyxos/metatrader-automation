# Testing Documentation for MetaTrader-Telegram Integration

This document provides information on how to run tests for the MetaTrader-Telegram integration project.

## Test Structure

The tests are organized as follows:

- `tests/conftest.py`: Contains common fixtures used across multiple test files
- `tests/test_validateOrder.py`: Tests for the order validation functionality
- `tests/test_sendOrder.py`: Tests for sending orders to MetaTrader 5
- `tests/test_processMessage.py`: Tests for processing messages from Telegram
- `tests/test_app.py`: Tests for the Flask web application
- `tests/test_index.py`: Tests for the Telegram client functionality

## Setup

1. Install the test dependencies:

```bash
pip install -r requirements-test.txt
```

2. Ensure you have a `.env` file with the necessary configuration (see `.env.example` for reference)

## Running Tests

To run all tests:

```bash
pytest
```

To run tests with coverage report:

```bash
pytest --cov=src
```

To run a specific test file:

```bash
pytest tests/test_validateOrder.py
```

To run tests excluding slow or integration tests:

```bash
pytest -m "not slow"
pytest -m "not integration"
```

## Mocking Strategy

The tests use mocking to avoid making actual API calls or database operations:

1. **MetaTrader 5**: The MetaTrader 5 API is mocked to avoid making actual trades
2. **Telegram**: The Telegram client is mocked to avoid making actual API calls
3. **SQLite**: An in-memory SQLite database is used for testing
4. **Environment Variables**: Environment variables are mocked to avoid using actual credentials

## Test Coverage

The tests aim to cover:

1. **Happy Path**: Testing the normal flow of the application
2. **Error Handling**: Testing how the application handles errors
3. **Edge Cases**: Testing unusual inputs or scenarios

## Adding New Tests

When adding new functionality to the project, please follow these guidelines for testing:

1. Create a new test file if necessary, following the naming convention `test_*.py`
2. Use the existing fixtures in `conftest.py` where possible
3. Mock external dependencies to avoid making actual API calls
4. Test both success and failure scenarios
5. Add appropriate assertions to verify the behavior
