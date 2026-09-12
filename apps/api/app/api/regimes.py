from fastapi import APIRouter

router = APIRouter()

@router.get("")
def list_regimes() -> dict:
    return {"items": [{"state": 0, "label": "stable market", "probability": .71, "mean_return": .0184, "volatility": .032}, {"state": 1, "label": "expansionary market", "probability": .19, "mean_return": .0311, "volatility": .058}, {"state": 2, "label": "high-volatility stress", "probability": .10, "mean_return": -.0462, "volatility": .117}], "model": "GaussianHMM", "state_count": 3}

@router.get("/timeline")
def timeline() -> dict:
    return {"items": [], "dataset_version": "ngx_monthly_v3"}

@router.get("/statistics")
def statistics() -> dict:
    return list_regimes()