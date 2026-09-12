from fastapi import APIRouter, HTTPException

router = APIRouter()
FACTORS = {
    "market": {"name": "Market", "short": "MKT", "annualised_return": 14.8, "volatility": 12.1, "sharpe": 1.22, "newey_west_t": 2.84},
    "size": {"name": "Size", "short": "SMB", "annualised_return": 6.4, "volatility": 8.9, "sharpe": .72, "newey_west_t": 1.96},
    "value": {"name": "Value", "short": "HML", "annualised_return": 9.7, "volatility": 10.4, "sharpe": .93, "newey_west_t": 2.31},
    "momentum": {"name": "Momentum", "short": "MOM", "annualised_return": 18.1, "volatility": 15.7, "sharpe": 1.15, "newey_west_t": 3.08},
    "liquidity": {"name": "Liquidity", "short": "LIQ", "annualised_return": 11.3, "volatility": 9.6, "sharpe": 1.18, "newey_west_t": 2.67},
}

def get_factor_or_404(factor: str) -> dict:
    if factor not in FACTORS:
        raise HTTPException(status_code=404, detail="Factor not found")
    return {"factor": factor, **FACTORS[factor]}

@router.get("")
def list_factors() -> dict:
    return {"items": [{"factor": key, **value} for key, value in FACTORS.items()]}

@router.get("/{factor}")
def get_factor(factor: str) -> dict:
    return get_factor_or_404(factor)

@router.get("/{factor}/history")
def factor_history(factor: str) -> dict:
    get_factor_or_404(factor)
    return {"factor": factor, "items": [], "dataset_version": "ngx_monthly_v3"}

@router.get("/{factor}/statistics")
def factor_statistics(factor: str) -> dict:
    return get_factor_or_404(factor)