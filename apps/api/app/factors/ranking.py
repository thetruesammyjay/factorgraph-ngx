"""Point-in-time cross-sectional factor rankings for a selected month."""

from __future__ import annotations

import pandas as pd


def _rank_factor(
    frame: pd.DataFrame,
    *,
    characteristic: str,
    eligible_column: str,
    ascending: bool,
    portfolio_size: int,
    interpretation: str,
) -> dict:
    values = frame.copy()
    values[characteristic] = pd.to_numeric(values[characteristic], errors="coerce")
    eligible = values[
        values[eligible_column].fillna(False).astype(bool)
        & values[characteristic].notna()
    ].sort_values([characteristic, "ticker"], ascending=[ascending, True], kind="mergesort")
    rows = [
        {
            "rank": rank,
            "ticker": str(row.ticker),
            "score": float(getattr(row, characteristic)),
            "selected": rank <= portfolio_size,
        }
        for rank, row in enumerate(eligible.itertuples(index=False), start=1)
    ]
    return {
        "status": "computed" if rows else "blocked",
        "reason": None if rows else "No securities have an eligible point-in-time characteristic.",
        "characteristic": characteristic,
        "interpretation": interpretation,
        "eligible_securities": len(rows),
        "selected_securities": min(len(rows), portfolio_size),
        "rankings": rows,
    }


def build_stock_rankings(
    characteristics: pd.DataFrame,
    momentum_scores: pd.DataFrame,
    *,
    requested_factors: list[str],
    portfolio_size: int,
) -> dict:
    """Rank supported characteristics without combining incomparable scores."""
    if portfolio_size < 1:
        raise ValueError("portfolio_size must be positive")
    if characteristics.empty:
        return {
            "status": "blocked",
            "observation_month": None,
            "portfolio_size": portfolio_size,
            "factors": {
                factor: {
                    "status": "blocked",
                    "reason": "No characteristic observations are available in the selected window.",
                    "eligible_securities": 0,
                    "selected_securities": 0,
                    "rankings": [],
                }
                for factor in requested_factors
            },
        }

    frame = characteristics.copy()
    frame["ticker"] = frame["ticker"].astype(str).str.upper()
    latest_month = frame["observation_month"].astype(str).max()
    frame = frame[frame["observation_month"].astype(str) == latest_month]
    if frame["ticker"].duplicated().any():
        raise ValueError("latest characteristics contain duplicate tickers")

    factors: dict[str, dict] = {}
    for factor in requested_factors:
        if factor == "size":
            factors[factor] = _rank_factor(
                frame,
                characteristic="market_cap",
                eligible_column="size_eligible",
                ascending=True,
                portfolio_size=portfolio_size,
                interpretation="smallest market capitalization first; factor sort only",
            )
        elif factor == "value":
            factors[factor] = _rank_factor(
                frame,
                characteristic="book_to_market",
                eligible_column="value_eligible",
                ascending=False,
                portfolio_size=portfolio_size,
                interpretation="highest book-to-market first",
            )
        elif factor == "momentum":
            scores = momentum_scores.copy()
            if not scores.empty:
                scores["ticker"] = scores["ticker"].astype(str).str.upper()
                scores["formation_return"] = pd.to_numeric(
                    scores["formation_return"], errors="coerce"
                )
            eligible = scores.dropna(subset=["formation_return"]).sort_values(
                ["formation_return", "ticker"], ascending=[False, True], kind="mergesort"
            )
            rows = [
                {
                    "rank": rank,
                    "ticker": str(row.ticker),
                    "score": float(row.formation_return),
                    "selected": rank <= portfolio_size,
                }
                for rank, row in enumerate(eligible.itertuples(index=False), start=1)
            ]
            factors[factor] = {
                "status": "computed" if rows else "blocked",
                "reason": None if rows else "Momentum signal history is insufficient for the configured lookback.",
                "characteristic": "lagged_compounded_marked_return",
                "interpretation": "highest prior return after the configured skip period",
                "eligible_securities": len(rows),
                "selected_securities": min(len(rows), portfolio_size),
                "rankings": rows,
            }
        elif factor == "market":
            factors[factor] = {
                "status": "not_applicable",
                "reason": "Market is a portfolio-wide benchmark factor, not a cross-sectional security characteristic.",
                "eligible_securities": 0,
                "selected_securities": 0,
                "rankings": [],
            }
        elif factor == "liquidity":
            factors[factor] = {
                "status": "blocked",
                "reason": "The selected monthly characteristic data does not contain validated liquidity measures.",
                "eligible_securities": 0,
                "selected_securities": 0,
                "rankings": [],
            }

    statuses = [item["status"] for item in factors.values()]
    status = (
        "computed"
        if "computed" in statuses
        else "not_applicable"
        if statuses and all(item == "not_applicable" for item in statuses)
        else "blocked"
    )
    return {
        "status": status,
        "observation_month": latest_month,
        "portfolio_size": portfolio_size,
        "ranking_scope": "independent factor sorts; scores are not combined",
        "factors": factors,
    }
