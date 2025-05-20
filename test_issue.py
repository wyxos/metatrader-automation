import sys
import os
import json

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from validateOrder import validateOrder

# Test the issue with the specific message format
message = "BTCUSD buy 106900 tp 1 107100 tp 2 107200 tp 3 107300 tp 4 109500 sl 104900 no financial advice"
result = validateOrder(message)
print(json.dumps(result, indent=2))
