from pathlib import Path
import json
import tempfile
import os

from metatron_nervous_system import MetatronNervousSystem


def test_encode_decode_roundtrip():
    m = MetatronNervousSystem(Path(tempfile.mkdtemp()))
    val = 123.456
    compressed = m.phi_compress(val)
    dna = m.encode_to_dna(compressed)
    decoded = m.decode_from_dna(dna)
    # decoded will be an integer scaled value divided by 10000
    assert abs(decoded - int(abs(compressed) * 10000) / 10000.0) < 1e-6


def test_create_and_archive(tmp_path, monkeypatch):
    # create a tiny CSV file
    csv = tmp_path / 'sample.csv'
    csv.write_text('fitness,phi_score\n10,1.0\n20,1.0\n')
    registry = Path(tempfile.mkdtemp())
    m = MetatronNervousSystem(registry)
    # ensure no env key
    monkeypatch.delenv('TMTOS_STAMPER_KEY', raising=False)
    archived = m.scan_and_archive([tmp_path], client='unittest')
    assert len(archived) == 1
    packet = json.loads(archived[0].read_text())
    assert packet['client'] == 'unittest'
    assert 'dna_packet' in packet


def test_hmac_signature(tmp_path, monkeypatch):
    csv = tmp_path / 'sample2.csv'
    csv.write_text('fitness,phi_score\n5,2.0\n')
    registry = Path(tempfile.mkdtemp())
    m = MetatronNervousSystem(registry)
    meta_key = 'mysecret'
    archived = m.scan_and_archive([tmp_path], client='u', hmac_key=meta_key)
    packet = json.loads(archived[0].read_text())
    assert 'hmac_signature' in packet
    # verify signature matches sha
    import hmac as _hmac, hashlib
    expected = _hmac.new(meta_key.encode('utf-8'), packet['sha256'].encode('utf-8'), hashlib.sha256).hexdigest()
    assert packet['hmac_signature'] == expected
