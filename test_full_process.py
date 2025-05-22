import json
import sys
import os

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from validateOrder import validateOrder
from processMessage import process_message

# The message from the issue description
message = "XAUUSD buy 3309 tp 1 3311 tp 2 3312 tp 3 3313 tp 4 3330 sl 3290 no financial advice"

# Parse the message using validateOrder
result = validateOrder(message)
print("Result from validateOrder:")
print(json.dumps(result, indent=2))

# Expected tp values: [3311, 3312, 3313, 3330]
print("\nExpected tp values: [3311, 3312, 3313, 3330]")
print("Actual tp values:", result["tp"])

# Now let's simulate the process_message function
print("\nSimulating process_message function...")
# We'll create a mock database connection
import sqlite3
conn = sqlite3.connect(':memory:')
cursor = conn.cursor()

# Create the logs table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        channel TEXT,
        message TEXT,
        parameters TEXT,
        trade_response TEXT,
        is_valid_trade INTEGER DEFAULT 0,
        exception TEXT,
        created_at TEXT,
        processed_at TEXT,
        failed_at TEXT
    )
''')

# Create the channels table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS channels (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id INTEGER,
        name TEXT,
        enabled INTEGER DEFAULT 1
    )
''')

# Insert a test channel
cursor.execute('''
    INSERT INTO channels (telegram_id, name, enabled)
    VALUES (-1001234567890, 'Test Channel', 1)
''')

conn.commit()

# Process the message
process_message(message, "Test Channel", conn)

# Check what was stored in the database
cursor.execute("SELECT * FROM logs")
logs = cursor.fetchall()

print("\nLogs in the database:")
for log in logs:
    print(log)

# Parse the parameters from the log
if logs:
    parameters = json.loads(logs[0][3])
    print("\nParameters stored in the database:")
    print(json.dumps(parameters, indent=2))
    print("\nTP values stored in the database:", parameters["tp"])
