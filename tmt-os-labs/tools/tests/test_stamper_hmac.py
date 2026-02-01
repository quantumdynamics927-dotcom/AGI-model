import json
import hashlib
import hmac as _hmac
from pathlib import Path
import importlib.util


def load_stamper_module():
    stamper_path = Path(__file__).resolve().parents[1] / "stamper.py"
    spec = importlib.util.spec_from_file_location("stamper", str(stamper_path))
    stamper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(stamper)
    return stamper


def test_stamp_file_hmac_direct_key(tmp_path):
    stamper = load_stamper_module()
    f = tmp_path / "report.csv"
    f.write_text("a,b\n1,2\n")
    key = "supersecret"
    meta = stamper.stamp_file(f, out_dir=tmp_path, client_name=None, physics_metrics=None, hmac_key=key)
    assert 'hmac_signature' in meta
    # Validate signature equals expected HMAC of sha256 digest
    digest = hashlib.sha256(f.read_bytes()).hexdigest()
    expected = _hmac.new(key.encode('utf-8'), digest.encode('utf-8'), hashlib.sha256).hexdigest()
    assert meta['hmac_signature'] == expected


def test_stamp_file_hmac_env_key(tmp_path, monkeypatch):
    stamper = load_stamper_module()
    f = tmp_path / "report2.csv"
    f.write_text("x,y\n3,4\n")
    monkeypatch.setenv('TMTOS_STAMPER_KEY', 'envsecret')
    meta = stamper.stamp_file(f, out_dir=tmp_path)
    assert 'hmac_signature' in meta
    digest = hashlib.sha256(f.read_bytes()).hexdigest()
    expected = _hmac.new(b'envsecret', digest.encode('utf-8'), hashlib.sha256).hexdigest()
    assert meta['hmac_signature'] == expected
