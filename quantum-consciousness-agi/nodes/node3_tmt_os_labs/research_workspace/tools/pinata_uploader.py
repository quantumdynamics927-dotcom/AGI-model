import os
import requests
from typing import Dict, Any

PINATA_BASE = 'https://api.pinata.cloud'

class PinataClient:
    def __init__(self, api_key=None, api_secret=None, jwt=None):
        self.api_key = api_key or os.getenv('PINATA_API_KEY')
        self.api_secret = api_secret or os.getenv('PINATA_SECRET')
        self.jwt = jwt or os.getenv('PINATA_JWT')

    def _headers(self):
        if self.jwt:
            return {'Authorization': f'Bearer {self.jwt}'}
        return {'pinata_api_key': self.api_key, 'pinata_secret_api_key': self.api_secret}

    def upload_file(self, filepath: str) -> str:
        url = f'{PINATA_BASE}/pinning/pinFileToIPFS'
        with open(filepath, 'rb') as fh:
            files = {'file': (os.path.basename(filepath), fh)}
            r = requests.post(url, files=files, headers=self._headers())
        r.raise_for_status()
        return r.json()['IpfsHash']

    def upload_json(self, metadata: Dict[str, Any]) -> str:
        url = f'{PINATA_BASE}/pinning/pinJSONToIPFS'
        r = requests.post(url, json=metadata, headers=self._headers())
        r.raise_for_status()
        return r.json()['IpfsHash']

# convenience
pinata = PinataClient()
