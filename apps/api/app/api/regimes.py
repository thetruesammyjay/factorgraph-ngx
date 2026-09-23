"""Regime endpoints guarded by the available monthly sample."""

from fastapi import APIRouter

router = APIRouter()

BLOCKED_REASON = (
    "The 2024 pilot has only 12 monthly endpoints; a multi-state regime model "
    "would not be statistically defensible."
)


@router.get("")
def list_regimes() -> dict:
    return {"status": "blocked", "items": [], "model": None, "reason": BLOCKED_REASON}


@router.get("/timeline")
def timeline() -> dict:
    return {
        "status": "blocked",
        "items": [],
        "dataset_version": "ngx-public-data-2024-pilot-v1",
        "reason": BLOCKED_REASON,
    }


@router.get("/statistics")
def statistics() -> dict:
    return list_regimes()
