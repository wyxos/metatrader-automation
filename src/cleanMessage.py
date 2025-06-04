import json
import sys
import re
from currencies import currencies

def removeEmoticons(input_string):
    # Regex pattern to match emoticons commonly used in WhatsApp/Telegram
    emoticon_pattern = r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F700-\U0001F77F\U0001F780-\U0001F7FF\U0001F800-\U0001F8FF\U0001F900-\U0001F9FF\U0001FA00-\U0001FA6F\U0001FA70-\U0001FAFF\U00002700-\U000027BF\U000024C2-\U0001F251]'
    return re.sub(emoticon_pattern, '', input_string)

def cleanMessage(input_string):
    # Remove non-breaking hyphens and dashes from the input string
    cleaned_string = re.sub(r"[\u2012-\u2015]+", "", input_string)

    # Remove @ signs and replace with a single space
    cleaned_string = re.sub(r'@', ' ', cleaned_string)

    # Remove emoticons from the input string
    cleaned_string = removeEmoticons(cleaned_string)

    # Convert all characters to lowercase
    cleaned_string = cleaned_string.lower()

    # Remove the word 'now' accounting for spaces
    cleaned_string = re.sub(r'\bnow\b', '', cleaned_string)

    # Remove new lines and replace with a space
    cleaned_string = re.sub(r'\n+', ' ', cleaned_string)

    # Strip leading and trailing spaces
    cleaned_string = cleaned_string.strip()

    # Replace all instances of "point :" with blank space
    cleaned_string = re.sub(r'point :', '', cleaned_string)

    # Replace common currency symbols with standard symbols
    for key, value in currencies().items():
        cleaned_string = cleaned_string.replace(key.lower(), value)

    # Replace stoploss or stop loss with sl
    cleaned_string = re.sub(r'\bstop\s*loss\b', 'sl', cleaned_string)

    # Normalize "sl :" or "sl:" to "sl"
    cleaned_string = re.sub(r'\bsl\s*:\s*', 'sl ', cleaned_string)

    # Replace instances of take profit or takeprofit with tp
    cleaned_string = re.sub(r'\btake\s*profit\b', 'tp', cleaned_string)

    # Normalize "tp :" or "tp:" to "tp"
    cleaned_string = re.sub(r'\btp\s*:\s*', 'tp ', cleaned_string)

    # Normalize sequences like "tp.575" or "tp.580"
    cleaned_string = re.sub(r'\btp\.\s*(\d+)', r'tp \1', cleaned_string)

    # Normalize patterns like "tp1 3128" to "tp 3128"
    cleaned_string = re.sub(r'\btp(\d+)\s+(?=\d)', 'tp ', cleaned_string)

    # Replace multiple spaces with a single space
    cleaned_string = re.sub(r' {2,}', ' ', cleaned_string)

    # Replace instances where "tp \d :"" as tp
    cleaned_string = re.sub(r'tp\s?(\d+)\s?:', r'tp', cleaned_string)

    # Replace instances where "tp \d\. :" with tp
    cleaned_string = re.sub(r'tp (\d+)\. :', r'tp', cleaned_string)

    return cleaned_string


def main():
    if len(sys.argv) < 2:
        # Test with a default string if no arguments are provided
#         input_string = "Sell now XAUUSD @2739.00\n\nStoploss: 2744.50\n\nTP: 2706.00\n\nJOIN @forexusfreesignals\n\nUse max 1-2% risk per trade"
#         input_string = "BTCUSD buy 92600 tp 1 92700 tp 2 92800 tp 3 92900 tp 4 94600 sl 90600 no financial advice"
#         input_string = "XAUUSD buy : 2569 - 2566 sl : 2563 tp : 2575 tp : 2580"
#         input_string = "XAUUSD buy 2679-2676 stoploss point : 2674 take profit 1 :2682 take profit 2. :2685 take profit 3. :2690"
#         input_string = "XAUUSD sell (2669.5- 2671.5) tp1: 2668 tp2: 2665.5 stop loss: 2674.5"
        input_string = "XAUUSD sell (2668.5- 2670.5) tp1: 2667 tp2: 2663 stop loss: 2673.5"
    else:
        # Join all arguments to handle strings with spaces
        input_string = ' '.join(sys.argv[1:])

    json_result = cleanMessage(input_string)
    print(json_result)

if __name__ == "__main__":
    main()
