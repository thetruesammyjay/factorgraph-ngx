"""Experiment configuration and deterministic pilot-result endpoints."""

import json
from datetime import UTC, datetime
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from sqlalchemy.exc import SQLAlchemyError

from app.data.experiment_reports import load_pilot_report
from app.db import experiment_repository
from app.graph.nodes import NODE_ORDER
from app.schemas.models import ExperimentCreate, ExperimentResponse
from app.services.experiments import (
    build_experiment_plan,
    execute_experiment,
    stable_experiment_config,
)

router = APIRouter()
_EXPERIMENTS: list[dict] = []
_RUN_METADATA_FIELDS = {
    "id",
    "name",
    "status",
    "dataset_version",
    "created_at",
    "completed_at",
    "git_commit",
    "execution_trace",
    "node_outputs",
    "constraints",
    "run_fingerprint",
    "last_completed_node",
    "errors",
}


def _database_unavailable() -> HTTPException:
    return HTTPException(status_code=503, detail="Experiment database is unavailable")


def _all_experiments() -> list[dict]:
    if not experiment_repository.database_enabled():
        return _EXPERIMENTS
    try:
        return experiment_repository.list_experiments()
    except SQLAlchemyError as exc:
        raise _database_unavailable() from exc


def _find_experiment(experiment_id: str) -> dict | None:
    if not experiment_repository.database_enabled():
        return next((item for item in _EXPERIMENTS if item["id"] == experiment_id), None)
    try:
        return experiment_repository.get_experiment(experiment_id)
    except SQLAlchemyError as exc:
        raise _database_unavailable() from exc


@router.get("")
def list_experiments() -> dict:
    items = _all_experiments()
    return {"items": items, "total": len(items)}


@router.post("", response_model=ExperimentResponse, status_code=201)
def create_experiment(payload: ExperimentCreate) -> ExperimentResponse:
    item = {
        "id": str(uuid4()),
        "status": "draft",
        "dataset_version": "unassigned",
        "created_at": datetime.now(UTC),
        "completed_at": None,
        "git_commit": None,
        "execution_trace": [],
        "node_outputs": {},
        "constraints": [],
        "run_fingerprint": None,
        "last_completed_node": None,
        "errors": [],
        **payload.model_dump(mode="json"),
    }
    if experiment_repository.database_enabled():
        try:
            item = experiment_repository.create_experiment(item)
        except SQLAlchemyError as exc:
            raise _database_unavailable() from exc
    else:
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
    item = _find_experiment(experiment_id)
    return item or {"id": experiment_id, "status": "not_found"}


@router.get("/{experiment_id}/run")
def latest_experiment_run(experiment_id: str) -> dict:
    item = _find_experiment(experiment_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Experiment not found")
    return {
        "experiment_id": experiment_id,
        "status": item["status"],
        "dataset_version": item.get("dataset_version"),
        "last_completed_node": item.get("last_completed_node"),
        "execution_trace": item.get("execution_trace", []),
        "node_outputs": item.get("node_outputs", {}),
        "constraints": item.get("constraints", []),
        "run_fingerprint": item.get("run_fingerprint"),
        "errors": item.get("errors", []),
    }


@router.get("/{experiment_id}/plan")
def experiment_plan(experiment_id: str) -> dict:
    item = _find_experiment(experiment_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Experiment not found")
    try:
        report = load_pilot_report()
    except (FileNotFoundError, json.JSONDecodeError, ValueError) as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return {
        "experiment_id": experiment_id,
        "name": item.get("name"),
        "configuration": stable_experiment_config(item),
        **build_experiment_plan(item, report),
    }


@router.get("/{experiment_id}/manifest")
def experiment_manifest(experiment_id: str) -> dict:
    item = _find_experiment(experiment_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Experiment not found")
    trace = item.get("execution_trace", [])
    return {
        "experiment_id": experiment_id,
        "name": item.get("name"),
        "status": item.get("status"),
        "dataset_version": item.get("dataset_version"),
        "run_fingerprint": item.get("run_fingerprint"),
        "configuration": {
            key: value for key, value in item.items() if key not in _RUN_METADATA_FIELDS
        },
        "constraints": item.get("constraints", []),
        "execution": {
            "node_count": len(trace),
            "last_completed_node": item.get("last_completed_node"),
            "nodes": [
                {"sequence": node.get("sequence"), "node": node.get("node"), "status": node.get("status")}
                for node in trace
            ],
        },
    }


@router.get("/{experiment_id}/export")
def export_experiment(experiment_id: str) -> dict:
    manifest = experiment_manifest(experiment_id)
    run = latest_experiment_run(experiment_id)
    provenance = run.get("node_outputs", {}).get("persist_results", {}).get("dataset_provenance")
    return {
        "schema_version": 1,
        "exported_at": datetime.now(UTC),
        "experiment": manifest,
        "run": run,
        "dataset_provenance": provenance,
        "provenance_status": "captured_at_run" if provenance else "not_captured_for_this_run",
    }


@router.get("/{experiment_id}/run/nodes/{node_name}")
def experiment_node_run(experiment_id: str, node_name: str) -> dict:
    item = _find_experiment(experiment_id)
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
        "sequence": trace.get("sequence"),
        "status": trace.get("status"),
        "outputs": trace.get("outputs", {}),
    }


@router.post("/{experiment_id}/run")
def run_experiment(experiment_id: str) -> dict:
    item = _find_experiment(experiment_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Experiment not found")
    state = execute_experiment(experiment_id, item)
    updates = {
        "status": state["status"],
        "dataset_version": state.get("dataset_version", "unassigned"),
        "completed_at": datetime.now(UTC)
        if state["status"] in {"completed", "completed_with_constraints"}
        else None,
        "execution_trace": state.get("execution_trace", []),
        "node_outputs": state.get("node_outputs", {}),
        "constraints": state.get("constraints", []),
        "run_fingerprint": state.get("run_fingerprint"),
        "last_completed_node": state.get("last_completed_node"),
        "errors": state.get("errors", []),
    }
    item.update(updates)
    if experiment_repository.database_enabled():
        try:
            item = experiment_repository.update_experiment(experiment_id, updates) or item
        except SQLAlchemyError as exc:
            raise _database_unavailable() from exc
    return {
        "experiment_id": experiment_id,
        "status": state["status"],
        "message": (
            "Research graph execution completed."
            if state["status"] == "completed"
            else "Research graph completed with constraints."
            if state["status"] == "completed_with_constraints"
            else "Research graph execution blocked."
        ),
        "dataset_version": state.get("dataset_version"),
        "last_completed_node": state.get("last_completed_node"),
        "execution_trace": state.get("execution_trace", []),
        "node_outputs": state.get("node_outputs", {}),
        "constraints": state.get("constraints", []),
        "run_fingerprint": state.get("run_fingerprint"),
        "errors": state.get("errors", []),
    }
