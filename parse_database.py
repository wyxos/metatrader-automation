import sqlite3
import json
import logging
import time
from validate_trade_signal import validate_trade_signal

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def process_database_records():
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect('telegram_mt5_logs.db')
        cursor = conn.cursor()

        # Select all records from the logs table
        cursor.execute("SELECT id, message FROM logs")
        records = cursor.fetchall()

        # Check if records exist
        if not records:
            logging.info("No records found in the logs table.")
            return

        # Iterate through each record and process the message column
        for record in records:
            record_id, message = record
            logging.info(f"Processing record ID: {record_id}")

            try:
                parameters = validate_trade_signal(message)
                # parameters is expected to be a JSON string
                parameters_dict = json.loads(parameters)

                if isinstance(parameters_dict, dict) and "error" not in parameters_dict:
                    is_valid_trade = 1
                else:
                    is_valid_trade = 0
                    logging.warning(f"Failed to extract valid parameters for record ID {record_id}: {parameters_dict.get('error', 'Unknown error')}" )
                    parameters = None  # Set parameters to None if there is an error

                logging.info(f"Extracted parameters for record ID {record_id}: {parameters}")

                # Update the parameters and is_valid_trade columns in the logs table
                cursor.execute(
                    "UPDATE logs SET parameters = ?, is_valid_trade = ? WHERE id = ?",
                    (parameters, is_valid_trade, record_id)
                )
            except json.JSONDecodeError:
                logging.error(f"Invalid JSON format for record ID {record_id}: {parameters}")
                # Set is_valid_trade to 0 if JSON is invalid
                cursor.execute(
                    "UPDATE logs SET is_valid_trade = ?, parameters = ? WHERE id = ?",
                    (0, None, record_id)
                )
            except Exception as e:
                logging.error(f"Error processing record ID {record_id}: {e}")
                # Set is_valid_trade to 0 if processing failed
                cursor.execute(
                    "UPDATE logs SET is_valid_trade = ?, parameters = ? WHERE id = ?",
                    (0, None, record_id)
                )

        # Commit changes and close the connection
        conn.commit()
        logging.info("Finished processing all records.")
    except sqlite3.Error as e:
        logging.error(f"Database error: {e}")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
    finally:
        if conn:
            conn.close()
            logging.info("Database connection closed.")

if __name__ == "__main__":
    while True:
        try:
            process_database_records()
        except Exception as e:
            logging.er
