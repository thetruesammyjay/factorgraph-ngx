"""Regime endpoints guarded by the latest experiment's monthly sample."""

import json
from pathlib import Path

from fastapi import APIRouter

router = APIRouter()

REPORT_PATH = Path(__file__).resolve().parents[1] / "data" / "reports" / "pilot-latest.json"


def blocked_context() -> tuple[str, str]:
    report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    months = report.get("market_input_coverage", {}).get("aligned_months", 0)
    reason = (
        f"The current experiment has only {months} monthly endpoints; a multi-state "
        "regime model requires at least 36 observations for this pilot."
    )
    return report["experiment_id"], reason


@router.get("")
def list_regimes() -> dict:
    _, reason = blocked_context()
    return {"status": "blocked", "items": [], "model": None, "reason": reason}


@router.get("/timeline")
def timeline() -> dict:
    dataset_version, reason = blocked_context()
    return {
        "status": "blocked",
        "items": [],
        "dataset_version": dataset_version,
        "reason": reason,
    }


@router.get("/statistics")
def statistics() -> dict:
    return list_regimes()
