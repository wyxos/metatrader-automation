import json
import logging
from src.validateOrder import validateOrder
from src.sendOrder import sendOrder

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Test message with multiple take-profit values
test_message = "XAUUSD buy 3301 sl 3294 tp1 3304 tp2 3307 tp3 3310 tp4 3313"

# Sample account info for testing
test_account_info = {
    'id': 1,
    'account_name': 'Test Account',
    'server_name': 'Test Server',
    'login_id': '12345',
    'password': 'password123'
}

# Validate the message to extract order details
order_json = validateOrder(test_message)
print("Parsed order:", json.dumps(order_json, indent=2))

# Test sending multiple orders with different take-profit values
if order_json:
    # Make a copy of the original tp values
    original_tp_values = order_json['tp'].copy()

    for i, tp in enumerate(original_tp_values):
        # Only shutdown after the last order
        is_last_order = i == len(original_tp_values) - 1

        print(f"\nSending order with TP {tp} (is_last_order={is_last_order}):")

        # Set the current tp value
        order_json['tp'] = tp

        # Send the order with account info
        response = sendOrder(order_json, tp, account_info=test_account_info, shutdown_after=is_last_order)
        print("Response:", json.dumps(response, indent=2))

        # If an order fails, don't try to send more orders
        if not response.get('success'):
            print(f"Order failed with error: {response.get('error')}")
            break
else:
    print("Failed to parse order from message")
