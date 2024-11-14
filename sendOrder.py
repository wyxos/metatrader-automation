import json
import MetaTrader5 as mt5

def sendOrder(order_json):
    # Parse the JSON string to a Python dictionary
    order_data = json.loads(order_json)

    # Extract attributes
    price = order_data["price"]
    signal = order_data["signal"].lower()  # "buy" or "sell"
    symbol = order_data["symbol"]
    tp = order_data["tp"]
    sl = order_data["sl"]

    # Initialize MetaTrader 5
    if not mt5.initialize():
        print("Failed to initialize MetaTrader 5, error code:", mt5.last_error())
        return False

    # Ensure AutoTrading is enabled
    account_info = mt5.account_info()
    if account_info is None:
        print("Failed to retrieve account information, error code:", mt5.last_error())
        mt5.shutdown()
        return False
    elif not account_info.trade_allowed:
        print("AutoTrading is disabled by client. Please enable AutoTrading in MetaTrader 5.")
        mt5.shutdown()
        return False

    # Define order type
    if signal == "buy":
        order_type = mt5.ORDER_TYPE_BUY
    elif signal == "sell":
        order_type = mt5.ORDER_TYPE_SELL
    else:
        print("Invalid signal. Use 'buy' or 'sell'.")
        mt5.shutdown()
        return False

    # Ensure the symbol is available for trading
    if not mt5.symbol_select(symbol, True):
        print(f"Failed to select symbol {symbol}. Please check the symbol name.")
        mt5.shutdown()
        return False

    # Get current symbol price details
    symbol_info_tick = mt5.symbol_info_tick(symbol)
    if symbol_info_tick is None:
        print(f"Failed to get tick information for symbol {symbol}.")
        mt5.shutdown()
        return False

    # Define order parameters
    order_request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": 1.0,  # Set the volume to 1.0 lot (customize as needed)
        "type": order_type,
        "price": symbol_info_tick.ask if signal == "buy" else symbol_info_tick.bid,
        "sl": sl,
        "tp": tp,
        "deviation": 10,  # Allowable deviation in points
        "magic": 234000,  # Magic number to identify the order
        "comment": "Order sent from Python script",
        "type_time": mt5.ORDER_TIME_GTC,  # Good till cancelled
        "type_filling": mt5.ORDER_FILLING_IOC,  # Immediate or cancel
    }

    # Send the order
    result = mt5.order_send(order_request)

    # Check the result of the request
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"Failed to send order: {result.retcode}")
        print("Error details:", result)
        mt5.shutdown()
        return False
    else:
        print(f"Order successfully placed. Ticket: {result.order}")
        mt5.shutdown()
        return True

# Example usage:
if __name__ == "__main__":
    order_json = '{"price": 1.2345, "signal": "buy", "symbol": "EURUSD", "tp": 1.2400, "sl": 1.00}'
    send_order(order_json)
