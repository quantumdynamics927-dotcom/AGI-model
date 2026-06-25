"""Tests for backend_aware_offset (Milestone 0 of the Quantum AGI roadmap).

Run with::

    PYTHONPATH="$(pwd):$(pwd)/TMT-OS:$(pwd)/tmt-os-labs:$(pwd)/integrations:$(pwd)/agi_scripts:$(pwd)/agi_app:$(pwd)/agi_model:$(pwd)/quantum_observer" \\
        python -m pytest tests/test_backend_aware_offset.py -v
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

from backend_aware_offset import (
    BackendAwareOffsetEstimator,
    BackendAwareOffsetReport,
    main as cli_main,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


# ---------- helpers ----------


def _make_record(backend: str, measured: float, predicted: float) -> dict:
    return {
        "job_id": f"job-{backend}-{measured:.4f}",
        "backend": backend,
        "measured_phi": measured,
        "predicted_phi": predicted,
    }


def _make_backend_records(backend: str, true_offset: float, n: int, sigma: float, predicted_mean: float = 0.75, rng: np.random.Generator | None = None) -> list[dict]:
    """Generate ``n`` synthetic records with a planted backend offset."""
    rng = rng or np.random.default_rng(seed=hash(backend) % (2**32))
    predicted = rng.normal(loc=predicted_mean, scale=0.05, size=n)
    # Plant the offset exactly so recovered mean should converge to true_offset
    # for large n.
    measured = predicted + true_offset + rng.normal(loc=0.0, scale=sigma, size=n)
    return [
        _make_record(backend, float(m), float(p))
        for m, p in zip(measured, predicted)
    ]


# ---------- shrinkage behavior ----------


def test_shrinkage_pulls_single_sample_toward_global():
    """A backend with n=1 should be pulled hard toward the global mean."""
    # Global mean ~ -0.1 from the big backend; the singleton has offset -0.5.
    records = (
        _make_backend_records("ibm_big", true_offset=-0.10, n=20, sigma=0.01)
        + [_make_record("ibm_lonely", measured=0.20, predicted=0.70)]  # offset = -0.50
    )
    rep = BackendAwareOffsetEstimator(shrinkage_prior_n=5.0).fit(records)

    big = next(m for m in rep.per_backend if m.backend == "ibm_big")
    lonely = next(m for m in rep.per_backend if m.backend == "ibm_lonely")

    # Big backend: weight should be high (20 / 25 = 0.8).
    assert big.shrinkage_weight == pytest.approx(0.8, abs=1e-9)

    # Singleton: weight should be 1/6 ≈ 0.167, so the shrunk offset is heavily
    # pulled toward the global mean (~-0.1), not the singleton's -0.5.
    assert lonely.shrinkage_weight == pytest.approx(1.0 / 6.0, abs=1e-9)
    # The singleton's reported shrunk_offset should be much closer to the
    # global mean than to its own raw -0.5.
    assert abs(lonely.shrunk_offset - rep.global_offset) < abs(lonely.mean_offset - rep.global_offset)
    # And the shrinkage pull must be at least 50% of the way toward the global.
    pull = abs(lonely.mean_offset - lonely.shrunk_offset)
    full_distance = abs(lonely.mean_offset - rep.global_offset)
    assert pull >= 0.5 * full_distance


def test_shrinkage_prior_n_zero_disables_shrinkage():
    """If the operator sets the prior to 0, per-backend estimates are reported unmodified."""
    records = _make_backend_records("ibm_a", true_offset=-0.10, n=10, sigma=0.01)
    rep = BackendAwareOffsetEstimator(shrinkage_prior_n=0.0).fit(records)
    [only] = rep.per_backend
    assert only.shrinkage_weight == 1.0
    assert only.shrunk_offset == pytest.approx(only.mean_offset, abs=1e-12)


def test_shrinkage_prior_n_rejects_negative():
    with pytest.raises(ValueError):
        BackendAwareOffsetEstimator(shrinkage_prior_n=-1.0)


# ---------- synthetic-data recovery ----------


def test_recovery_on_synthetic_three_backends():
    """With 3 backends x 10 samples, the per-backend mean should converge to the planted value
    and the shrunk offset should lie in the convex hull of [global_mean, backend_mean].

    We allow 3 * sigma on the per-backend mean (n=10 is small for tight convergence)
    and require only that shrinkage keeps the shrunk value between the global mean and the
    backend-specific mean (the defining property of the estimator).
    """
    rng = np.random.default_rng(seed=20260625)
    sigma = 0.02
    records = (
        _make_backend_records("ibm_a", true_offset=-0.10, n=10, sigma=sigma, rng=rng)
        + _make_backend_records("ibm_b", true_offset=-0.20, n=10, sigma=sigma, rng=rng)
        + _make_backend_records("ibm_c", true_offset=+0.05, n=10, sigma=sigma, rng=rng)
    )

    rep = BackendAwareOffsetEstimator(shrinkage_prior_n=5.0).fit(records)
    expected = {"ibm_a": -0.10, "ibm_b": -0.20, "ibm_c": 0.05}

    for m in rep.per_backend:
        assert m.sample_count == 10
        # (a) Per-backend mean should be within 3*sigma of the planted truth.
        mean_diff = abs(m.mean_offset - expected[m.backend])
        assert mean_diff < 3 * sigma, (
            f"{m.backend}: mean_offset={m.mean_offset:.4f}, expected={expected[m.backend]}"
        )
        # (b) Shrunk offset must lie between global and per-backend mean (convex hull).
        lo = min(m.mean_offset, rep.global_offset)
        hi = max(m.mean_offset, rep.global_offset)
        assert lo - 1e-12 <= m.shrunk_offset <= hi + 1e-12, (
            f"{m.backend}: shrunk={m.shrunk_offset:.4f} not in [{lo:.4f}, {hi:.4f}]"
        )


# ---------- report shape ----------


def test_report_json_round_trip():
    records = _make_backend_records("ibm_x", true_offset=-0.15, n=4, sigma=0.01)
    rep = BackendAwareOffsetEstimator().fit(records)
    blob = rep.to_json()
    parsed = json.loads(blob)
    assert parsed["total_samples"] == 4
    assert len(parsed["per_backend"]) == 1
    assert parsed["per_backend"][0]["backend"] == "ibm_x"
    assert parsed["per_backend"][0]["sample_count"] == 4
    # The recommended_offset_for helper should agree with the JSON.
    assert rep.recommended_offset_for("ibm_x") == parsed["per_backend"][0]["shrunk_offset"]
    assert rep.recommended_offset_for("never_seen") is None


def test_report_markdown_contains_key_fields():
    records = _make_backend_records("ibm_fez", true_offset=-0.13, n=5, sigma=0.01)
    rep = BackendAwareOffsetEstimator().fit(records)
    md = rep.to_markdown()
    for needle in [
        "# Backend-Aware Offset Report",
        "Total samples:",
        "Global offset",
        "Shrinkage prior n",
        "| Backend | n | mean offset | std offset | weight | shrunk offset |",
        "`ibm_fez`",
    ]:
        assert needle in md, f"Markdown missing fragment: {needle!r}"


def test_empty_records_raises():
    with pytest.raises(ValueError):
        BackendAwareOffsetEstimator().fit([])


def test_records_missing_fields_are_skipped():
    records = [
        _make_record("ibm_ok", measured=0.6, predicted=0.7),
        {"job_id": "broken", "backend": "ibm_ok"},  # missing measured/predicted
        {"job_id": "broken2", "backend": "ibm_ok", "measured_phi": "not_a_number"},
        _make_record("ibm_ok", measured=0.65, predicted=0.75),
    ]
    rep = BackendAwareOffsetEstimator().fit(records)
    assert rep.total_samples == 2  # the two good records


# ---------- CLI ----------


def test_cli_smoke_against_real_report():
    """End-to-end CLI run against the existing quantum_calibration_report.json."""
    report_path = REPO_ROOT / "quantum_calibration_report.json"
    if not report_path.exists():
        pytest.skip("quantum_calibration_report.json not present")
    result = subprocess.run(
        [sys.executable, "-m", "backend_aware_offset", "--report", str(report_path)],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, f"CLI failed: {result.stderr}"
    assert "Backend-Aware Offset Report" in result.stdout
    assert "| Backend | n |" in result.stdout


def test_cli_missing_report_returns_nonzero():
    result = subprocess.run(
        [sys.executable, "-m", "backend_aware_offset", "--report", "/nonexistent.json"],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode != 0
    assert "ERROR" in result.stderr


def test_cli_quiet_suppresses_markdown(tmp_path: Path):
    report_path = REPO_ROOT / "quantum_calibration_report.json"
    if not report_path.exists():
        pytest.skip("quantum_calibration_report.json not present")
    md_out = tmp_path / "out.md"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "backend_aware_offset",
            "--report",
            str(report_path),
            "--markdown-out",
            str(md_out),
            "--quiet",
        ],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    assert result.stdout == ""  # quiet suppresses
    assert md_out.exists() and md_out.read_text(encoding="utf-8").startswith("#")