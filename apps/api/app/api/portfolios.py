from fastapi import APIRouter

router = APIRouter()

@router.get("/{experiment_id}")
def portfolio(experiment_id: str) -> dict:
    return {"experiment_id": experiment_id, "initial_value": 10_000_000, "cumulative_return": .246, "sharpe": 1.42, "max_drawdown": -.118, "positions": 10}

@router.get("/{experiment_id}/holdings")
def holdings(experiment_id: str) -> dict:
    return {"experiment_id": experiment_id, "items": [{"ticker": "DANGCEM", "weight": .10, "score": 1.84}, {"ticker": "BUACEMENT", "weight": .10, "score": 1.72}, {"ticker": "SEPLAT", "weight": .10, "score": 1.64}]}

@router.get("/{experiment_id}/performance")
def performance(experiment_id: str) -> dict:
    return {"experiment_id": experiment_id, "items": [], "benchmark": "NGX ASI"}