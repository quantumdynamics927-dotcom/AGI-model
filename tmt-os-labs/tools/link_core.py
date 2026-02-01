"""Helper utilities to link client code to the TMT-OS core.

Functions:
- resolve_core_path()
- ensure_core_in_path()
- try_import(module_name)
- write_local_core_path/read_local_core_path
"""
from pathlib import Path
import os
import sys
import logging

logger = logging.getLogger("tmtos_client")


def resolve_core_path():
    env = os.getenv("TMTOS_CORE_PATH")
    if env:
        p = Path(env)
    else:
        p = Path(r"E:\\tmt-os")
    p = p.expanduser().resolve()
    if not p.exists():
        raise FileNotFoundError(f"Core path not found: {p}. Set TMTOS_CORE_PATH or ensure E:\\tmt-os exists.")
    return str(p)


def ensure_core_in_path():
    core = resolve_core_path()
    if core not in sys.path:
        sys.path.append(core)
        logger.info("Added CORE_PATH to sys.path: %s", core)
    return core


def try_import(module_name: str):
    try:
        module = __import__(module_name)
        logger.info("Imported %s", module_name)
        return module
    except ImportError as e:
        logger.exception("Failed to import %s from CORE_PATH", module_name)
        raise


CONFIG_FILE = Path('.tmtos_core_path')

def write_local_core_path(core_path, file_path=CONFIG_FILE):
    file_path.write_text(str(core_path))
    logger.info("Wrote core path to %s", file_path)


def read_local_core_path(file_path=CONFIG_FILE):
    if file_path.exists():
        return file_path.read_text().strip()
    return None
