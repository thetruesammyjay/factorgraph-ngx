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
    if factor in {"size", "value"}:
        report = load_pilot_report()
        portfolios = report.get("characteristic_portfolios", {})
        return {
            "factor": factor,
            "status": item["status"],
            "items": portfolios.get("performance", []),
            "dataset_version": report["experiment_id"],
            "coverage": portfolios.get("coverage"),
        }
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
        "items": report["market_factor"],
        "dataset_version": report["experiment_id"],
    }


@router.get("/{factor}/statistics")
def factor_statistics(factor: str) -> dict:
    item = get_factor_or_404(factor)
    report = load_pilot_report()
    if factor == "market" and item["status"] == "eligible":
        return {
            **item,
            "statistics": report["market_factor_statistics"],
            "reason": None,
        }
    if factor in {"size", "value"}:
        portfolio = report.get("characteristic_portfolios", {}).get("factors", {}).get(factor)
        if portfolio:
            return {
                **item,
                "statistics": portfolio["statistics"],
                "reason": "computed from partial point-in-time coverage; factor gate remains preliminary",
            }
    return {
        **item,
        "statistics": None,
        "reason": "inferential statistics are unavailable until the factor gate passes",
    }


@router.get("/{factor}/regression")
def factor_regression(factor: str) -> dict:
    """Return HAC regression diagnostics for a computed pilot factor."""
    item = get_factor_or_404(factor)
    report = load_pilot_report()
    regression = report.get("factor_regressions", {}).get(factor)
    if regression is None:
        return {
            **item,
            "regression": None,
            "reason": "regression diagnostics are unavailable for this factor",
        }
    return {
        **item,
        "regression": regression,
        "dataset_version": report["experiment_id"],
    }


@router.get("/{factor}/characteristics")
def factor_characteristics(factor: str, latest: bool = True) -> dict:
    item = get_factor_or_404(factor)
    if factor not in {"size", "value"}:
        raise HTTPException(
            status_code=400,
            detail="characteristic snapshots are available only for Size and Value",
        )
    report = load_pilot_report()
    source = report["latest_characteristics"] if latest else report["characteristics"]
    eligibility_field = f"{factor}_eligible"
    return {
        "factor": factor,
        "status": item["status"],
        "latest": latest,
        "coverage": report["characteristic_coverage"],
        "items": [row for row in source if row[eligibility_field]],
        "excluded": [row for row in source if not row[eligibility_field]],
        "dataset_version": report["experiment_id"],
    }
