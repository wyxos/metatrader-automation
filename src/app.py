from flask import Flask, jsonify, render_template, request
from fetchChannels import list_and_save_channels
import sqlite3
import asyncio
import subprocess
import os
import webbrowser
import threading
from dotenv import load_dotenv
load_dotenv()

def open_browser():
    webbrowser.open_new('http://127.0.0.1:8000')

from init_db import initialize_database
initialize_database()

is_dev = os.getenv('FRONTEND_ENV', 'prod') == 'dev'
app_debug = os.getenv('APP_DEBUG', 'false').lower() == 'true'

if is_dev:
    app = Flask(__name__)  # No static/template folders
else:
    app = Flask(__name__, template_folder='../ui/dist', static_folder='../ui/dist/assets')

DB_FILE = 'telegram_mt5_logs.db'

# Properly run the async coroutine
asyncio.run(list_and_save_channels())

# Start index.py in a subprocess
subprocess.Popen(["python", "src/index.py"])

# Route to fetch logs as JSON
@app.route('/logs', methods=['GET'])
def get_logs(db_connection=None):
    # If no connection is provided, create a new one
    if db_connection is None:
        conn = sqlite3.connect(DB_FILE)
        should_close_conn = True
    else:
        # Use the provided connection
        conn = db_connection
        should_close_conn = False

    # Get query parameters for filtering and pagination
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    start_date = request.args.get('start_date', None)
    end_date = request.args.get('end_date', None)
    channel = request.args.get('channel', None)
    status = request.args.get('status', None)
    is_valid_trade = request.args.get('is_valid_trade', None)

    # Build the query with filters
    query = '''
        SELECT l.*, c.id as channel_id, m.account_id, a.account_name
        FROM logs l
        LEFT JOIN channels c ON l.channel = c.name
        LEFT JOIN channel_account_mappings m ON c.id = m.channel_id
        LEFT JOIN mt_accounts a ON m.account_id = a.id
        WHERE 1=1
    '''
    params = []

    # Apply date range filter
    if start_date:
        query += ' AND l.created_at >= ?'
        params.append(start_date)

    if end_date:
        query += ' AND l.created_at <= ?'
        params.append(end_date)

    # Apply channel filter
    if channel:
        query += ' AND l.channel = ?'
        params.append(channel)

    # Apply status filter
    if status:
        if status == 'success':
            query += ' AND l.trade_response != "null" AND json_extract(l.trade_response, "$.success") = 1'
        elif status == 'error':
            query += ' AND l.exception IS NOT NULL'

    # Apply is_valid_trade filter
    if is_valid_trade is not None:
        query += ' AND l.is_valid_trade = ?'
        params.append(int(is_valid_trade))

    # Add ordering
    query += ' ORDER BY l.created_at DESC'

    # Get total count for pagination
    count_query = query.replace('SELECT l.*, c.id as channel_id, m.account_id, a.account_name', 'SELECT COUNT(*)')
    cursor = conn.cursor()
    cursor.execute(count_query, params)
    total_count = cursor.fetchone()[0]

    # Add pagination
    query += ' LIMIT ? OFFSET ?'
    offset = (page - 1) * per_page
    params.extend([per_page, offset])

    # Execute the query
    cursor.execute(query, params)
    rows = cursor.fetchall()

    # Close the connection only if we created it
    if should_close_conn:
        conn.close()

    # Convert rows to a list of dictionaries
    logs = []
    for row in rows:
        # The last three columns are from the joined tables (channel_id, account_id, account_name)
        account_name = row[-1] if row[-1] is not None else "default"

        logs.append({
            'id': row[0],
            'channel': row[1],
            'message': row[2],
            'parameters': row[3],
            'trade_response': row[4],
            'is_valid_trade': row[5],
            'exception': row[6],
            'created_at': row[7],
            'processed_at': row[8],
            'failed_at': row[9],
            'account_name': account_name
        })

    # Return logs with pagination metadata
    return jsonify({
        'logs': logs,
        'pagination': {
            'total': total_count,
            'page': page,
            'per_page': per_page,
            'total_pages': (total_count + per_page - 1) // per_page
        }
    })

@app.route('/channels', methods=['GET'])
def get_channels(db_connection=None):
    # If no connection is provided, create a new one
    if db_connection is None:
        conn = sqlite3.connect(DB_FILE)
        should_close_conn = True
    else:
        # Use the provided connection
        conn = db_connection
        should_close_conn = False

    # Get query parameters for filtering
    name = request.args.get('name', None)
    enabled = request.args.get('enabled', None)
    account_id = request.args.get('account_id', None)
    channel_id = request.args.get('id', None)

    # Build the base query
    query = '''
        SELECT c.id, c.telegram_id, c.name, c.enabled, m.account_id
        FROM channels c
        LEFT JOIN channel_account_mappings m ON c.id = m.channel_id
        WHERE 1=1
    '''
    params = []

    # Apply filters
    if name:
        query += ' AND c.name LIKE ?'
        params.append(f'%{name}%')

    if enabled is not None:
        query += ' AND c.enabled = ?'
        params.append(int(enabled))

    if account_id:
        query += ' AND m.account_id = ?'
        params.append(int(account_id))

    if channel_id:
        query += ' AND CAST(c.telegram_id AS TEXT) LIKE ?'
        params.append(f'%{channel_id}%')

    # Execute the query
    cursor = conn.cursor()
    cursor.execute(query, params)
    rows = cursor.fetchall()

    # Close the connection only if we created it
    if should_close_conn:
        conn.close()

    # Convert rows to a list of dictionaries
    channels = [
        {
            'id': row[0],
            'telegram_id': row[1],
            'name': row[2],
            'enabled': row[3],
            'account_id': row[4]
        }
        for row in rows
    ]
    return jsonify(channels)

@app.route('/channel', methods=['PATCH'])
# Route to enable or disable a channel by ID received in request
def update_channel(db_connection=None):
    # If no connection is provided, create a new one
    if db_connection is None:
        conn = sqlite3.connect(DB_FILE)
        should_close_conn = True
    else:
        # Use the provided connection
        conn = db_connection
        should_close_conn = False

    cursor = conn.cursor()
    cursor.execute('UPDATE channels SET enabled = NOT enabled WHERE id = ?', (request.json['id'],))
    conn.commit()

    # Close the connection only if we created it
    if should_close_conn:
        conn.close()
    return jsonify({'message': 'Channel updated successfully'})

@app.route('/channels', methods=['PATCH'])
def bulk_update_channels(db_connection=None):
    data = request.json
    ids = data['ids']
    enabled = data['enabled']

    # If no connection is provided, create a new one
    if db_connection is None:
        conn = sqlite3.connect(DB_FILE)
        should_close_conn = True
    else:
        # Use the provided connection
        conn = db_connection
        should_close_conn = False

    cursor = conn.cursor()
    cursor.execute(
        f"UPDATE channels SET enabled = ? WHERE id IN ({','.join(['?']*len(ids))})",
        [enabled, *ids]
    )
    conn.commit()

    # Close the connection only if we created it
    if should_close_conn:
        conn.close()
    return jsonify({'message': 'Channels updated successfully'})

# Routes for MetaTrader accounts
@app.route('/accounts', methods=['GET'])
def get_accounts(db_connection=None):
    # If no connection is provided, create a new one
    if db_connection is None:
        conn = sqlite3.connect(DB_FILE)
        should_close_conn = True
    else:
        # Use the provided connection
        conn = db_connection
        should_close_conn = False

    cursor = conn.cursor()
    cursor.execute('SELECT * FROM mt_accounts')
    rows = cursor.fetchall()

    # Close the connection only if we created it
    if should_close_conn:
        conn.close()

    # Convert rows to a list of dictionaries
    accounts = [
        {
            'id': row[0],
            'account_name': row[1],
            'server_name': row[2],
            'login_id': row[3],
            'password': row[4],
            'created_at': row[5]
        }
        for row in rows
    ]
    return jsonify(accounts)

@app.route('/accounts', methods=['POST'])
def create_account(db_connection=None):
    data = request.json

    # If no connection is provided, create a new one
    if db_connection is None:
        conn = sqlite3.connect(DB_FILE)
        should_close_conn = True
    else:
        # Use the provided connection
        conn = db_connection
        should_close_conn = False

    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO mt_accounts (account_name, server_name, login_id, password) VALUES (?, ?, ?, ?)',
        (data['account_name'], data['server_name'], data['login_id'], data['password'])
    )
    conn.commit()

    # Get the ID of the newly created account
    account_id = cursor.lastrowid

    # Close the connection only if we created it
    if should_close_conn:
        conn.close()

    return jsonify({'id': account_id, 'message': 'Account created successfully'})

@app.route('/accounts/<int:account_id>', methods=['PUT'])
def update_account(account_id, db_connection=None):
    data = request.json

    # If no connection is provided, create a new one
    if db_connection is None:
        conn = sqlite3.connect(DB_FILE)
        should_close_conn = True
    else:
        # Use the provided connection
        conn = db_connection
        should_close_conn = False

    cursor = conn.cursor()
    cursor.execute(
        'UPDATE mt_accounts SET account_name = ?, server_name = ?, login_id = ?, password = ? WHERE id = ?',
        (data['account_name'], data['server_name'], data['login_id'], data['password'], account_id)
    )
    conn.commit()

    # Close the connection only if we created it
    if should_close_conn:
        conn.close()

    return jsonify({'message': 'Account updated successfully'})

@app.route('/accounts/<int:account_id>', methods=['DELETE'])
def delete_account(account_id, db_connection=None):
    # If no connection is provided, create a new one
    if db_connection is None:
        conn = sqlite3.connect(DB_FILE)
        should_close_conn = True
    else:
        # Use the provided connection
        conn = db_connection
        should_close_conn = False

    cursor = conn.cursor()
    cursor.execute('DELETE FROM mt_accounts WHERE id = ?', (account_id,))
    conn.commit()

    # Close the connection only if we created it
    if should_close_conn:
        conn.close()

    return jsonify({'message': 'Account deleted successfully'})

# Routes for channel-to-account mappings
@app.route('/channel-mappings', methods=['GET'])
def get_channel_mappings(db_connection=None):
    # If no connection is provided, create a new one
    if db_connection is None:
        conn = sqlite3.connect(DB_FILE)
        should_close_conn = True
    else:
        # Use the provided connection
        conn = db_connection
        should_close_conn = False

    cursor = conn.cursor()
    cursor.execute('''
        SELECT cm.id, c.id as channel_id, c.name as channel_name, a.id as account_id, a.account_name
        FROM channel_account_mappings cm
        JOIN channels c ON cm.channel_id = c.id
        JOIN mt_accounts a ON cm.account_id = a.id
    ''')
    rows = cursor.fetchall()

    # Close the connection only if we created it
    if should_close_conn:
        conn.close()

    # Convert rows to a list of dictionaries
    mappings = [
        {
            'id': row[0],
            'channel_id': row[1],
            'channel_name': row[2],
            'account_id': row[3],
            'account_name': row[4]
        }
        for row in rows
    ]
    return jsonify(mappings)

@app.route('/channel-mappings', methods=['POST'])
def create_channel_mapping(db_connection=None):
    data = request.json

    # If no connection is provided, create a new one
    if db_connection is None:
        conn = sqlite3.connect(DB_FILE)
        should_close_conn = True
    else:
        # Use the provided connection
        conn = db_connection
        should_close_conn = False

    cursor = conn.cursor()

    # Check if a mapping already exists for this channel
    cursor.execute('SELECT id FROM channel_account_mappings WHERE channel_id = ?', (data['channel_id'],))
    existing_mapping = cursor.fetchone()

    if existing_mapping:
        # Update existing mapping
        cursor.execute(
            'UPDATE channel_account_mappings SET account_id = ? WHERE channel_id = ?',
            (data['account_id'], data['channel_id'])
        )
    else:
        # Create new mapping
        cursor.execute(
            'INSERT INTO channel_account_mappings (channel_id, account_id) VALUES (?, ?)',
            (data['channel_id'], data['account_id'])
        )

    conn.commit()

    # Get the ID of the newly created or updated mapping
    if existing_mapping:
        mapping_id = existing_mapping[0]
    else:
        mapping_id = cursor.lastrowid

    # Close the connection only if we created it
    if should_close_conn:
        conn.close()

    return jsonify({'id': mapping_id, 'message': 'Channel mapping created/updated successfully'})

@app.route('/channel-mappings/<int:mapping_id>', methods=['DELETE'])
def delete_channel_mapping(mapping_id, db_connection=None):
    # If no connection is provided, create a new one
    if db_connection is None:
        conn = sqlite3.connect(DB_FILE)
        should_close_conn = True
    else:
        # Use the provided connection
        conn = db_connection
        should_close_conn = False

    cursor = conn.cursor()
    cursor.execute('DELETE FROM channel_account_mappings WHERE id = ?', (mapping_id,))
    conn.commit()

    # Close the connection only if we created it
    if should_close_conn:
        conn.close()

    return jsonify({'message': 'Channel mapping deleted successfully'})

# Route to render HTML page
@app.route('/')
def index():
    if is_dev:
        return '''
        <!doctype html>
        <html lang="en">
        <head>
            <meta charset="UTF-8" />
            <meta name="viewport" content="width=device-width, initial-scale=1.0" />
            <title>Telegram MT5 App</title>
            <link
              rel="stylesheet"
              href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css"
            />
        </head>
        <body>
            <div id="app"></div>
            <script type="module" src="http://localhost:5173/src/main.js"></script>
        </body>
        </html>
        '''
    else:
        return render_template('index.html')

if __name__ == '__main__':
    os.system('cls' if os.name == 'nt' else 'clear')

    # Launch browser after short delay
    threading.Timer(1.5, open_browser).start()

    app.run(debug=app_debug, use_reloader=False, port=8000)
