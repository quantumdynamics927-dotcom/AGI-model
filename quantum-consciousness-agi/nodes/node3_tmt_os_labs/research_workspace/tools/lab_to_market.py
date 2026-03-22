import os
import json
from pathlib import Path
from dotenv import load_dotenv
from .pinata_uploader import PinataClient
from .minter import AGIMinter

load_dotenv()

pinata = PinataClient()
minter = AGIMinter()

class TMTPipeline:
    def __init__(self):
        self.pinata = pinata
        self.minter = minter

    def deploy_to_market(self, report_path: str, metadata: dict):
        report_path = Path(report_path)
        if not report_path.exists():
            raise FileNotFoundError(report_path)

        print('Uploading report to Pinata...')
        report_cid = self.pinata.upload_file(str(report_path))
        metadata['image'] = f'ipfs://{report_cid}'

        print('Uploading metadata to Pinata...')
        metadata_cid = self.pinata.upload_json(metadata)
        token_uri = f'ipfs://{metadata_cid}'

        print('Minting NFT on Polygon...')
        tx_hash = self.minter.mint(self.minter.account.address, token_uri)
        print('Mint tx hash:', tx_hash)
        return tx_hash

if __name__ == '__main__':
    print('TMTPipeline CLI for manual testing')
