import json
import logging
from src.validateOrder import validateOrder
from src.sendOrder import sendOrder

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Test message with multiple take-profit values
test_message = "XAUUSD buy 2570 sl 2564 tp1 2572 tp2 2574 tp3 2576"

# Validate the message to extract order details
order_json = validateOrder(test_message)
print("Parsed order:", json.dumps(order_json, indent=2))

# Test sending multiple orders with different take-profit values
if order_json:
    for i, tp in enumerate(order_json['tp']):
        # Only shutdown after the last order
        is_last_order = i == len(order_json['tp']) - 1

        print(f"\nSending order with TP {tp} (is_last_order={is_last_order}):")
        response = sendOrder(order_json, tp, shutdown_after=is_last_order)
        print("Response:", json.dumps(response, indent=2))

        # If an order fails, don't try to send more orders
        if not response.get('success'):
            print(f"Order failed with error: {response.get('error')}")
            break
else:
    print("Failed to parse order from message")
