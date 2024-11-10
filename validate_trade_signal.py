import json
import ollama

# Assuming that cleanMessage is a valid function you have implemented in another file
from cleanMessage import cleanMessage

def validate_trade_signal(input_string):
    # Connect to Ollama to use Llama3.2 model for symbol extraction
    model = 'llama3.2'

    string = cleanMessage(input_string)

    example = """{
        "symbol": string,
        "signal": string (BUY/SELL),
        "price": float if single, or array or null if not present,
        "stopLoss": defined by SL or STOP LOSS, float if single, or array or null if not present,
        "takeProfit": defined by TP or TAKE PROFIT, float if single, or array or null if not present
    }
    """

    # Use Ollama Python library to get the response from Llama3.2
    response = ollama.generate(
        model=model,
        prompt=(
            f"Extract the following information from the trade signal provided: \n"
            f"1. Symbol: The asset being traded (e.g., GOLD). \n"
            f"2. Signal: The action to take (BUY/SELL). \n"
            f"3. Price: The price or price range mentioned. If a range is provided, return it as an array. \n"
            f"4. Stop Loss (stopLoss): Extracted from terms like SL or STOP LOSS. \n"
            f"5. Take Profit (takeProfit): Extracted from terms like TP or TAKE PROFIT. \n"
            f"Ensure that the response is a JSON object containing only the extracted attributes.\n"
            f"Price range can be separated by '-' or space and is usually after the signal or an @ sign, in such events, return an array for the price attribute.\n"
            f"Return a JSON containing the attributes extracted without any other text. Example: {example}\n"
            f"Here's the input: {string}."
        )
    )

    json.dumps(response, indent=4)

    # Create a dictionary with the results
    try:
        result = json.loads(response['response'])
    except (KeyError, json.JSONDecodeError) as e:
        return json.dumps({"error": f"Failed to parse response: {str(e)}"}, indent=4)

    # Convert the dictionary to a JSON object
    result_json = json.dumps(result, indent=4)
    return result_json

# Example usage
if __name__ == "__main__":
    input_str = """
    GOLD BUY NOW @2730-2727
    SL 2724
    TP 2732.54
    TP 2737.95
    Layering slowly use proper lot size
    """
    processed_json = validate_trade_signal(input_str)
    print(processed_json)
