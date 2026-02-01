import pytest
import requests
from tmt_os_labs.tools.pinata_uploader import PinataClient

class DummyResponse:
    def __init__(self, json_data, status_code=200):
        self._json = json_data
        self.status_code = status_code
    def json(self):
        return self._json
    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f'Status {self.status_code}')

def test_upload_json_requests_mock(monkeypatch):
    pc = PinataClient(api_key='x', api_secret='y')
    def fake_post(url, json=None, headers=None):
        assert 'pinJSONToIPFS' in url
        return DummyResponse({'IpfsHash': 'QmFakeCid'})
    monkeypatch.setattr('requests.post', fake_post)
    cid = pc.upload_json({'name':'test'})
    assert cid == 'QmFakeCid'
