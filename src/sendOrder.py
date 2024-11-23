import json
import MetaTrader5 as mt5
import logging
from validateOrder import validateOrder

def sendOrder(order_json, tp):
    # Parse the JSON string to a Python dictionary
    order_data = order_json

    # Extract attributes
    price = order_data["price"]
    signal = order_data["signal"].lower()  # "buy" or "sell"
    symbol = order_data["symbol"]
    tp = tp
    sl = order_data["sl"]

    # Initialize MetaTrader 5
    if not mt5.initialize():
        print("Failed to initialize MetaTrader 5, error code:", mt5.last_error())
        return {"success": False, "error": "Initialization failed"}

    # Ensure AutoTrading is enabled
    account_info = mt5.account_info()
    if account_info is None:
        print("Failed to retrieve account information, error code:", mt5.last_error())
        mt5.shutdown()
        return {"success": False, "error": "Account information retrieval failed"}
    elif not account_info.trade_allowed:
        print("AutoTrading is disabled by client. Please enable AutoTrading in MetaTrader 5.")
        mt5.shutdown()
        return {"success": False, "error": "AutoTrading is disabled"}

    # Define order type
    if signal == "buy":
        order_type = mt5.ORDER_TYPE_BUY
    elif signal == "sell":
        order_type = mt5.ORDER_TYPE_SELL
    else:
        print("Invalid signal. Use 'buy' or 'sell'.")
        mt5.shutdown()
        return {"success": False, "error": "Invalid signal"}

    # Ensure the symbol is available for trading
    if not mt5.symbol_select(symbol, True):
        print(f"Failed to select symbol {symbol}. Please check the symbol name.")
        mt5.shutdown()
        return {"success": False, "error": f"Symbol {symbol} not available"}

    # Get current symbol price details
    symbol_info_tick = mt5.symbol_info_tick(symbol)
    if symbol_info_tick is None:
        print(f"Failed to get tick information for symbol {symbol}.")
        mt5.shutdown()
        return {"success": False, "error": f"Tick information for symbol {symbol} unavailable"}

    # Define order parameters
    order_request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": 0.01,  # Set the volume to 1.0 lot (customize as needed)
        "type": order_type,
        "price": symbol_info_tick.ask if signal == "buy" else symbol_info_tick.bid,
#         "price": 2638,
        "sl": sl,
        "tp": tp,
        "deviation": 10,  # Allowable deviation in points
        "magic": 234000,  # Magic number to identify the order
        "comment": "Order sent from Python script",
        "type_time": mt5.ORDER_TIME_GTC,  # Good till cancelled
        "type_filling": mt5.ORDER_FILLING_IOC,  # Immediate or cancel
    }

    logging.info(f"Sending order request: {order_request}")

    # Send the order
    result = mt5.order_send(order_request)

    if result is None:
        print("Failed to send order: no response received")
        mt5.shutdown()
        return {"success": False, "error": "No response received from MetaTrader"}

    # Check the result of the request
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"Failed to send order: {result.retcode} with {result.comment}")
        mt5.shutdown()
        return {
            "success": False,
            "error": f"Order failed with retcode {result.retcode}",
            "details": result._asdict()  # Return result details as a dictionary
        }
    else:
        print(f"Order successfully placed. Ticket: {result.order}")
        mt5.shutdown()
        return {
            "success": True,
            "result": result._asdict()  # Return result details as a dictionary
        }

# Example usage:
if __name__ == "__main__":
#     order_json = {"price": 1.2345, "signal": "buy", "symbol": "EURUSD", "tp": [1.2400], "sl": 1.00}
#     order_json = validateOrder("EURUSD buy 1.2345 sl 1.00 tp 1.2400")
#     order_json = {"price": 43210, "signal": "sell", "symbol": "DJ30", "tp": [43180], "sl": 43250}
#     order_json = validateOrder("XAUUSD buy 2535.30 sl 2629.30 tp 2640.30 tp 2645.30")
    order_json = validateOrder("XAUUSD buy market price sl 2670.0 tp 2690.30")
#     order_json = { "price": 2535.30, "signal": "buy", "symbol": "AUDJPY", "tp": [2640.30, 2645.30], "sl": 2629.30 }
#     order_json = validateOrder("BTCUSD buy 92600 tp 1 92700 tp 2 92800 tp 3 92900 tp 4 94600 sl 90600 no financial advice")

    response = sendOrder(order_json, order_json["tp"][0])

    print(json.dumps(response, indent=2))
