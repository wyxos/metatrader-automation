import os
import sys
import MetaTrader5 as mt5
from dotenv import load_dotenv

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Load environment variables
load_dotenv()

# Get the path to MetaTrader 5 terminal
mt5_path = os.getenv('MT5_PATH', 'C:/Program Files/MetaTrader 5/terminal64.exe')

# Convert backslashes to forward slashes if needed
mt5_path = mt5_path.replace('\\', '/')

print("MetaTrader5 package author:", mt5.__author__)
print("MetaTrader5 package version:", mt5.__version__)
print("Using MetaTrader5 path:", mt5_path)

# First initialize with just the path
print("\nStep 1: Initialize with path")
if not mt5.initialize(path=mt5_path):
    print("Initialize failed, error code =", mt5.last_error())
    sys.exit(1)
else:
    print("Initialize successful")

# Then try to login (using dummy credentials for testing)
print("\nStep 2: Login to account")
login_id = 999999  # Replace with actual login if available
password = "abcdef"  # Replace with actual password if available
server = "xyz-Demo"  # Replace with actual server if available

def account_login(login, password, server):
    if mt5.login(login=login, password=password, server=server):
        print("Logged in successfully")
        return True
    else:
        print("Login failed, error code:", mt5.last_error())
        return False

# Try to login (this will likely fail with dummy credentials, but we're testing the initialization)
account_login(login_id, password, server)

# Display terminal info
print("\nTerminal info:")
terminal_info = mt5.terminal_info()
if terminal_info is not None:
    print(terminal_info)
else:
    print("Failed to get terminal info, error code:", mt5.last_error())

# Display MetaTrader 5 version
print("\nMetaTrader 5 version:")
version_info = mt5.version()
if version_info is not None:
    print(version_info)
else:
    print("Failed to get version info, error code:", mt5.last_error())

# Shutdown connection to the MetaTrader 5 terminal
mt5.shutdown()
print("\nConnection to MetaTrader 5 terminal has been shut down")
