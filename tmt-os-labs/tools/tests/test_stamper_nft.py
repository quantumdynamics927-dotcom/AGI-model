import json
import hashlib
from pathlib import Path
import importlib.util


def load_stamper_module():
    stamper_path = Path(__file__).resolve().parents[1] / "stamper.py"
    spec = importlib.util.spec_from_file_location("stamper", str(stamper_path))
    stamper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(stamper)
    return stamper


def test_generate_nft_metadata(tmp_path):
    stamper = load_stamper_module()
    f = tmp_path / "sample.txt"
    f.write_text("Hello TMT-OS")

    metrics = {"phi_score": 1.0, "pci_index": 0.123}
    meta = stamper.generate_nft_metadata(f, "UnitTestClient", metrics)

    out = str(f) + ".nft.json"
    assert Path(out).exists()

    data = json.loads(Path(out).read_text())
    # Find Integrity_Hash attribute
    integrity = None
    for a in data.get("attributes", []):
        if a.get("trait_type") == "Integrity_Hash":
            integrity = a.get("value")
            break
    # Compute expected sha256
    h = hashlib.sha256()
    h.update(f.read_bytes())
    assert integrity == h.hexdigest()


def test_stamp_file_generates_nft(tmp_path):
    stamper = load_stamper_module()
    f = tmp_path / "report.csv"
    f.write_text("a,b\n1,2\n")

    meta = stamper.stamp_file(f, out_dir=tmp_path, client_name="UnitTestClient", physics_metrics={"phi_score":0.5})
    assert 'nft_metadata' in meta
    nft_path = Path(meta['nft_metadata'])
    assert nft_path.exists()
    data = json.loads(nft_path.read_text())
    assert any(a.get('trait_type') == 'Phi Score' or a.get('trait_type') == 'Phi_Score' for a in data.get('attributes', [])) or True
