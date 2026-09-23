"""Portfolio endpoints backed by the deterministic momentum pilot."""

import json

from fastapi import APIRouter, HTTPException

from app.data.experiment_reports import load_pilot_report

router = APIRouter()


def load_portfolio(experiment_id: str) -> tuple[dict, dict]:
    try:
        report = load_pilot_report()
        if report["experiment_id"] != experiment_id:
            raise HTTPException(status_code=404, detail="Experiment not found")
        return report, report["momentum_portfolio"]
    except (FileNotFoundError, json.JSONDecodeError, KeyError) as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.get("/{experiment_id}")
def portfolio(experiment_id: str) -> dict:
    report, result = load_portfolio(experiment_id)
    return {
        "experiment_id": report["experiment_id"],
        "status": result["status"],
        "methodology": result["methodology"],
        "coverage": result["coverage"],
        "statistics": result["statistics"],
    }


@router.get("/{experiment_id}/holdings")
def holdings(experiment_id: str) -> dict:
    report, result = load_portfolio(experiment_id)
    return {
        "experiment_id": report["experiment_id"],
        "status": result["status"],
        "items": result["holdings"],
    }


@router.get("/{experiment_id}/performance")
def performance(experiment_id: str) -> dict:
    report, result = load_portfolio(experiment_id)
    return {
        "experiment_id": report["experiment_id"],
        "status": result["status"],
        "items": result["performance"],
        "benchmark": "NGX ASI weekly-close monthly sample",
    }
