from pathlib import Path
import os

from integrations.cybershield_adapter import ingest_scan_file, ingest_scan_payload
from tools.syntheticizer import Syntheticizer


def test_ingest_and_synthesize_file(tmp_path, monkeypatch):
    monkeypatch.setenv('PRIVATE_VAULT_SALT', 'test_salt_123')
    monkeypatch.setenv('AGI_VAULT_DIR', str(tmp_path / 'vault'))
    raw = tmp_path / 'raw_samples.csv'
    raw.write_text(
        'patient_id,age,gender,visit_date,cholesterol\n'
        'abc-123,42,M,2025-01-01,5.4\n'
        'def-456,37,F,2025-01-15,4.9\n',
        encoding='utf-8',
    )

    res = ingest_scan_file(str(raw), source='unittest')
    assert 'sanitized_path' in res
    assert Path(res['sanitized_path']).exists()
    assert isinstance(res['ledger_index'], int)

    syn = Syntheticizer.syntheticize_file(
        res['sanitized_path'],
        n_samples=5,
        latent=2,
        epochs=1,
    )
    assert 'synthetic_path' in syn
    assert Path(syn['synthetic_path']).exists()
    assert str(tmp_path / 'vault') in syn['synthetic_path']


def test_ingest_payload_and_single_row(tmp_path, monkeypatch):
    monkeypatch.setenv('PRIVATE_VAULT_SALT', 'test_salt_123')
    monkeypatch.setenv('AGI_VAULT_DIR', str(tmp_path / 'vault'))
    payload = {
        'patient_id': 'abc-123',
        'age': 42,
        'gender': 'M',
        'visit_date': '2025-01-01',
        'cholesterol': 5.4,
    }
    res = ingest_scan_payload(payload, source='unittest')
    assert 'sanitized_path' in res
    assert str(tmp_path / 'vault') in res['sanitized_path']
    sr = Syntheticizer.syntheticize_row(
        payload,
        n_samples=1,
        latent=2,
        epochs=1,
    )
    assert 'synthetic_path' in sr
    assert Path(sr['synthetic_path']).exists()
    assert str(tmp_path / 'vault') in sr['synthetic_path']
