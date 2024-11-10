import json
import sys
import re

def removeEmoticons(input_string):
    # Regex pattern to match emoticons commonly used in WhatsApp/Telegram
    emoticon_pattern = r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F700-\U0001F77F\U0001F780-\U0001F7FF\U0001F800-\U0001F8FF\U0001F900-\U0001F9FF\U0001FA00-\U0001FA6F\U0001FA70-\U0001FAFF\U00002700-\U000027BF\U000024C2-\U0001F251]'
    return re.sub(emoticon_pattern, '', input_string)

def cleanMessage(input_string):
    # Remove emoticons from the input string
    cleaned_string = removeEmoticons(input_string)
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
    # Convert the cleaned input string to a dictionary format
    result = {
        "input": cleaned_string
    }
    # Convert the dictionary to a JSON string
    return json.dumps(result, indent=4)

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
