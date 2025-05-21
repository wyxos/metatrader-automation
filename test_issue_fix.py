import json
import logging
import sys
import os

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from validateOrder import validateOrder
from sendOrder import sendOrder

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Test message from the issue description
test_message = "XAUUSD buy 3308 - 3305 sl 3302 tp 3313 (50pips) tp 3318 (100pips) manage your risk and reward"

# Sample account info for testing
test_account_info = {
    'id': 1,
    'account_name': 'Capstock-Server',
    'server_name': 'Capstock-Server',
    'login_id': '301100',
    'password': '$Jason2024'
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
        response = sendOrder(order_json, account_info=test_account_info, shutdown_after=is_last_order)
        print("Response:", json.dumps(response, indent=2))

        # If an order fails, don't try to send more orders
        if not response.get('success'):
            print(f"Order failed with error: {response.get('error')}")
            break
else:
    print("Failed to parse order from message")
