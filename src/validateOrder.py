import re
import json
from currencies import currencies
from cleanMessage import cleanMessage

def validateOrder(message):
    # Clean the message first
    message = cleanMessage(message)
    currenciesList = currencies()

    # Extract the symbol
    symbol = None
    for key, value in currenciesList.items():
        if value.lower() in message.lower():
            symbol = value
            message = re.sub(r'\b' + re.escape(value) + r'\b', '', message, flags=re.IGNORECASE).strip()
            break

    # Extract signal (buy/sell)
    signal_match = re.search(r'\b(buy|sell)\b', message, re.IGNORECASE)
    signal = signal_match.group().lower() if signal_match else None
    if signal:
        message = re.sub(r'\b(buy|sell)\b', '', message, flags=re.IGNORECASE).strip()

    # Extract Stop Loss (SL)
    sl_match = re.search(r'\bsl:? ?(\d+\.?\d*)', message, re.IGNORECASE)
    sl = float(sl_match.group(1)) if sl_match else None
    if sl:
        message = re.sub(r'\bsl:? ?\d+\.?\d*', '', message, flags=re.IGNORECASE).strip()

    # Extract Take Profit (TP)
    tp_matches = re.findall(r'\btp ?(\d+\.?\d*)', message, re.IGNORECASE)
    tps = [float(tp) for tp in tp_matches] if tp_matches else []
    if tp_matches:
        message = re.sub(r'\btp ?\d+\.?\d*', '', message, flags=re.IGNORECASE).strip()

    # Extract price or range
    price = None
    range_match = re.search(r'(\d+\.?\d*) ?- ?(\d+\.?\d*)', message)
    if range_match:
        price = (float(range_match.group(1)), float(range_match.group(2)))
    else:
        price_match = re.search(r'\d+\.?\d*', message)
        price = float(price_match.group()) if price_match else None

    # Clean up remaining message
    message = re.sub(r'\d+\.?\d*', '', message).strip()
    message = re.sub(r'\s+', ' ', message)  # Normalize spaces

    # Create a dictionary with extracted details
    order_data = {
        "signal": signal,
        "symbol": symbol,
        "price": price,
        "sl": sl,
        "tp": tps
    }

    return order_data

# Example usage
if __name__ == "__main__":
    messages = [
        "XAUUSD buy 2570 - 2567 sl: 2564 tp: 2572 tp: 2574 tp: 2576 tp: open",
        "XAUUSD sell 2571 tp 2569 tp 2568 tp 2567 tp 2556 sl 2586",
        "GBPCAD sell 1.78050 sl 1.78450 tp.77400",
        "NZDUSD sell 0.58740 sl 0.58900 tp.58600 tp.58450",
        "XAUUSD buy : 2569 - 2566 sl : 2563 tp : 2575 tp : 2580"
    ]

    for msg in messages:
        result = validateOrder(msg)
        print(json.dumps(result, indent=2))
