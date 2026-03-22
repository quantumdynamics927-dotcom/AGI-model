"""Compatibility shim to expose Node3ExperimentalLabs at repository root."""

import importlib.util
from pathlib import Path

_src = Path(__file__).resolve().parent / 'tmt-os-labs' / 'node3_experimental_labs.py'
_spec = importlib.util.spec_from_file_location('_node3_experimental_labs_impl', _src)
_mod = importlib.util.module_from_spec(_spec)
assert _spec is not None and _spec.loader is not None
_spec.loader.exec_module(_mod)

Node3ExperimentalLabs = _mod.Node3ExperimentalLabs
PHI = _mod.PHI
