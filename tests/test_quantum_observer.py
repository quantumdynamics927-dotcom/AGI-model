import json
import pytest
from integrations.quantum_observer import QuantumObserver


class DummyResponse:
    def __init__(self, status_code=200, text='ok', headers=None, json_data=None):
        self.status_code = status_code
        self.text = text
        self.headers = headers or {'Content-Type': 'application/json'}
        self._json = json_data or {'id': 1, 'jsonrpc': '2.0', 'result': '0x10'}

    def json(self):
        return self._json

    def raise_for_status(self):
        if self.status_code >= 400:
            raise Exception(f'HTTP {self.status_code}')


def test_get_block_number_monkeypatch(monkeypatch):
    obs = QuantumObserver(rpc_url='https://example.rpc')

    def fake_post(url, json, timeout):
        return DummyResponse(json_data={'id': json.get('id'), 'jsonrpc': '2.0', 'result': '0xabc'})

    monkeypatch.setattr('requests.post', fake_post)
    res = obs.get_block_number()
    assert isinstance(res, dict)
    assert res.get('result') == '0xabc'


def test_verify_pinata_monkeypatch(monkeypatch):
    obs = QuantumObserver()

    def fake_get(url, timeout):
        return DummyResponse(status_code=200, text='{"name":"test"}', json_data={'name': 'test'})

    monkeypatch.setattr('requests.get', fake_get)
    res = obs.verify_pinata('https://gateway.pinata.cloud/ipfs/FAKECID')
    assert res['ok'] is True
    assert 'content_type' in res
