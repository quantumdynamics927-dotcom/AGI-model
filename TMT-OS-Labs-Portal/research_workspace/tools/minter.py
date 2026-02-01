import os
from web3 import Web3
import json

class AGIMinter:
    def __init__(self, provider_url=None, private_key=None, contract_address=None, abi_path=None):
        self.provider_url = provider_url or os.getenv('ALCHEMY_POLYGON_URL')
        self.w3 = Web3(Web3.HTTPProvider(self.provider_url))
        self.account = self.w3.eth.account.from_key(private_key or os.getenv('PRIVATE_KEY'))
        self.contract_address = contract_address or os.getenv('OPENSEA_CONTRACT_ADDR')
        if abi_path is None:
            abi_path = os.path.join(os.path.dirname(__file__), '..', '..', 'artifacts', 'contracts', 'AGIReportNFT.sol', 'AGIReportNFT.json')
        with open(abi_path) as f:
            self.abi = json.load(f)['abi']
        self.contract = self.w3.eth.contract(address=self.contract_address, abi=self.abi)

    def mint(self, to_address: str, token_uri: str, gas=500000):
        nonce = self.w3.eth.get_transaction_count(self.account.address)
        tx = self.contract.functions.mintResearch(to_address, token_uri).build_transaction({
            'from': self.account.address,
            'nonce': nonce,
            'gas': gas,
            'gasPrice': self.w3.eth.gas_price
        })
        signed = self.w3.eth.account.sign_transaction(tx, self.account.key)
        tx_hash = self.w3.eth.send_raw_transaction(signed.rawTransaction)
        return self.w3.to_hex(tx_hash)
