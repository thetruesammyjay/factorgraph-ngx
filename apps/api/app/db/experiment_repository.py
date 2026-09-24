"""Persistence helpers for saved research experiments and graph runs."""

from uuid import UUID

from sqlalchemy import select

from app.db.models import Experiment
from app.db.session import SessionLocal


def database_enabled() -> bool:
    return SessionLocal is not None


def _as_dict(record: Experiment) -> dict:
    return {
        **record.config,
        "id": str(record.id),
        "name": record.name,
        "status": record.status,
        "dataset_version": record.dataset_version,
        "created_at": record.created_at,
        "completed_at": record.completed_at,
        "git_commit": None,
        "execution_trace": record.execution_trace or [],
        "node_outputs": record.node_outputs or {},
        "constraints": record.constraints or [],
        "run_fingerprint": record.run_fingerprint,
        "last_completed_node": record.last_completed_node,
        "errors": record.errors or [],
    }


def list_experiments() -> list[dict]:
    if SessionLocal is None:
        raise RuntimeError("Database repository is not enabled")
    with SessionLocal() as session:
        records = session.scalars(select(Experiment).order_by(Experiment.created_at.desc()))
        return [_as_dict(record) for record in records]


def get_experiment(experiment_id: str) -> dict | None:
    if SessionLocal is None:
        raise RuntimeError("Database repository is not enabled")
    try:
        record_id = UUID(experiment_id)
    except ValueError:
        return None
    with SessionLocal() as session:
        record = session.get(Experiment, record_id)
        return _as_dict(record) if record else None


def create_experiment(item: dict) -> dict:
    if SessionLocal is None:
        raise RuntimeError("Database repository is not enabled")
    config_fields = {
        key: value
        for key, value in item.items()
        if key
        not in {
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
    }
    record = Experiment(
        id=UUID(item["id"]),
        name=item["name"],
        config=config_fields,
        status=item["status"],
        dataset_version=item["dataset_version"],
        created_at=item["created_at"],
    )
    with SessionLocal() as session:
        session.add(record)
        session.commit()
        session.refresh(record)
        return _as_dict(record)


def update_experiment(experiment_id: str, updates: dict) -> dict | None:
    if SessionLocal is None:
        raise RuntimeError("Database repository is not enabled")
    try:
        record_id = UUID(experiment_id)
    except ValueError:
        return None
    with SessionLocal() as session:
        record = session.get(Experiment, record_id)
        if record is None:
            return None
        for key in (
            "status",
            "dataset_version",
            "completed_at",
            "execution_trace",
            "node_outputs",
            "constraints",
            "run_fingerprint",
            "last_completed_node",
            "errors",
        ):
            if key in updates:
                setattr(record, key, updates[key])
        session.commit()
        session.refresh(record)
        return _as_dict(record)
