"""IPFS adapter with optional real upload support.

Tries to use `ipfshttpclient` to add files to a local or remote IPFS node. If the
library or node is unavailable, falls back to deterministic placeholder CIDs using
the file SHA256 (not real IPFS CIDs, but stable for testing).

Functions:
- upload_file(path) -> cid (str)
- upload_bytes(bytes, name) -> cid (str)
"""
from pathlib import Path
import hashlib
import json
import logging

logger = logging.getLogger('ipfs_adapter')
logger.setLevel(logging.INFO)
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
    logger.addHandler(ch)

try:
    import ipfshttpclient
except Exception:
    ipfshttpclient = None
import os
import requests


def _sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _placeholder_cid_from_hash(hexhash: str) -> str:
    # Create a stable placeholder CID-like string
    return f'PHCID-{hexhash[:46]}'


def upload_file(path: Path) -> str:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(str(path))
    data = path.read_bytes()
    # Prefer Pinata if configured via env
    pinata_jwt = os.getenv('PINATA_JWT')
    pinata_key = os.getenv('PINATA_API_KEY')
    pinata_secret = os.getenv('PINATA_API_SECRET')
    if pinata_jwt or (pinata_key and pinata_secret):
        try:
            if pinata_jwt:
                headers = {'Authorization': f'Bearer {pinata_jwt}'}
            else:
                headers = {'pinata_api_key': pinata_key, 'pinata_secret_api_key': pinata_secret}
            with open(path, 'rb') as fh:
                files = {'file': (path.name, fh)}
                resp = requests.post('https://api.pinata.cloud/pinning/pinFileToIPFS', files=files, headers=headers, timeout=30)
            resp.raise_for_status()
            j = resp.json()
            cid = j.get('IpfsHash') or j.get('IpfsHash')
            logger.info('Pinned %s to Pinata -> %s', path, cid)
            return cid
        except Exception as e:
            logger.debug('Pinata upload failed: %s', e)
    if ipfshttpclient:
        try:
            client = ipfshttpclient.connect()
            res = client.add(str(path))
            cid = res.get('Hash') or res.get('Cid')
            logger.info('Uploaded %s -> %s', path, cid)
            return cid
        except Exception as e:
            logger.debug('ipfshttpclient failed: %s', e)
    # fallback
    hexh = _sha256_hex(data)
    cid = _placeholder_cid_from_hash(hexh)
    logger.info('Using placeholder CID for %s -> %s', path, cid)
    return cid


def upload_bytes(data: bytes, name: str = 'blob') -> str:
    pinata_jwt = os.getenv('PINATA_JWT')
    pinata_key = os.getenv('PINATA_API_KEY')
    pinata_secret = os.getenv('PINATA_API_SECRET')
    if pinata_jwt or (pinata_key and pinata_secret):
        try:
            headers = {'Content-Type': 'application/json'}
            if pinata_jwt:
                headers['Authorization'] = f'Bearer {pinata_jwt}'
            else:
                headers.update({'pinata_api_key': pinata_key, 'pinata_secret_api_key': pinata_secret})
            # Pin JSON via pinJSONToIPFS
            resp = requests.post('https://api.pinata.cloud/pinning/pinJSONToIPFS', json={'name': name, 'data': data.decode('utf-8', errors='ignore')}, headers=headers, timeout=30)
            resp.raise_for_status()
            j = resp.json()
            cid = j.get('IpfsHash')
            logger.info('Pinned bytes to Pinata -> %s', cid)
            return cid
        except Exception as e:
            logger.debug('Pinata pinJSON failed: %s', e)
    if ipfshttpclient:
        try:
            client = ipfshttpclient.connect()
            res = client.add_bytes(data)
            cid = res
            logger.info('Uploaded bytes %s -> %s', name, cid)
            return cid
        except Exception as e:
            logger.debug('ipfshttpclient.add_bytes failed: %s', e)
    hexh = _sha256_hex(data)
    cid = _placeholder_cid_from_hash(hexh)
    logger.info('Using placeholder CID for bytes %s -> %s', name, cid)
    return cid
