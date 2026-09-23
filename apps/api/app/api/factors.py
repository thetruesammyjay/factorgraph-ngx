"""Factor eligibility endpoints backed by the deterministic pilot report."""

import json

from fastapi import APIRouter, HTTPException

from app.data.experiment_reports import load_pilot_report

router = APIRouter()


def eligibility_items() -> list[dict]:
    try:
        return load_pilot_report()["factor_eligibility"]
    except (FileNotFoundError, json.JSONDecodeError, KeyError) as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


def get_factor_or_404(factor: str) -> dict:
    result = next((item for item in eligibility_items() if item["factor"] == factor), None)
    if result is None:
        raise HTTPException(status_code=404, detail="Factor not found")
    return result


@router.get("")
def list_factors() -> dict:
    return {"items": eligibility_items()}


@router.get("/{factor}")
def get_factor(factor: str) -> dict:
    return get_factor_or_404(factor)


@router.get("/{factor}/history")
def factor_history(factor: str) -> dict:
    item = get_factor_or_404(factor)
    if factor != "market":
        return {
            "factor": factor,
            "status": item["status"],
            "items": [],
            "reason": "factor-return history has not passed its data gate",
        }
    report = load_pilot_report()
    return {
        "factor": factor,
        "status": item["status"],
        "items": report["market_proxy"],
        "dataset_version": report["experiment_id"],
    }


@router.get("/{factor}/statistics")
def factor_statistics(factor: str) -> dict:
    item = get_factor_or_404(factor)
    return {
        **item,
        "statistics": None,
        "reason": "inferential statistics are unavailable until the factor gate passes",
    }
