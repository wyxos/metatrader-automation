import requests
import json
import logging
import re

# Ollama API configuration
OLLAMA_API_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL_NAME = "llama3.2"

# Function to validate trade signal using Ollama LLM
def validate_trade_signal(message):
    # Sanitize the input message
    sanitized_message = re.sub(r'[^\x00-\x7F]+', '', message)  # Remove non-ASCII characters
    sanitized_message = sanitized_message.replace('\n', ' ')  # Replace newline characters with space

    payload = {
        "model": OLLAMA_MODEL_NAME,
        "prompt": (
            "The following is a potential trade signal message. Extract the trade information if it is valid. "
            "The fields to extract are: action (buy/sell), symbol, price (or price range), stop loss (sl), and take profit (tp). "
            "If there are multiple take profit levels, extract each one. If it is not a valid trade signal, respond with 'Invalid'. "
            f"Message: '{sanitized_message}'"
        ),
        "format": "json",
        "stream": False
    }
    try:
        response = requests.post(OLLAMA_API_URL, json=payload)
        response.raise_for_status()
        data = response.text.strip()

        # Extract the 'response' field from the API output
        try:
            response_json = json.loads(data)
            if 'response' in response_json:
                trade_data = response_json['response']
                result = json.loads(trade_data)

                # Validate the price range if present
                if 'price' in result:
                    # Check if price is a list-like string and parse it
                    if isinstance(result['price'], str) and result['price'].startswith('[') and result['price'].endswith(']'):
                        price_list = json.loads(result['price'])
                        if len(price_list) == 2:
                            start_price, end_price = price_list
                            if start_price < end_price:
                                logging.warning(f"Price range seems incorrect: start price ({start_price}) is less than end price ({end_price}).")
                                return None  # Invalidate the trade signal
                            else:
                                result['price_range'] = price_list  # Store as list for consistency
                                del result['price']
                    else:
                        if '-' in result['price']:
                            try:
                                start_price, end_price = map(float, result['price'].split('-'))
                                if start_price < end_price:
                                    logging.warning(f"Price range seems incorrect: start price ({start_price}) is less than end price ({end_price}).")
                                    return None  # Invalidate the trade signal
                                else:
                                    result['price_range'] = [start_price, end_price]
                                    del result['price']
                            except ValueError:
                                logging.error("Error parsing price range. Invalid format detected.")
                                return None  # Invalidate the trade signal

                logging.info(f"Trade signal extracted: {result}")
                return result
        except json.JSONDecodeError as e:
            logging.error(f"Error decoding JSON from Ollama API response: {e}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Error communicating with Ollama API: {e}")
    return None

# Example usage for testing
def main():
    test_message = "GOLD BUY NOW IN ZONE  2717.16-1713.16\n\n(SCALPING)\n\nTP 1 : 2719.08\nTP 2 : 2621.08\nTP 3 : OPEN\n\n\nSL :  2709.16"
    result = validate_trade_signal(test_message)
    if result:
        print("Valid trade signal:", result)
    else:
        print("Invalid trade signal or unable to parse.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
