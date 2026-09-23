"""Experiment configuration and deterministic pilot-result endpoints."""

import json
from datetime import UTC, datetime
from uuid import uuid4

from fastapi import APIRouter, HTTPException

from app.data.experiment_reports import load_pilot_report
from app.schemas.models import ExperimentCreate, ExperimentResponse

router = APIRouter()
_EXPERIMENTS: list[dict] = []


@router.get("")
def list_experiments() -> dict:
    return {"items": _EXPERIMENTS, "total": len(_EXPERIMENTS)}


@router.post("", response_model=ExperimentResponse, status_code=201)
def create_experiment(payload: ExperimentCreate) -> ExperimentResponse:
    item = {
        "id": f"exp_{uuid4().hex[:8].upper()}",
        "status": "draft",
        "dataset_version": "unassigned",
        "created_at": datetime.now(UTC),
        "completed_at": None,
        "git_commit": None,
        **payload.model_dump(),
    }
    _EXPERIMENTS.insert(0, item)
    return ExperimentResponse(**item)


@router.get("/pilot/latest")
def latest_pilot_experiment() -> dict:
    try:
        return load_pilot_report()
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.get("/{experiment_id}")
def get_experiment(experiment_id: str) -> dict:
    return next(
        (item for item in _EXPERIMENTS if item["id"] == experiment_id),
        {"id": experiment_id, "status": "not_found"},
    )


@router.post("/{experiment_id}/run")
def run_experiment(experiment_id: str) -> dict:
    return {
        "experiment_id": experiment_id,
        "status": "queued",
        "message": "Research graph execution queued.",
    }
