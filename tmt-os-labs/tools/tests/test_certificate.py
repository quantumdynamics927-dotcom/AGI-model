from pathlib import Path
import json
import importlib.util


def load_certificate_module():
    cert_path = Path(__file__).resolve().parents[1] / "certificate.py"
    spec = importlib.util.spec_from_file_location("certificate", str(cert_path))
    cert = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cert)
    return cert


def test_generate_certificate(tmp_path):
    cert = load_certificate_module()
    nft = tmp_path / 'sample.nft.json'
    data = {
        "name": "TMT-OS Research: UnitTest",
        "attributes": [
            {"trait_type": "Researcher", "value": "UnitTester"},
            {"trait_type": "Integrity_Hash", "value": "deadbeef"},
            {"trait_type": "Timestamp", "value": 1600000000}
        ]
    }
    nft.write_text(json.dumps(data))
    out = cert.generate_certificate(nft)
    assert Path(out).exists()
