"""Mint adapter for on-chain minting via web3 (or thirdweb if available).

This adapter provides a minimal `MintAdapter` that can mint an ERC-721 style
token by calling common methods (`mintTo`, `safeMint`, `mint`). It prefers
`web3` (web3.py) for direct RPC signing and sending. If `web3` is unavailable
it will raise ImportError with instructions.

Usage:
    adapter = MintAdapter(rpc_url, private_key)
    tx_hash = adapter.mint_erc721(contract_address, to_address, token_uri, abi=optional_abi)

Note: This is a lightweight adapter; adapt to your contract's ABI and mint
method names as needed.
"""
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger('mint_adapter')
logger.setLevel(logging.INFO)
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
    logger.addHandler(ch)

try:
    from web3 import Web3
    from web3.middleware import geth_poa_middleware
except Exception:
    Web3 = None


class MintAdapter:
    def __init__(self, rpc_url: str, private_key: Optional[str] = None, chain_id: Optional[int] = None):
        if Web3 is None:
            raise ImportError('web3.py is required for MintAdapter. Install with `pip install web3`')
        self.rpc_url = rpc_url
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        # common for polygon testnets
        try:
            self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        except Exception:
            pass
        self.private_key = private_key
        self.chain_id = chain_id or int(self.w3.eth.chain_id)

    def _build_contract(self, contract_address: str, abi: Optional[Any] = None):
        if abi:
            return self.w3.eth.contract(address=self.w3.toChecksumAddress(contract_address), abi=abi)
        # minimal ABI with common mint variants
        minimal_abi = [
            {
                'constant': False,
                'inputs': [{'name': 'to', 'type': 'address'}, {'name': 'tokenURI', 'type': 'string'}],
                'name': 'mintTo',
                'outputs': [],
                'type': 'function',
            },
            {
                'constant': False,
                'inputs': [{'name': 'to', 'type': 'address'}, {'name': 'tokenURI', 'type': 'string'}],
                'name': 'safeMint',
                'outputs': [],
                'type': 'function',
            },
            {
                'constant': False,
                'inputs': [{'name': 'to', 'type': 'address'}, {'name': 'tokenURI', 'type': 'string'}],
                'name': 'mint',
                'outputs': [],
                'type': 'function',
            },
        ]
        return self.w3.eth.contract(address=self.w3.toChecksumAddress(contract_address), abi=minimal_abi)

    def _build_tx(self, func_call, from_address: str, gas: Optional[int] = None, gas_price: Optional[int] = None):
        tx = func_call.buildTransaction({
            'from': self.w3.toChecksumAddress(from_address),
            'nonce': self.w3.eth.get_transaction_count(self.w3.toChecksumAddress(from_address)),
            'chainId': self.chain_id,
        })
        if gas:
            tx['gas'] = gas
        if gas_price:
            tx['gasPrice'] = gas_price
        else:
            try:
                tx['gasPrice'] = self.w3.eth.gas_price
            except Exception:
                pass
        return tx

    def _sign_send(self, tx: Dict[str, Any]):
        if not self.private_key:
            raise ValueError('private_key required to sign transactions')
        signed = self.w3.eth.account.sign_transaction(tx, private_key=self.private_key)
        tx_hash = self.w3.eth.send_raw_transaction(signed.rawTransaction)
        logger.info('Sent tx: %s', tx_hash.hex())
        return tx_hash.hex()

    def mint_erc721(self, contract_address: str, to_address: str, token_uri: str, abi: Optional[Any] = None,
                    from_address: Optional[str] = None, gas: Optional[int] = None, gas_price: Optional[int] = None) -> str:
        """Attempt to mint an ERC-721 token by trying common mint function names.

        Returns transaction hash (hex) on success.
        """
        contract = self._build_contract(contract_address, abi=abi)
        candidate_funcs = ['mintTo', 'safeMint', 'mint']
        func = None
        for name in candidate_funcs:
            if hasattr(contract.functions, name):
                try:
                    func = getattr(contract.functions, name)(to_address, token_uri)
                    break
                except Exception:
                    # some ABIs may expect different signatures; try the next
                    func = None
        if func is None:
            # Try generic fallback: if contract has a `create` or `mintToken` method with single arg
            for name in ['create', 'mintToken', 'safeMintTo']:
                if hasattr(contract.functions, name):
                    try:
                        func = getattr(contract.functions, name)(to_address, token_uri)
                        break
                    except Exception:
                        func = None
        if func is None:
            raise RuntimeError('No known mint function available on contract; provide ABI or adapt adapter')

        if not from_address:
            # derive from private key
            acct = self.w3.eth.account.from_key(self.private_key) if self.private_key else None
            from_address = acct.address if acct else self.w3.eth.default_account
        tx = self._build_tx(func, from_address, gas=gas, gas_price=gas_price)
        return self._sign_send(tx)
