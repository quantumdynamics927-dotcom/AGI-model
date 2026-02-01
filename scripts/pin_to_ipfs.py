"""
Utility: pin a JSON file to Web3.storage and return CID.
(This is optional — mint.py contains the same helper.)
"""

import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

WEB3_STORAGE_API_KEY = os.getenv("WEB3_STORAGE_API_KEY")

if not WEB3_STORAGE_API_KEY:
    raise SystemExit("Set WEB3_STORAGE_API_KEY in .env")


def pin_json(json_obj, filename="manifest.json"):
    url = "https://api.web3.storage/upload"
    headers = {"Authorization": f"Bearer {WEB3_STORAGE_API_KEY}"}
    files = {"file": (filename, json.dumps(json_obj).encode())}
    r = requests.post(url, headers=headers, files=files)
    r.raise_for_status()
    return r.json().get("cid")


if __name__ == "__main__":
    sample = {"hello": "world"}
    cid = pin_json(sample)
    print("CID:", cid)
