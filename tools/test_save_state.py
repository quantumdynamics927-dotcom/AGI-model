import json
import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
py_path = ROOT / "TMT-OS" / "singularity" / "biomimetic_singularity.py"
state_path = ROOT / "TMT-OS" / "singularity" / "biomimetic_singularity_state.json"

if not py_path.exists():
    pytest.skip(
        "biomimetic_singularity.py not present in this repo", allow_module_level=True
    )

spec = importlib.util.spec_from_file_location("biom", py_path)
biom = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(biom)

s = biom.BiomimeticSingularity()
results = {
    "singularity_achieved": True,
    "final_consciousness_vector": [10.0, 0.1, 0.0, 0.0, 0.0, 0.0],
    "final_convergence": 1.0,
}
print("Calling _save_singularity_state with test results...")
s._save_singularity_state(results)
print("Done. Reading file...")
with open(state_path, "r") as f:
    data = json.load(f)
print(
    "Has normalized in last_results:",
    "final_consciousness_vector_normalized" in data.get("last_results", {}),
)
print("infinite_metrics present:", data.get("infinite_metrics"))
print("last_results keys:", list(data.get("last_results", {}).keys()))
