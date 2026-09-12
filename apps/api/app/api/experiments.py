from datetime import datetime, timezone
from uuid import uuid4
from fastapi import APIRouter
from app.schemas.models import ExperimentCreate, ExperimentResponse

router = APIRouter()
_EXPERIMENTS: list[dict] = [{"id": "exp_01HXYZ", "name": "ngx-five-factor-baseline", "status": "completed", "dataset_version": "ngx_monthly_v3", "created_at": datetime(2026, 9, 11, tzinfo=timezone.utc), "completed_at": datetime(2026, 9, 11, 14, tzinfo=timezone.utc), "git_commit": None, "start_date": "2019-01-01", "end_date": "2025-12-31", "factors": ["market", "size", "value", "momentum", "liquidity"], "portfolio_method": "equal_weight", "portfolio_size": 10, "rebalance_frequency": "monthly", "regime_count": 3, "bootstrap_iterations": 10000, "newey_west_threshold": 2.5, "fundamental_availability_policy": "actual_or_fixed_lag", "fixed_reporting_lag_days": 90}]

@router.get("")
def list_experiments() -> dict:
    return {"items": _EXPERIMENTS, "total": len(_EXPERIMENTS)}

@router.post("", response_model=ExperimentResponse, status_code=201)
def create_experiment(payload: ExperimentCreate) -> ExperimentResponse:
    item = {"id": f"exp_{uuid4().hex[:8].upper()}", "status": "draft", "dataset_version": "ngx_monthly_v3", "created_at": datetime.now(timezone.utc), "completed_at": None, "git_commit": None, **payload.model_dump()}
    _EXPERIMENTS.insert(0, item)
    return ExperimentResponse(**item)

@router.get("/{experiment_id}")
def get_experiment(experiment_id: str) -> dict:
    return next((item for item in _EXPERIMENTS if item["id"] == experiment_id), {"id": experiment_id, "status": "not_found"})

@router.post("/{experiment_id}/run")
def run_experiment(experiment_id: str) -> dict:
    return {"experiment_id": experiment_id, "status": "queued", "message": "Research graph execution queued."}