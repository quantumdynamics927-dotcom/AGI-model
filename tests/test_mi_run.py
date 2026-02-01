import sys
import os
# Ensure project root is on sys.path so imports work when running from tests/ folder
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tesla_integration_utils import calculate_tesla_consciousness
import json

res = calculate_tesla_consciousness({'00':600,'01':200,'10':150,'11':50})
print(json.dumps(res, indent=2))
