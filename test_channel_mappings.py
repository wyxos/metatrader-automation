import sqlite3
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Connect to the database
conn = sqlite3.connect('telegram_mt5_logs.db')
cursor = conn.cursor()

# Get all channels
cursor.execute('SELECT id, telegram_id, name FROM channels')
channels = cursor.fetchall()

logging.info(f"Found {len(channels)} channels in the database")

# Get all channel-account mappings
cursor.execute('''
    SELECT m.id, m.channel_id, c.name as channel_name, m.account_id, a.account_name
    FROM channel_account_mappings m
    JOIN channels c ON m.channel_id = c.id
    JOIN mt_accounts a ON m.account_id = a.id
''')
mappings = cursor.fetchall()

logging.info(f"Found {len(mappings)} channel-account mappings in the database")

# Check which channels have mappings
mapped_channel_ids = [mapping[1] for mapping in mappings]
unmapped_channels = [channel for channel in channels if channel[0] not in mapped_channel_ids]

if unmapped_channels:
    logging.warning(f"Found {len(unmapped_channels)} channels without account mappings:")
    for channel in unmapped_channels:
        logging.warning(f"  - Channel ID: {channel[0]}, Name: {channel[2]}")
else:
    logging.info("All channels have account mappings")

# Get all logs
cursor.execute('SELECT id, channel, account_name FROM logs ORDER BY id DESC LIMIT 20')
logs = cursor.fetchall()

logging.info(f"Last 20 logs in the database:")
for log in logs:
    logging.info(f"  - Log ID: {log[0]}, Channel: {log[1]}, Account: {log[2]}")

# Check if channel names in logs match channel names in the database
for log in logs:
    channel_name = log[1]

    # Try exact match
    cursor.execute('SELECT id FROM channels WHERE name = ?', (channel_name,))
    exact_match = cursor.fetchone()

    # Try case-insensitive match
    cursor.execute('SELECT id FROM channels WHERE LOWER(name) = LOWER(?)', (channel_name,))
    case_insensitive_match = cursor.fetchone()

    # Try flexible match
    cursor.execute('SELECT id FROM channels WHERE LOWER(name) LIKE LOWER(?)', (f'%{channel_name}%',))
    flexible_match = cursor.fetchone()

    if exact_match:
        logging.info(f"Channel '{channel_name}' found with exact match (ID: {exact_match[0]})")
    elif case_insensitive_match:
        logging.warning(f"Channel '{channel_name}' found with case-insensitive match (ID: {case_insensitive_match[0]})")
    elif flexible_match:
        logging.warning(f"Channel '{channel_name}' found with flexible match (ID: {flexible_match[0]})")
    else:
        logging.error(f"Channel '{channel_name}' not found in the database")

# Close the connection
conn.close()
