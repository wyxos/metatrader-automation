import sqlite3
import time
import json
import logging
from cleanMessage import cleanMessage
from validateOrder import validateOrder
from sendOrder import sendOrder


def process_message(message, channel):
    # Database file
    db_file = 'telegram_mt5_logs.db'

    # Connect to the SQLite database
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Ensure message is not empty
    if not message:
        logging.info('No message found.')
        conn.close()
        return

    # Clean the message
    message = cleanMessage(message)
    logging.info(f"Processing message: {message}")

    # Initialize variables
    created_at = time.strftime('%Y-%m-%d %H:%M:%S')
    parameters = None
    trade_response = None
    exception = None
    is_valid_trade = 0
    processed_at = None
    failed_at = None

    try:
        # Validate the message to extract order details
        orderJson = validateOrder(message)

        # If orderJson is valid, set parameters to its string representation
        if orderJson:
            parameters = json.dumps(orderJson)

        # Check for missing fields in the order
        if not orderJson.get('signal') or not orderJson.get('symbol') or not orderJson.get('price') or not orderJson.get('tp') or not orderJson.get('sl'):
            logging.error("Invalid order format.")
            exception = "Invalid order format."
            failed_at = time.strftime('%Y-%m-%d %H:%M:%S')
        else:
            is_valid_trade = 1
            # Iterate through each take-profit (tp) value and send an order
            for tp in orderJson['tp']:
                orderJson['tp'] = tp
                trade_response = sendOrder(orderJson, tp)
                if not trade_response['success']:
                    failed_at = time.strftime('%Y-%m-%d %H:%M:%S')
                else:
                    processed_at = time.strftime('%Y-%m-%d %H:%M:%S')

    except Exception as e:
        logging.error(f"Error validating order: {e}")
        exception = str(e)
        failed_at = time.strftime('%Y-%m-%d %H:%M:%S')

    try:
        # Insert the log into the database
        cursor.execute('''
            INSERT INTO logs (channel, message, parameters, trade_response, exception, is_valid_trade, processed_at, failed_at, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (channel, message, parameters, json.dumps(trade_response), exception, is_valid_trade, processed_at, failed_at, created_at))
        conn.commit()
        record_id = cursor.lastrowid

        logging.info(f"Record inserted with ID: {record_id}")
    except Exception as e:
        logging.error(f"Error inserting log into database: {e}")
        conn.rollback()  # Rollback if something goes wrong

    # Close the database connection
    conn.close()


if __name__ == "__main__":
    # Example usage
    messages = [
        "XAUUSD buy 2570 - 2567 sl: 2564 tp: 2572 tp: 2574 tp: 2576 tp: open",
        "XAUUSD sell 2571 tp 2569 tp 2568 tp 2567 tp 2556 sl 2586",
        "GBPCAD sell 1.78050 sl 1.78450 tp.77400",
        "NZDUSD sell 0.58740 sl 0.58900 tp.58600 tp.58450",
        "XAUUSD buy : 2569 - 2566 sl : 2563 tp : 2575 tp : 2580"
    ]

    for msg in messages:
        process_message(msg)
