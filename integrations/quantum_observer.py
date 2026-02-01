"""Quantum Observer (Node 8) integration.

Provides simple utilities to verify that metadata hosted on IPFS/Pinata has been
observed on-chain via a given RPC endpoint (Polygon Amoy). Designed to be
lightweight and to return structured results for archival by Metatron.
"""
from typing import Optional, Dict, Any
from urllib.parse import urlparse
import requests
import logging

logger = logging.getLogger('quantum_observer')
logger.setLevel(logging.INFO)
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
    logger.addHandler(ch)


class QuantumObserver:
    def __init__(self, rpc_url: str = 'https://80002.rpc.thirdweb.com', chain_id: int = 80002, timeout: int = 10):
        self.rpc_url = rpc_url
        self.chain_id = chain_id
        self.timeout = timeout

    def verify_pinata(self, pinata_url: str) -> Dict[str, Any]:
        """Check that the Piñata/IPFS URL is reachable and returns JSON/metadata."""
        try:
            r = requests.get(pinata_url, timeout=self.timeout)
            return {'ok': r.status_code == 200, 'status_code': r.status_code, 'content_type': r.headers.get('Content-Type'), 'text_snippet': r.text[:500]}
        except Exception as e:
            logger.debug('Pinata verification failed: %s', e)
            return {'ok': False, 'error': str(e)}

    def rpc_call(self, method: str, params: Optional[list] = None) -> Dict[str, Any]:
        payload = {'jsonrpc': '2.0', 'id': 1, 'method': method, 'params': params or []}
        try:
            r = requests.post(self.rpc_url, json=payload, timeout=self.timeout)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            logger.debug('RPC call failed: %s', e)
            return {'error': str(e)}

    def get_block_number(self) -> Dict[str, Any]:
        return self.rpc_call('eth_blockNumber', [])

    def get_tx_receipt(self, tx_hash: str) -> Dict[str, Any]:
        return self.rpc_call('eth_getTransactionReceipt', [tx_hash])

    def verify_observation(self, pinata_url: str, tx_hash: Optional[str] = None) -> Dict[str, Any]:
        """Run a verification: check IPFS/Pinata then (optionally) check transaction on chain.

        Returns a dict with pinata check, rpc block number, and tx receipt (if tx_hash provided).
        """
        result: Dict[str, Any] = {'pinata': None, 'rpc': None, 'tx_receipt': None}
        result['pinata'] = self.verify_pinata(pinata_url)
        result['rpc'] = self.get_block_number()
        if tx_hash:
            result['tx_receipt'] = self.get_tx_receipt(tx_hash)
        return result


def pinfs_gateway_from_cid(cid: str) -> str:
    """Return a gateway URL for a CID or placeholder string.

    If input already looks like a URL, return it unchanged.
    """
    if cid.startswith('http://') or cid.startswith('https://'):
        return cid
    # strip ipfs://
    if cid.startswith('ipfs://'):
        cid = cid[len('ipfs://'):]
    return f'https://gateway.pinata.cloud/ipfs/{cid}'
