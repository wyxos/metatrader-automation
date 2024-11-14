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
    # Replace double spaces with a single space
    cleaned_string = re.sub(r' {2,}', ' ', cleaned_string)
    # Strip leading and trailing spaces
    cleaned_string = cleaned_string.strip()

    # Replace common currency symbols with standard symbols
    for key, value in currencies().items():
        cleaned_string = cleaned_string.replace(key.lower(), value)

    # Sometimes 'tp' is written as 'take profit', replace it with 'tp'
    cleaned_string = re.sub(r'\btake profit\b', 'tp', cleaned_string)

    # Sometimes 'sl' is written as 'stop loss', replace it with 'sl'
    cleaned_string = re.sub(r'\bstop loss\b', 'sl', cleaned_string)

    # Sometimes tp are supplied with multiple tp 1 xxxx tp 2 xxxx tp 3 xxxx, replace the tp and the number with just tp
    cleaned_string = re.sub(r'\btp \d\b', 'tp', cleaned_string)

    # Sometimes it's written as tp1, tp2, tp3
    cleaned_string = re.sub(r'\btp\d\b', 'tp', cleaned_string)

    # Convert the dictionary to a JSON string
    return cleaned_string

def main():
    if len(sys.argv) < 2:
        # Test with a default string if no arguments are provided
        input_string = "Sell now XAUUSD @2739.00\n\nStoploss: 2744.50\n\nTP: 2706.00\n\nJOIN @forexusfreesignals\n\nUse max 1-2% risk per trade"
    else:
        # Join all arguments to handle strings with spaces
        input_string = ' '.join(sys.argv[1:])

    json_result = cleanMessage(input_string)
    print(json_result)

if __name__ == "__main__":
    main()
