import sqlite3
import csv

def export_sqlite_to_csv(db_file, table_name, csv_file):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Fetch all rows from the specified table
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()

    # Fetch column names from the table
    column_names = [description[0] for description in cursor.description]

    # Write data to CSV file
    with open(csv_file, 'w', newline='', encoding='utf-8') as csvfile:
        csv_writer = csv.writer(csvfile)
        # Write the column headers
        csv_writer.writerow(column_names)
        # Write the data rows
        csv_writer.writerows(rows)

    # Close the connection
    conn.close()
    print(f"Data from table '{table_name}' has been exported to '{csv_file}'.")

if __name__ == "__main__":
    # Database and table information
    db_file = 'telegram_mt5_logs.db'
    table_name = 'logs'
    csv_file = 'logs_export.csv'

    # Export the table to CSV
    export_sqlite_to_csv(db_file, table_name, csv_file)
