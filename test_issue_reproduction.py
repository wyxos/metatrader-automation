import json
import sys
import os

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from validateOrder import validateOrder

# The message from the issue description
message = "XAUUSD buy 3309 tp 1 3311 tp 2 3312 tp 3 3313 tp 4 3330 sl 3290 no financial advice"

# Parse the message
result = validateOrder(message)

# Print the result
print(json.dumps(result, indent=2))

# Expected tp values: [3311, 3312, 3313, 3330]
print("\nExpected tp values: [3311, 3312, 3313, 3330]")
print("Actual tp values:", result["tp"])
