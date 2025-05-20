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

    cursor = conn.cursor()
    cursor.execute('SELECT * FROM logs WHERE created_at >= date("now") ORDER BY created_at DESC')
#     cursor.execute('SELECT * FROM logs ORDER BY created_at DESC')
    rows = cursor.fetchall()

    # Close the connection only if we created it
    if should_close_conn:
        conn.close()

    # Convert rows to a list of dictionaries
    logs = [
        {
            'id': row[0],
            'channel': row[1],
            'message': row[2],
            'parameters': row[3],
            'trade_response': row[4],
            'is_valid_trade': row[5],
            'exception': row[6],
            'created_at': row[7],
            'processed_at': row[8],
            'failed_at': row[9]
        }
        for row in rows
    ]
    return jsonify(logs)

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

    cursor = conn.cursor()
    cursor.execute('SELECT * FROM channels')
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
            'enabled': row[3]
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

# Route to render HTML page
@app.route('/')
def index():
    if is_dev:
        return '''
        <!DOCTYPE html>
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
            <script type="module" src="http://localhost:5174/src/main.js"></script>
        </body>
        </html>
        '''
    else:
        return render_template('index.html')

if __name__ == '__main__':
    os.system('cls' if os.name == 'nt' else 'clear')

    # Launch browser after short delay
    threading.Timer(1.5, open_browser).start()

    app.run(debug=True, use_reloader=False, port=8000)
