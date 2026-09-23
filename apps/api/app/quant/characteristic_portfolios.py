"""Point-in-time Size and Value portfolio sorts and long-short returns."""

from __future__ import annotations

import pandas as pd

from app.quant.bootstrap import bootstrap_mean
from app.quant.statistics import describe_returns, newey_west_t_stat

REQUIRED_COLUMNS = {
    "observation_month",
    "ticker",
    "marked_monthly_return",
    "market_cap",
    "book_to_market",
    "size_eligible",
    "value_eligible",
}


def _bucket(values: pd.Series, *, ascending: bool, groups: int) -> pd.Series:
    rank = values.rank(method="first", ascending=ascending)
    return ((rank - 1) * groups // len(values)).astype(int) + 1


def _factor_statistics(values: pd.Series, *, bootstrap_iterations: int, seed: int) -> dict:
    clean = values.dropna().astype(float)
    if len(clean) < 3:
        return {
            "statistics": None,
            "newey_west_t": None,
            "bootstrap": None,
            "observations": len(clean),
        }
    lags = min(4, len(clean) - 1)
    return {
        "statistics": describe_returns(clean),
        "newey_west_t": newey_west_t_stat(clean, lags=lags),
        "newey_west_lags": lags,
        "bootstrap": bootstrap_mean(
            clean, iterations=bootstrap_iterations, seed=seed, confidence=0.95
        ),
        "observations": len(clean),
    }


def build_characteristic_portfolios(
    characteristics: pd.DataFrame,
    *,
    groups: int = 2,
    min_assets: int = 2,
    bootstrap_iterations: int = 2_000,
    seed: int = 42,
) -> dict:
    """Form portfolios at month *t* and apply them to returns in month *t+1*."""
    missing = sorted(REQUIRED_COLUMNS.difference(characteristics.columns))
    if missing:
        raise ValueError(f"characteristics missing columns: {', '.join(missing)}")
    if groups < 2:
        raise ValueError("groups must be at least two")
    if min_assets < groups:
        raise ValueError("min_assets must be at least groups")

    frame = characteristics.copy()
    frame["observation_month"] = frame["observation_month"].astype(str)
    frame["ticker"] = frame["ticker"].astype(str).str.upper()
    if frame[["observation_month", "ticker"]].duplicated().any():
        raise ValueError("characteristics contain duplicate month-ticker keys")
    frame["marked_monthly_return"] = pd.to_numeric(
        frame["marked_monthly_return"], errors="coerce"
    )
    for column in ("market_cap", "book_to_market"):
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
    months = sorted(frame["observation_month"].unique())
    rows: list[dict] = []
    holdings: list[dict] = []
    for index, formation_month in enumerate(months[:-1]):
        holding_month = months[index + 1]
        formation = frame[frame["observation_month"] == formation_month]
        holding = frame[frame["observation_month"] == holding_month].set_index("ticker")
        result = {"formation_month": formation_month, "holding_month": holding_month}
        for factor, characteristic, eligible_column, ascending, labels in (
            ("size", "market_cap", "size_eligible", True, ("small", "big")),
            ("value", "book_to_market", "value_eligible", False, ("high", "low")),
        ):
            eligible = formation[
                formation[eligible_column].astype(bool)
                & formation[characteristic].notna()
            ].copy()
            if len(eligible) < min_assets:
                result.update(
                    {
                        f"{factor}_{labels[0]}_return": None,
                        f"{factor}_{labels[1]}_return": None,
                        f"{factor}_spread_return": None,
                        f"{factor}_{labels[0]}_count": 0,
                        f"{factor}_{labels[1]}_count": 0,
                    }
                )
                continue
            eligible["bucket"] = _bucket(
                eligible[characteristic], ascending=ascending, groups=groups
            )
            low_bucket = 1
            high_bucket = groups
            bucket_names = {low_bucket: labels[0], high_bucket: labels[1]}
            group_returns: dict[str, float | None] = {}
            for bucket, label in bucket_names.items():
                members = eligible[eligible["bucket"] == bucket]
                observed = holding.reindex(members["ticker"])["marked_monthly_return"].dropna()
                group_returns[label] = float(observed.mean()) if not observed.empty else None
                result[f"{factor}_{label}_count"] = len(observed)
                for ticker in members["ticker"]:
                    holdings.append(
                        {
                            "formation_month": formation_month,
                            "holding_month": holding_month,
                            "factor": factor,
                            "ticker": ticker,
                            "portfolio": label,
                            "characteristic": float(formation.loc[formation["ticker"] == ticker, characteristic].iloc[0]),
                        }
                    )
            result[f"{factor}_{labels[0]}_return"] = group_returns[labels[0]]
            result[f"{factor}_{labels[1]}_return"] = group_returns[labels[1]]
            result[f"{factor}_spread_return"] = (
                group_returns[labels[0]] - group_returns[labels[1]]
                if group_returns[labels[0]] is not None and group_returns[labels[1]] is not None
                else None
            )
        rows.append(result)

    performance = pd.DataFrame(rows)
    if performance.empty:
        performance = pd.DataFrame(columns=["formation_month", "holding_month"])
    outputs = {}
    for factor in ("size", "value"):
        spread = performance.get(f"{factor}_spread_return", pd.Series(dtype=float))
        outputs[factor] = {
            "methodology": {
                "formation": "point-in-time characteristic observed at formation month end",
                "holding": "equal-weight marked monthly return in the following month",
                "sort": "two groups with deterministic rank tie-breaking",
                "spread": (
                    "small minus big for Size"
                    if factor == "size"
                    else "high book-to-market minus low for Value"
                ),
            },
            "statistics": _factor_statistics(
                spread, bootstrap_iterations=bootstrap_iterations, seed=seed + (1 if factor == "value" else 0)
            ),
        }
    return {
        "status": "preliminary",
        "coverage": {
            "formation_months": len(performance),
            "months_with_size_spread": int(performance.get("size_spread_return", pd.Series(dtype=float)).notna().sum()),
            "months_with_value_spread": int(performance.get("value_spread_return", pd.Series(dtype=float)).notna().sum()),
            "groups": groups,
            "minimum_assets": min_assets,
        },
        "performance": performance,
        "holdings": pd.DataFrame(holdings),
        "factors": outputs,
    }
