import json

def validate_trade_signal(input_string):
    # Example processing: count the number of words and characters
    word_count = len(input_string.split())
    char_count = len(input_string)

    # Create a dictionary with the results
    result = {
        "original_string": input_string,
        "word_count": word_count,
        "char_count": char_count
    }

    # Convert the dictionary to a JSON object
    result_json = json.dumps(result, indent=4)
    return result_json

# Example usage
if __name__ == "__main__":
    input_str = "Hello, this is a sample string to be processed."
    processed_json = process_string(input_str)
    print(processed_json)
