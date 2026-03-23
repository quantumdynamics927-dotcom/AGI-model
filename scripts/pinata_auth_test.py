import os

import requests


def _noop_load_dotenv(*_args, **_kwargs):
    return None


try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = _noop_load_dotenv
    if __name__ != "__main__":
        import pytest

        pytest.skip("python-dotenv is not installed", allow_module_level=True)

if __name__ != "__main__":
    import pytest

    PINATA_JWT = os.getenv("PINATA_JWT")
    PINATA_API_KEY = os.getenv("PINATA_API_KEY")
    PINATA_API_SECRET = os.getenv("PINATA_API_SECRET")
    if not (PINATA_JWT or (PINATA_API_KEY and PINATA_API_SECRET)):
        pytest.skip(
            "Pinata credentials not configured for CI",
            allow_module_level=True,
        )

# Load local .env for local testing
load_dotenv()

jwt = os.getenv("PINATA_JWT")
api_key = os.getenv("PINATA_API_KEY")
api_secret = os.getenv("PINATA_API_SECRET")

print("JWT present:", bool(jwt))
print("API key present:", bool(api_key))
print("API secret present:", bool(api_secret))

headers_jwt = {"Authorization": f"Bearer {jwt}"} if jwt else {}
try:
    r = requests.get(
        "https://api.pinata.cloud/data/testAuthentication",
        headers=headers_jwt,
        timeout=10,
    )
    print("testAuthentication (JWT):", r.status_code, r.text[:200])
except requests.RequestException as e:
    print("testAuthentication (JWT) error:", e)

# Try pinJSONToIPFS with API key/secret
payload = {"test": "ping"}
headers_keys = {"pinata_api_key": api_key, "pinata_secret_api_key": api_secret}
try:
    r2 = requests.post(
        "https://api.pinata.cloud/pinning/pinJSONToIPFS",
        json=payload,
        headers=headers_keys,
        timeout=10,
    )
    print("pinJSONToIPFS (API keys):", r2.status_code, r2.text[:200])
except requests.RequestException as e:
    print("pinJSONToIPFS (API keys) error:", e)

# Try pinJSONToIPFS with JWT
try:
    r3 = requests.post(
        "https://api.pinata.cloud/pinning/pinJSONToIPFS",
        json=payload,
        headers=headers_jwt,
        timeout=10,
    )
    print("pinJSONToIPFS (JWT):", r3.status_code, r3.text[:200])
except requests.RequestException as e:
    print("pinJSONToIPFS (JWT) error:", e)
