import re
import json
from currencies import currencies
from cleanMessage import cleanMessage

def validateOrder(message):
    message = cleanMessage(message)

    currenciesList = currencies()

    print('validating message:', message)

    symbol = None

    # loop through the currencies dictionary and replace the keys with their values
    for key, value in currenciesList.items():
        # check if value is in the message, if so, set symbol to that value and break the loop
        if value.lower() in message.lower():
            symbol = value
            # Remove the symbol from the message, accounting for possible extra spaces
            message = re.sub(r'\b' + re.escape(value) + r'\b', '', message, flags=re.IGNORECASE).strip()
            message = re.sub(r'\s+', ' ', message)  # Remove extra spaces left behind
            break

    # match the word SL until the next word character
    sl_match = re.search(r'\bsl\b\s*\d+\.\d+', message, re.IGNORECASE)
    # extract the float value from the match
    sl = sl_match.group().split()[-1] if sl_match else None

    # remove sl match from the message
    message = re.sub(r'\bsl\b\s*\d+\.\d+', '', message, flags=re.IGNORECASE).strip()
    message = re.sub(r'\s+', ' ', message)  # Remove extra spaces left behind

    print('sl:', sl)

    # check how many tp values are in the message
    tp_matches = re.findall(r'\btp\b\s*\d+\.\d+', message, re.IGNORECASE)

    # for each tp match, extract the float value
    tp = [tp_match.split()[-1] for tp_match in tp_matches]

    # remove tp matches from the message
    message = re.sub(r'\btp\b\s*\d+\.\d+', '', message, flags=re.IGNORECASE).strip()
    message = re.sub(r'\s+', ' ', message)  # Remove extra spaces left behind

    print('tp:', tp)

    # extract the signal from the message
    signal = re.search(r'\b(?:buy|sell)\b', message, re.IGNORECASE)

    # if signal is found, extract the signal value
    signal = signal.group() if signal else None

    # remove the signal from the message
    message = re.sub(r'\b(?:buy|sell)\b', '', message, flags=re.IGNORECASE).strip()
    message = re.sub(r'\s+', ' ', message)  # Remove extra spaces left behind

    # find the first floating pattern in the message
    price_match = re.search(r'\d+\.\d+', message)
    # extract the float value from the match
    price = price_match.group() if price_match else None

    # remove the price from the message
    message = re.sub(r'\d+\.\d+', '', message).strip()
    message = re.sub(r'\s+', ' ', message)  # Remove extra spaces left behind

    # log the message
    print('Symbol:',   symbol)
    print('Remaining message:', message)

    # Create a dictionary with the extracted order details
    order_data = {
        "signal": signal,
        "symbol": symbol,
        "price": price,
        "sl": sl,
        "tp": tp
    }

    # Convert the dictionary to a JSON string
    order_json = json.dumps(order_data)

    return order_json

# Example usage
if __name__ == "__main__":
    message = "BUY DJ30 @ 1.2345 SL 1.2000 TP 1 1.2500 TP 2 1.2100"
    result = validateOrder(message)
    print(result)
