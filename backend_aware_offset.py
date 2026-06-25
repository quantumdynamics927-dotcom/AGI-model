"""Backend-aware offset estimation for AGI-model quantum calibration.

Milestone 0 of the Quantum AGI roadmap (see ``docs/QUANTUM_AGI_ROADMAP.md``).

The existing ``quantum_calibration_framework.py`` fits a single systematic
offset against the full pool of hardware validation results. That works for
the current five-job ``ibm_fez`` batch, but it does not answer the next
scientific question the README calls out:

    Is the offset backend-specific, and can it transfer?

This module adds a per-backend offset estimator on top of the existing
``QuantumHardwareCalibrator``. The key design choice is **shrinkage**: a
backend with very few samples (e.g. one job) is pulled hard toward the
global mean, while a backend with many samples keeps its own estimate.
The shrinkage weight follows a James-Stein-flavored rule::

    w_backend = n / (n + shrinkage_prior_n)

so a backend with ``n == shrinkage_prior_n`` samples keeps only half its
estimate. The prior is configurable; the default ``shrinkage_prior_n = 5``
matches the "3-5 replicates per promoter" guidance already in the README.

The estimator is deliberately small:

* No new external dependencies beyond numpy.
* Reads the existing ``quantum_calibration_report.json`` shape.
* Emits both a JSON-serializable report and a Markdown table.

CLI usage::

    python -m backend_aware_offset --report quantum_calibration_report.json

The module is intentionally decoupled from ``quantum_calibration_framework.py``
so it can be imported without dragging in Qiskit and friends.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence

import numpy as np


# ---------- Data shapes ----------


@dataclass
class BackendCalibrationModel:
    """Per-backend offset summary.

    Attributes:
        backend: Backend identifier (e.g. ``"ibm_fez"``).
        sample_count: Number of validation results for this backend.
        mean_offset: Mean ``measured_phi - predicted_phi`` for this backend.
        std_offset: Sample standard deviation of the per-job offsets.
        shrinkage_weight: ``n / (n + shrinkage_prior_n)``. A weight of 1.0
            means the per-backend estimate is reported unmodified; a weight
            near 0.0 means the global estimate dominates.
        shrunk_offset: ``shrinkage_weight * mean_offset + (1 - shrinkage_weight) * global_offset``.
        last_updated: ISO-8601 UTC timestamp.
    """

    backend: str
    sample_count: int
    mean_offset: float
    std_offset: float
    shrinkage_weight: float
    shrunk_offset: float
    last_updated: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class BackendAwareOffsetReport:
    """Top-level report produced by ``BackendAwareOffsetEstimator``.

    Attributes:
        generated: ISO-8601 UTC timestamp at the moment the report was built.
        source_report_path: Path of the input ``quantum_calibration_report.json``
            (or ``None`` if built in-memory from a list of records).
        total_samples: Total number of validation results used.
        global_offset: Unweighted mean of all ``measured_phi - predicted_phi``
            values across backends. This is the offset the legacy calibrator
            would have reported.
        global_std: Sample standard deviation of all offsets.
        shrinkage_prior_n: The ``n`` used for the James-Stein-style prior.
        per_backend: One ``BackendCalibrationModel`` per backend, sorted by
            ``sample_count`` descending.
        recommended_offset_for: Convenience lookup: ``backend -> shrunk_offset``.
    """

    generated: str
    source_report_path: Optional[str]
    total_samples: int
    global_offset: float
    global_std: float
    shrinkage_prior_n: float
    per_backend: List[BackendCalibrationModel]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "generated": self.generated,
            "source_report_path": self.source_report_path,
            "total_samples": self.total_samples,
            "global_offset": self.global_offset,
            "global_std": self.global_std,
            "shrinkage_prior_n": self.shrinkage_prior_n,
            "per_backend": [m.to_dict() for m in self.per_backend],
        }

    def recommended_offset_for(self, backend: str) -> Optional[float]:
        for m in self.per_backend:
            if m.backend == backend:
                return m.shrunk_offset
        return None

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, sort_keys=False)

    def to_markdown(self) -> str:
        lines = [
            "# Backend-Aware Offset Report",
            "",
            f"Generated: `{self.generated}`",
            f"Source report: `{self.source_report_path or '(in-memory)'}`",
            f"Total samples: **{self.total_samples}**",
            f"Global offset (legacy): **{self.global_offset:+.4f}** "
            f"(std {self.global_std:.4f})",
            f"Shrinkage prior n: **{self.shrinkage_prior_n:g}**",
            "",
            "| Backend | n | mean offset | std offset | weight | shrunk offset |",
            "|---|---:|---:|---:|---:|---:|",
        ]
        for m in self.per_backend:
            lines.append(
                f"| `{m.backend}` | {m.sample_count} | "
                f"{m.mean_offset:+.4f} | {m.std_offset:.4f} | "
                f"{m.shrinkage_weight:.2f} | **{m.shrunk_offset:+.4f}** |"
            )
        lines.append("")
        lines.append(
            "Notes:"
        )
        lines.append(
            "  - `weight = n / (n + shrinkage_prior_n)` (James-Stein-style prior)."
        )
        lines.append(
            "  - `shrunk_offset = weight * mean_offset + (1 - weight) * global_offset`."
        )
        lines.append(
            "  - When n is small, the per-backend estimate is pulled toward the"
            " global offset, preventing a single job from dominating the report."
        )
        lines.append("")
        return "\n".join(lines)


# ---------- Estimator ----------


class BackendAwareOffsetEstimator:
    """Fit a per-backend offset, with shrinkage toward the global mean.

    Parameters:
        shrinkage_prior_n: Effective sample size of the prior. A backend with
            ``n == shrinkage_prior_n`` samples keeps only half its estimate.
            The default (``5``) matches the README's "3-5 replicates per
            promoter" guidance.
    """

    def __init__(self, shrinkage_prior_n: float = 5.0) -> None:
        if shrinkage_prior_n < 0:
            raise ValueError("shrinkage_prior_n must be >= 0")
        self.shrinkage_prior_n = float(shrinkage_prior_n)

    # ---- raw record ingestion ----

    @staticmethod
    def _aligned_arrays(
        records: Sequence[Dict[str, Any]],
    ) -> tuple[np.ndarray, np.ndarray]:
        """Build parallel ``(offset, backend)`` arrays from records.

        Records that lack ``measured_phi`` or ``predicted_phi`` (or have
        non-numeric values) are silently skipped; ``backend`` falls back to
        ``"unknown"`` when missing. Both arrays have the same length.
        """
        offsets: List[float] = []
        backends: List[str] = []
        for r in records:
            try:
                measured = float(r["measured_phi"])
                predicted = float(r["predicted_phi"])
            except (KeyError, TypeError, ValueError):
                continue
            backend = r.get("backend") or "unknown"
            offsets.append(measured - predicted)
            backends.append(str(backend))
        return (
            np.asarray(offsets, dtype=float),
            np.asarray(backends, dtype=object),
        )

    @staticmethod
    def offsets_from_records(records: Sequence[Dict[str, Any]]) -> np.ndarray:
        """Pull ``measured_phi - predicted_phi`` from each record.

        Records are expected to be the per-job entries inside
        ``quantum_calibration_report.json['results']``. Records without
        ``measured_phi`` or ``predicted_phi`` keys are silently skipped.
        """
        offsets, _ = BackendAwareOffsetEstimator._aligned_arrays(records)
        return offsets

    @staticmethod
    def backends_from_records(records: Sequence[Dict[str, Any]]) -> np.ndarray:
        """Pull the backend label from each record (or ``"unknown"`` if absent)."""
        _, backends = BackendAwareOffsetEstimator._aligned_arrays(records)
        return backends

    # ---- core fit ----

    def fit(
        self,
        records: Sequence[Dict[str, Any]],
        source_report_path: Optional[str] = None,
    ) -> BackendAwareOffsetReport:
        offsets = self.offsets_from_records(records)
        backends = self.backends_from_records(records)
        if offsets.size == 0:
            raise ValueError("No usable records (need measured_phi + predicted_phi).")

        global_offset = float(np.mean(offsets))
        # ddof=1 so the std matches what a human would compute by hand.
        global_std = float(np.std(offsets, ddof=1)) if offsets.size > 1 else 0.0

        unique_backends = sorted(set(backends.tolist()))
        models: List[BackendCalibrationModel] = []
        for backend in unique_backends:
            mask = backends == backend
            n = int(mask.sum())
            backend_offsets = offsets[mask]
            mean_offset = float(np.mean(backend_offsets))
            std_offset = (
                float(np.std(backend_offsets, ddof=1)) if n > 1 else 0.0
            )
            weight = n / (n + self.shrinkage_prior_n) if self.shrinkage_prior_n > 0 else 1.0
            shrunk = weight * mean_offset + (1.0 - weight) * global_offset
            models.append(
                BackendCalibrationModel(
                    backend=backend,
                    sample_count=n,
                    mean_offset=mean_offset,
                    std_offset=std_offset,
                    shrinkage_weight=weight,
                    shrunk_offset=shrunk,
                )
            )

        # Sort by sample_count desc, then by backend name for stability.
        models.sort(key=lambda m: (-m.sample_count, m.backend))

        return BackendAwareOffsetReport(
            generated=datetime.now(timezone.utc).isoformat(),
            source_report_path=source_report_path,
            total_samples=int(offsets.size),
            global_offset=global_offset,
            global_std=global_std,
            shrinkage_prior_n=self.shrinkage_prior_n,
            per_backend=models,
        )

    # ---- convenience ----

    @classmethod
    def fit_from_json(
        cls,
        path: Path,
        shrinkage_prior_n: float = 5.0,
    ) -> BackendAwareOffsetReport:
        """Read a ``quantum_calibration_report.json`` and fit offsets.

        The expected shape is the v2.0 schema produced by
        ``quantum_calibration_framework.generate_calibration_report``.
        """
        with open(path, "r", encoding="utf-8") as f:
            report = json.load(f)
        records = report.get("results") or []
        estimator = cls(shrinkage_prior_n=shrinkage_prior_n)
        return estimator.fit(records, source_report_path=str(path))


# ---------- CLI ----------


def _build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="backend_aware_offset",
        description=(
            "Estimate per-backend offsets with shrinkage toward the global "
            "mean. Reads a quantum_calibration_report.json (v2.0 schema) "
            "and prints a Markdown table to stdout."
        ),
    )
    p.add_argument(
        "--report",
        type=Path,
        required=True,
        help="Path to quantum_calibration_report.json (v2.0 schema).",
    )
    p.add_argument(
        "--shrinkage-prior-n",
        type=float,
        default=5.0,
        help="Effective sample size of the prior (default: 5).",
    )
    p.add_argument(
        "--json-out",
        type=Path,
        default=None,
        help="If set, write the JSON-serialized report to this path.",
    )
    p.add_argument(
        "--markdown-out",
        type=Path,
        default=None,
        help="If set, write the Markdown report to this path.",
    )
    p.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress the Markdown table on stdout (useful for CI logs).",
    )
    return p


def main(argv: Optional[Iterable[str]] = None) -> int:
    args = _build_arg_parser().parse_args(list(argv) if argv is not None else None)
    if not args.report.exists():
        print(f"ERROR: report file not found: {args.report}", file=sys.stderr)
        return 2
    try:
        rep = BackendAwareOffsetEstimator.fit_from_json(
            args.report, shrinkage_prior_n=args.shrinkage_prior_n
        )
    except Exception as exc:  # surface a clean error to CI
        print(f"ERROR: failed to fit: {exc}", file=sys.stderr)
        return 1

    if args.json_out is not None:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(rep.to_json(), encoding="utf-8")
    if args.markdown_out is not None:
        args.markdown_out.parent.mkdir(parents=True, exist_ok=True)
        args.markdown_out.write_text(rep.to_markdown(), encoding="utf-8")
    if not args.quiet:
        print(rep.to_markdown())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())