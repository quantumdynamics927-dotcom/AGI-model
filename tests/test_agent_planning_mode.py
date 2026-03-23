from __future__ import annotations

import json
from pathlib import Path

from agi_scripts.dna_agent import generate_planning_report as generate_dna_plan
from agi_scripts.phi_agent import generate_planning_report as generate_phi_plan
from agi_scripts.qnn_agent import generate_planning_report as generate_qnn_plan


def test_dna_planning_mode_writes_report(tmp_path):
    report, report_path = generate_dna_plan(tmp_path)

    assert report["agent"] == "dna"
    assert report["planning_mode"] is True
    assert Path(report_path).exists()


def test_phi_planning_mode_detects_latest_dna_report(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    dna_results_dir = tmp_path / "dna_34bp_results"
    dna_results_dir.mkdir()
    (dna_results_dir / "dna_agent_report_20260101_000000.json").write_text(
        json.dumps({"status": "ok"}),
        encoding="utf-8",
    )

    report, report_path = generate_phi_plan(tmp_path)

    assert report["agent"] == "phi"
    assert report["current_state"]["dna_report_available"] is True
    assert Path(report_path).exists()


def test_qnn_planning_mode_detects_latest_phi_report(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "phi_agent_report_20260101_000000.json").write_text(
        json.dumps({"status": "ok"}),
        encoding="utf-8",
    )

    report, report_path = generate_qnn_plan(tmp_path)

    assert report["agent"] == "qnn"
    assert report["current_state"]["phi_report_available"] is True
    assert Path(report_path).exists()