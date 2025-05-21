import sqlite3
import time
import json
import logging
from cleanMessage import cleanMessage
from validateOrder import validateOrder
from sendOrder import sendOrder


def process_message(message, channel, db_connection=None):
    # If no connection is provided, create a new one
    if db_connection is None:
        # Database file
        db_file = 'telegram_mt5_logs.db'

        # Connect to the SQLite database
        conn = sqlite3.connect(db_file)
        should_close_conn = True
    else:
        # Use the provided connection
        conn = db_connection
        should_close_conn = False

    cursor = conn.cursor()

    # Get account information for this channel
    account_info = None
    all_accounts = []
    try:
        # First get the channel ID - try case-insensitive match
        logging.info(f"Looking for channel with name: {channel}")
        cursor.execute('SELECT id FROM channels WHERE LOWER(name) = LOWER(?)', (channel,))
        channel_row = cursor.fetchone()

        # If not found, try a more flexible match
        if not channel_row:
            logging.info(f"Exact match not found, trying flexible match for: {channel}")
            cursor.execute('SELECT id FROM channels WHERE LOWER(name) LIKE LOWER(?)', (f'%{channel}%',))
            channel_row = cursor.fetchone()
            if channel_row:
                logging.info(f"Found channel with flexible match: {channel_row[0]}")
            else:
                logging.warning(f"No channel found for: {channel} even with flexible match")

        if channel_row:
            channel_id = channel_row[0]

            # Then get the account ID mapped to this channel
            logging.info(f"Found channel ID: {channel_id}, looking for account mapping")
            cursor.execute('''
                SELECT a.* FROM mt_accounts a
                JOIN channel_account_mappings m ON a.id = m.account_id
                WHERE m.channel_id = ?
            ''', (channel_id,))

            account_row = cursor.fetchone()

            if account_row:
                account_info = {
                    'id': account_row[0],
                    'account_name': account_row[1],
                    'server_name': account_row[2],
                    'login_id': account_row[3],
                    'password': account_row[4]
                }
                logging.info(f"Using account {account_info['account_name']} (ID: {account_info['id']}) for channel {channel}")
            else:
                # Check if there's a mapping in the database
                cursor.execute('SELECT COUNT(*) FROM channel_account_mappings WHERE channel_id = ?', (channel_id,))
                mapping_count = cursor.fetchone()[0]
                if mapping_count > 0:
                    logging.warning(f"Found mapping for channel {channel} (ID: {channel_id}) but couldn't retrieve account info")
                else:
                    logging.warning(f"No account mapped for channel {channel} (ID: {channel_id})")
                # Fetch all accounts for potential use if this is a valid trade
                cursor.execute('SELECT * FROM mt_accounts')
                account_rows = cursor.fetchall()
                for row in account_rows:
                    all_accounts.append({
                        'id': row[0],
                        'account_name': row[1],
                        'server_name': row[2],
                        'login_id': row[3],
                        'password': row[4]
                    })
                logging.info(f"Found {len(all_accounts)} accounts to use if this is a valid trade")
        else:
            logging.warning(f"Channel {channel} not found in database")
            # Fetch all accounts for potential use if this is a valid trade
            cursor.execute('SELECT * FROM mt_accounts')
            account_rows = cursor.fetchall()
            for row in account_rows:
                all_accounts.append({
                    'id': row[0],
                    'account_name': row[1],
                    'server_name': row[2],
                    'login_id': row[3],
                    'password': row[4]
                })
            logging.info(f"Found {len(all_accounts)} accounts to use if this is a valid trade")
    except Exception as e:
        logging.error(f"Error fetching account info: {e}")
        # Continue without account info if there's an error

    # Ensure message is not empty
    if not message:
        logging.info('No message found.')
        if should_close_conn:
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
            # Make a copy of the original tp values
            original_tp_values = orderJson['tp'].copy()

            # If no account is mapped and it's a valid trade, send to all accounts
            if not account_info and all_accounts and is_valid_trade:
                logging.info(f"Sending valid trade to all {len(all_accounts)} accounts")

                # For each account
                for account in all_accounts:
                    logging.info(f"Sending to account: {account['account_name']}")

                    # Iterate through each take-profit (tp) value and send an order
                    for i, tp in enumerate(original_tp_values):
                        # Set the current tp value
                        orderJson['tp'] = tp

                        # Only shutdown after the last order of the last account
                        is_last_order = (i == len(original_tp_values) - 1) and (account == all_accounts[-1])

                        # Send the order
                        account_trade_response = sendOrder(orderJson, tp, account, shutdown_after=is_last_order)

                        # Log the response for this account
                        try:
                            # Insert the log into the database for this account
                            cursor.execute('''
                                INSERT INTO logs (channel, message, parameters, trade_response, exception, is_valid_trade, processed_at, failed_at, created_at)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                            ''', (channel, message, parameters, json.dumps(account_trade_response), None if account_trade_response.get('success') else "Failed",
                                  is_valid_trade,
                                  time.strftime('%Y-%m-%d %H:%M:%S') if account_trade_response.get('success') else None,
                                  time.strftime('%Y-%m-%d %H:%M:%S') if not account_trade_response.get('success') else None,
                                  created_at))
                            conn.commit()
                        except Exception as e:
                            logging.error(f"Error inserting log for account {account['account_name']}: {e}")

                # Set trade_response to the last response (just for the main log entry)
                trade_response = {"success": True, "message": f"Sent to {len(all_accounts)} accounts"}
                processed_at = time.strftime('%Y-%m-%d %H:%M:%S')
            else:
                # Regular case - send to the mapped account or default
                # Iterate through each take-profit (tp) value and send an order
                for i, tp in enumerate(original_tp_values):
                    # Set the current tp value
                    orderJson['tp'] = tp

                    # Only shutdown after the last order
                    is_last_order = i == len(original_tp_values) - 1

                    # Send the order
                    trade_response = sendOrder(orderJson, tp, account_info, shutdown_after=is_last_order)
                    if trade_response.get('success'):
                        # success is present and truthy
                        processed_at = time.strftime('%Y-%m-%d %H:%M:%S')
                    else:
                        # either not present, or falsy
                        failed_at = time.strftime('%Y-%m-%d %H:%M:%S')
                        # If an order fails, don't try to send more orders
                        break

    except Exception as e:
        logging.error(f"Error validating order: {e}")
        exception = str(e)
        failed_at = time.strftime('%Y-%m-%d %H:%M:%S')

    try:
        # If we sent to all accounts, don't insert a duplicate main log entry
        if not (not account_info and all_accounts and is_valid_trade):
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

    # Close the database connection only if we created it
    if should_close_conn:
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
