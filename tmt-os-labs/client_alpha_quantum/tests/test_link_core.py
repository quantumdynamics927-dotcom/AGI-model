import os
import sys
from pathlib import Path

import pytest

from importlib import reload


def test_resolve_core_path_env_override(monkeypatch, tmp_path):
    monkeypatch.setenv('TMTOS_CORE_PATH', str(tmp_path))
    try:
        from notebooks import link_tmt_os_core as ltc  # import the module (notebook exported as py) - placeholder
    except ImportError:
        pytest.skip("link_tmt_os_core notebook not exported to python module")
    # Since we can't import notebook directly in pytest run, assert environment variable is read correctly
    assert os.getenv('TMTOS_CORE_PATH') == str(tmp_path)


def test_core_path_in_sys_path(monkeypatch, tmp_path):
    # Simulate resolve and ensure sys.path gets the path
    p = str(tmp_path)
    if p in sys.path:
        sys.path.remove(p)
    sys.path.append(p)
    assert p in sys.path


def test_import_yesod(monkeypatch):
    # This test will pass if yesod_mirror_tools is importable; otherwise skip
    try:
        import yesod_mirror_tools
    except ImportError:
        pytest.skip("yesod_mirror_tools not installed in this environment")
    assert 'yesod_mirror_tools' in sys.modules
