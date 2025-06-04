import sqlite3
import json
from validateOrder import validateOrder

def main():
    # Connect to the SQLite database
    db_path = 'telegram_mt5_logs.db'
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    try:
        # Fetch all rows from the 'logs' table
        cursor.execute("SELECT rowid, message FROM logs")
        rows = cursor.fetchall()

        for row in rows:
            rowid, message = row

            try:
                # Validate and parse each message
                order_data = validateOrder(message)
                order_data_json = json.dumps(order_data)

                # If successful, update the columns is_valid_trade and parameters
                cursor.execute(
                    "UPDATE logs SET is_valid_trade = ?, parameters = ? WHERE rowid = ?",
                    (1, order_data_json, rowid)
                )
                print(f"Successfully processed row {rowid}")

            except Exception as e:
                # If an exception occurs, update the exception column
                cursor.execute(
                    "UPDATE logs SET exception = ? WHERE rowid = ?",
                    (str(e), rowid)
                )
                print(f"Failed to process row {rowid}: {e}")

        # Commit all changes to the database
        connection.commit()

    except Exception as e:
        print(f"An error occurred while accessing the database: {e}")

    finally:
        # Close the database connection
        connection.close()

if __name__ == "__main__":
    main()
