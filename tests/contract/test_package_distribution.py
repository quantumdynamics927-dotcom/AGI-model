from __future__ import annotations

from pathlib import Path


def test_transitional_root_modules_are_included_in_build_config() -> None:
    pyproject = Path(__file__).resolve().parents[2] / "pyproject.toml"
    content = pyproject.read_text(encoding="utf-8")

    assert '{ include = "vae_model.py" }' in content
    assert '{ include = "ollama_cloud_models.py" }' in content
