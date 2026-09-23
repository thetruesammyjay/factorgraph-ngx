"""Security-universe endpoints backed by the packaged public-data pilot."""

import json

from fastapi import APIRouter, HTTPException

from app.data.experiment_reports import load_pilot_report

router = APIRouter()


def load_universe_report() -> tuple[dict, list[dict]]:
    try:
        report = load_pilot_report()
        universe = report["universe"]
        if not universe or "securities" not in universe:
            raise KeyError("universe metadata is missing")
        return report, universe["securities"]
    except (FileNotFoundError, json.JSONDecodeError, KeyError) as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


def company_or_404(ticker: str) -> tuple[dict, dict]:
    report, securities = load_universe_report()
    normalized = ticker.strip().upper()
    company = next((row for row in securities if row["ticker"] == normalized), None)
    if company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    return report, company


@router.get("")
def list_companies() -> dict:
    report, securities = load_universe_report()
    latest = {row["ticker"]: row for row in report["latest_characteristics"]}
    items = [
        {
            **company,
            "active": True,
            "price_coverage": True,
            "fundamentals_available": bool(
                latest.get(company["ticker"], {}).get("size_eligible", False)
            ),
        }
        for company in securities
    ]
    return {
        "items": items,
        "total": len(items),
        "universe_id": report["universe"]["universe_id"],
        "dataset_version": report["dataset_version"],
        "source": "validated_public_data_pilot",
    }


@router.get("/{ticker}")
def get_company(ticker: str) -> dict:
    report, company = company_or_404(ticker)
    latest = next(
        (
            row
            for row in report["latest_characteristics"]
            if row["ticker"] == company["ticker"]
        ),
        None,
    )
    return {**company, "active": True, "latest_characteristics": latest}


@router.get("/{ticker}/prices")
def get_prices(ticker: str) -> dict:
    report, company = company_or_404(ticker)
    items = [
        {
            "observation_month": row["observation_month"],
            "trading_date": row["trading_date"],
            "close": row["close"],
            "marked_monthly_return": row["marked_monthly_return"],
            "official_monthly_return": row["official_monthly_return"],
        }
        for row in report["characteristics"]
        if row["ticker"] == company["ticker"]
    ]
    return {
        "ticker": company["ticker"],
        "frequency": "monthly",
        "items": items,
        "dataset_version": report["dataset_version"],
    }


@router.get("/{ticker}/fundamentals")
def get_fundamentals(ticker: str) -> dict:
    report, company = company_or_404(ticker)
    observations: dict[str, dict] = {}
    for row in report["characteristics"]:
        if row["ticker"] != company["ticker"] or not row["source_id"]:
            continue
        observations[row["source_id"]] = {
            "fiscal_period": row["fiscal_period"],
            "effective_from": row["effective_from"],
            "effective_date_source": row["effective_date_source"],
            "book_equity": row["book_equity"],
            "shares_outstanding": row["shares_outstanding"],
            "source_id": row["source_id"],
        }
    return {
        "ticker": company["ticker"],
        "items": sorted(observations.values(), key=lambda row: row["effective_from"]),
        "dataset_version": report["dataset_version"],
    }
