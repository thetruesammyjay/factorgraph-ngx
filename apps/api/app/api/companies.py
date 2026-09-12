from fastapi import APIRouter, HTTPException

router = APIRouter()
COMPANIES = [
    {"ticker": "DANGCEM", "name": "Dangote Cement", "sector": "Industrials", "active": True},
    {"ticker": "BUACEMENT", "name": "BUA Cement", "sector": "Industrials", "active": True},
    {"ticker": "SEPLAT", "name": "Seplat Energy", "sector": "Energy", "active": True},
    {"ticker": "MTNN", "name": "MTN Nigeria", "sector": "Telecoms", "active": True},
    {"ticker": "GTCO", "name": "Guaranty Trust Holding", "sector": "Financials", "active": True},
]

@router.get("")
def list_companies() -> dict:
    return {"items": COMPANIES, "total": 183, "source": "demo_seed"}

@router.get("/{ticker}")
def get_company(ticker: str) -> dict:
    company = next((item for item in COMPANIES if item["ticker"] == ticker.upper()), None)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company

@router.get("/{ticker}/prices")
def get_prices(ticker: str) -> dict:
    return {"ticker": ticker.upper(), "items": [], "note": "Load validated NGX price observations to populate this series."}

@router.get("/{ticker}/fundamentals")
def get_fundamentals(ticker: str) -> dict:
    return {"ticker": ticker.upper(), "items": [], "note": "Load point-in-time aligned fundamentals to populate this series."}