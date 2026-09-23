"""Experiment configuration and deterministic pilot-result endpoints."""

import json
from datetime import UTC, datetime
from uuid import uuid4

from fastapi import APIRouter, HTTPException

from app.data.experiment_reports import load_pilot_report
from app.graph.nodes import NODE_ORDER
from app.schemas.models import ExperimentCreate, ExperimentResponse
from app.services.experiments import execute_experiment

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
        "execution_trace": [],
        "node_outputs": {},
        "last_completed_node": None,
        "errors": [],
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


@router.get("/{experiment_id}/run")
def latest_experiment_run(experiment_id: str) -> dict:
    item = next((item for item in _EXPERIMENTS if item["id"] == experiment_id), None)
    if item is None:
        raise HTTPException(status_code=404, detail="Experiment not found")
    return {
        "experiment_id": experiment_id,
        "status": item["status"],
        "dataset_version": item.get("dataset_version"),
        "last_completed_node": item.get("last_completed_node"),
        "execution_trace": item.get("execution_trace", []),
        "node_outputs": item.get("node_outputs", {}),
        "errors": item.get("errors", []),
    }


@router.get("/{experiment_id}/run/nodes/{node_name}")
def experiment_node_run(experiment_id: str, node_name: str) -> dict:
    item = next((item for item in _EXPERIMENTS if item["id"] == experiment_id), None)
    if item is None:
        raise HTTPException(status_code=404, detail="Experiment not found")
    if node_name not in NODE_ORDER:
        raise HTTPException(status_code=404, detail="Research graph node not found")
    trace = next(
        (entry for entry in item.get("execution_trace", []) if entry.get("node") == node_name),
        None,
    )
    if trace is None:
        raise HTTPException(status_code=404, detail="Node has not run")
    return {
        "experiment_id": experiment_id,
        "node": node_name,
        "status": trace.get("status"),
        "outputs": trace.get("outputs", {}),
    }


@router.post("/{experiment_id}/run")
def run_experiment(experiment_id: str) -> dict:
    item = next((item for item in _EXPERIMENTS if item["id"] == experiment_id), None)
    if item is None:
        raise HTTPException(status_code=404, detail="Experiment not found")
    state = execute_experiment(experiment_id, item)
    item.update(
        {
            "status": state["status"],
            "dataset_version": state.get("dataset_version", "unassigned"),
            "completed_at": datetime.now(UTC) if state["status"] == "completed" else None,
            "execution_trace": state.get("execution_trace", []),
            "node_outputs": state.get("node_outputs", {}),
            "last_completed_node": state.get("last_completed_node"),
            "errors": state.get("errors", []),
        }
    )
    return {
        "experiment_id": experiment_id,
        "status": state["status"],
        "message": (
            "Research graph execution completed."
            if state["status"] == "completed"
            else "Research graph execution blocked."
        ),
        "dataset_version": state.get("dataset_version"),
        "last_completed_node": state.get("last_completed_node"),
        "execution_trace": state.get("execution_trace", []),
        "node_outputs": state.get("node_outputs", {}),
        "errors": state.get("errors", []),
    }
