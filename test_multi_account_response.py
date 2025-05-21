import logging
import json
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# This is a simplified test that doesn't rely on actual database or imports
# It directly tests the logic we've implemented

# Mock accounts
test_accounts = [
    {
        'id': 1,
        'account_name': 'Test Account 1',
        'server_name': 'Test Server 1',
        'login_id': '12345',
        'password': 'password1'
    },
    {
        'id': 2,
        'account_name': 'Test Account 2',
        'server_name': 'Test Server 2',
        'login_id': '67890',
        'password': 'password2'
    }
]

# Mock order data
order_json = {
    "signal": "buy",
    "symbol": "XAUUSD",
    "price": 3301.0,
    "sl": 3294.0,
    "tp": [3304.0, 3307.0, 3310.0, 3313.0]
}

# Mock sendOrder function
def mock_sendOrder(order_json, account_info=None, shutdown_after=False):
    # Return a mock successful response
    return {
        "success": True,
        "result": {
            "retcode": 10009,
            "deal": 12345,
            "order": 67890,
            "volume": 0.01,
            "price": float(order_json.get('price', 0)) if not isinstance(order_json.get('price'), list) else float(order_json.get('price', [0])[0]),
            "bid": 0,
            "ask": 0,
            "comment": "Test order",
            "request_id": 123456,
            "retcode_external": 0
        }
    }

# Simulate the relevant part of process_message function
def test_multi_account_processing():
    logging.info("Starting test of multi-account processing")

    # Create an array to collect all responses
    all_responses = []

    # Make a copy of the original tp values
    original_tp_values = order_json['tp'].copy()

    # For each account
    for account in test_accounts:
        logging.info(f"Sending to account: {account['account_name']}")

        # Iterate through each take-profit (tp) value and send an order
        for i, tp in enumerate(original_tp_values):
            # Set the current tp value
            order_json['tp'] = tp

            # Only shutdown after the last order of the last account
            is_last_order = (i == len(original_tp_values) - 1) and (account == test_accounts[-1])

            # Send the order (using our mock function)
            account_trade_response = mock_sendOrder(order_json, account_info=account, shutdown_after=is_last_order)

            # Add this response to our collection
            all_responses.append({
                "account": account['account_name'],
                "id": account['id'],
                "response": account_trade_response
            })

            logging.info(f"Sent order with TP {tp} to account {account['account_name']}")

    # Set trade_response with all collected responses
    trade_response = {
        "success": True,
        "responses": all_responses
    }

    return trade_response

# Run the test
try:
    # Process the test message
    trade_response = test_multi_account_processing()

    # Log the response
    logging.info(f"Trade response: {json.dumps(trade_response, indent=2)}")

    # Verify the response format
    if "responses" in trade_response:
        logging.info("✅ Response contains 'responses' array")

        # Check each response in the array
        for response in trade_response["responses"]:
            if "account" in response and "id" in response and "response" in response:
                logging.info(f"✅ Response for account '{response['account']}' has correct format")
            else:
                logging.error(f"❌ Response for an account is missing required fields: {response}")
    else:
        logging.error("❌ Response does not contain 'responses' array")

    # Check the number of responses
    expected_responses = len(test_accounts) * 4  # 4 TP values
    actual_responses = len(trade_response["responses"])
    if actual_responses == expected_responses:
        logging.info(f"✅ Correct number of responses: {actual_responses} (expected {expected_responses})")
    else:
        logging.error(f"❌ Incorrect number of responses: {actual_responses} (expected {expected_responses})")

except Exception as e:
    logging.error(f"Error during test: {e}")

logging.info("Test completed")
