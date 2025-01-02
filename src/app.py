from flask import Flask, jsonify, render_template
import sqlite3

app = Flask(__name__, template_folder='../ui/dist', static_folder='../ui/dist/assets')
DB_FILE = 'telegram_mt5_logs.db'

# Route to fetch logs as JSON
@app.route('/logs', methods=['GET'])
def get_logs():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM logs WHERE created_at >= date("now") ORDER BY created_at DESC')')
    rows = cursor.fetchall()
    conn.close()

    # Convert rows to a list of dictionaries
    logs = [
        {
            'id': row[0],
            'channel': row[1],
            'message': row[2],
            'created_at': row[3],
            'is_valid_trade': row[4],
            'parameters': row[5],
            'processed_at': row[6],
            'failed_at': row[7],
            'exception': row[8],
            'trade_response': row[9]
        }
        for row in rows
    ]
    return jsonify(logs)

@app.route('/channels', methods=['GET'])
def get_channels():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM channels')
    rows = cursor.fetchall()
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

# Route to render HTML page
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False, port=8000)
