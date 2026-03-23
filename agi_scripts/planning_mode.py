from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class PlanningReport:
    agent: str
    objective: str
    generated_at: str
    planning_mode: bool
    current_state: dict[str, Any]
    goals: list[str]
    strategies: list[dict[str, Any]]
    evaluation_metrics: list[str]
    coordination: dict[str, Any]
    risks: list[str]
    next_actions: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def write_planning_report(
    *,
    output_dir: Path,
    prefix: str,
    report: PlanningReport,
) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    filename = (
        f"{prefix}_planning_report_"
        f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )
    path = output_dir / filename
    with path.open("w", encoding="utf-8") as handle:
        json.dump(report.to_dict(), handle, indent=2)
    return path