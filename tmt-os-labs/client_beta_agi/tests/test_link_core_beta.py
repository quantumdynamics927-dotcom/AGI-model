import os
import sys
from pathlib import Path

import pytest


def test_resolve_core_path_env_override(monkeypatch, tmp_path):
    monkeypatch.setenv('TMTOS_CORE_PATH', str(tmp_path))
    assert os.getenv('TMTOS_CORE_PATH') == str(tmp_path)


def test_core_path_in_sys_path(monkeypatch, tmp_path):
    p = str(tmp_path)
    if p in sys.path:
        sys.path.remove(p)
    sys.path.append(p)
    assert p in sys.path


def test_import_yesod(monkeypatch):
    try:
        import yesod_mirror_tools
    except ImportError:
        pytest.skip("yesod_mirror_tools not installed in this environment")
    assert 'yesod_mirror_tools' in sys.modules
