"""Regime endpoints backed by the latest experiment's deterministic analysis."""

import json

from fastapi import APIRouter

from app.data.experiment_reports import load_pilot_report

router = APIRouter()


def blocked_context() -> tuple[str, str]:
    report = load_pilot_report()
    analysis = report.get("regime_analysis", {})
    return report["experiment_id"], analysis.get("reason", "regime analysis is unavailable")


def regime_report() -> dict:
    try:
        return load_pilot_report().get("regime_analysis", {})
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


@router.get("")
def list_regimes() -> dict:
    report = regime_report()
    return {
        "status": report.get("status", "blocked"),
        "items": report.get("statistics", []),
        "model": report.get("model"),
        "coverage": report.get("coverage"),
        "reason": report.get("reason"),
    }


@router.get("/timeline")
def timeline() -> dict:
    report = regime_report()
    dataset_version, reason = blocked_context()
    return {
        "status": report.get("status", "blocked"),
        "items": report.get("timeline", []),
        "dataset_version": dataset_version,
        "coverage": report.get("coverage"),
        "reason": reason,
    }


@router.get("/statistics")
def statistics() -> dict:
    return list_regimes()
