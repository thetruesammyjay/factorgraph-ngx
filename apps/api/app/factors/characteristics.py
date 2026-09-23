"""Point-in-time Size and Value characteristics for monthly NGX observations."""

from __future__ import annotations

from dataclasses import asdict, dataclass

import numpy as np
import pandas as pd

MONTHLY_COLUMNS = {"observation_month", "trading_date", "ticker", "close"}
FUNDAMENTAL_COLUMNS = {
    "ticker",
    "fiscal_period",
    "effective_from",
    "effective_date_source",
    "book_equity",
    "shares_outstanding",
    "source_id",
}


@dataclass(frozen=True)
class CharacteristicCoverage:
    observations: int
    months: int
    universe_tickers: int
    point_in_time_observations: int
    fundamental_tickers: int
    size_eligible_observations: int
    value_eligible_observations: int
    actual_date_observations: int
    estimated_date_observations: int

    def to_dict(self) -> dict[str, int]:
        return asdict(self)


def _validate(frame: pd.DataFrame, columns: set[str], label: str) -> None:
    missing = sorted(columns.difference(frame.columns))
    if missing:
        raise ValueError(f"{label} data missing columns: {', '.join(missing)}")


def build_point_in_time_characteristics(
    monthly: pd.DataFrame, fundamentals: pd.DataFrame
) -> tuple[pd.DataFrame, CharacteristicCoverage]:
    """Join each month to the latest fundamental known on its observation date."""
    _validate(monthly, MONTHLY_COLUMNS, "monthly")
    _validate(fundamentals, FUNDAMENTAL_COLUMNS, "fundamental")
    prices = monthly.copy()
    prices["trading_date"] = pd.to_datetime(prices["trading_date"], errors="coerce")
    prices["ticker"] = prices["ticker"].astype("string").str.strip().str.upper()
    prices["close"] = pd.to_numeric(prices["close"], errors="coerce")
    if prices["trading_date"].isna().any():
        raise ValueError("monthly data contains invalid trading dates")
    if prices[["observation_month", "ticker"]].duplicated().any():
        raise ValueError("monthly data contains duplicate month-ticker keys")
    if prices["close"].isna().any() or (prices["close"] <= 0).any():
        raise ValueError("monthly data contains missing or non-positive closes")

    facts = fundamentals.copy()
    facts["ticker"] = facts["ticker"].astype("string").str.strip().str.upper()
    for column in ("fiscal_period", "effective_from"):
        facts[column] = pd.to_datetime(facts[column], errors="coerce")
    for column in ("book_equity", "shares_outstanding"):
        facts[column] = pd.to_numeric(facts[column], errors="coerce")
    if facts[["fiscal_period", "effective_from"]].isna().any().any():
        raise ValueError("fundamental data contains invalid point-in-time dates")
    if facts[["ticker", "fiscal_period", "effective_from"]].duplicated().any():
        raise ValueError("fundamental data contains duplicate point-in-time keys")
    if (facts["shares_outstanding"].dropna() <= 0).any():
        raise ValueError("fundamental data contains non-positive shares outstanding")

    aligned_parts = []
    fact_columns = sorted(FUNDAMENTAL_COLUMNS.difference({"ticker", "effective_from"}))
    for ticker, price_group in prices.groupby("ticker", sort=True):
        fact_group = facts[facts["ticker"] == ticker].sort_values("effective_from")
        left = price_group.sort_values("trading_date")
        if fact_group.empty:
            aligned = left.copy()
            for column in fact_columns:
                aligned[column] = pd.NA
        else:
            aligned = pd.merge_asof(
                left,
                fact_group[["effective_from", *fact_columns]].sort_values("effective_from"),
                left_on="trading_date",
                right_on="effective_from",
                direction="backward",
                allow_exact_matches=True,
            )
        aligned_parts.append(aligned)
    result = pd.concat(aligned_parts, ignore_index=True)
    for column in ("book_equity", "shares_outstanding"):
        result[column] = pd.to_numeric(result[column], errors="coerce")

    result["has_point_in_time_fundamentals"] = result["effective_from"].notna()
    result["size_eligible"] = (
        result["has_point_in_time_fundamentals"]
        & result["shares_outstanding"].notna()
        & result["shares_outstanding"].gt(0)
    )
    result["value_eligible"] = (
        result["size_eligible"]
        & result["book_equity"].notna()
        & result["book_equity"].gt(0)
    )
    result["market_cap"] = (
        result["close"] * result["shares_outstanding"]
    ).where(result["size_eligible"])
    result["log_market_cap"] = np.log(result["market_cap"]).where(result["size_eligible"])
    result["book_to_market"] = (
        result["book_equity"] / result["market_cap"]
    ).where(result["value_eligible"])
    result["size_rank"] = result.groupby("observation_month")["market_cap"].rank(
        ascending=True, method="min"
    )
    result["value_rank"] = result.groupby("observation_month")["book_to_market"].rank(
        ascending=False, method="min"
    )
    result["size_exclusion_reason"] = result["size_eligible"].map(
        {True: None, False: "missing_point_in_time_fundamentals"}
    )
    result["value_exclusion_reason"] = None
    result.loc[
        ~result["has_point_in_time_fundamentals"], "value_exclusion_reason"
    ] = "missing_point_in_time_fundamentals"
    result.loc[
        result["size_eligible"] & ~result["value_eligible"], "value_exclusion_reason"
    ] = "non_positive_or_missing_book_equity"

    date_sources = result["effective_date_source"].fillna("")
    coverage = CharacteristicCoverage(
        observations=len(result),
        months=result["observation_month"].nunique(),
        universe_tickers=result["ticker"].nunique(),
        point_in_time_observations=int(result["has_point_in_time_fundamentals"].sum()),
        fundamental_tickers=result.loc[
            result["has_point_in_time_fundamentals"], "ticker"
        ].nunique(),
        size_eligible_observations=int(result["size_eligible"].sum()),
        value_eligible_observations=int(result["value_eligible"].sum()),
        actual_date_observations=int(date_sources.eq("ACTUAL_PUBLICATION_DATE").sum()),
        estimated_date_observations=int(date_sources.eq("FIXED_LAG_ESTIMATE").sum()),
    )
    return result.sort_values(["observation_month", "ticker"]), coverage


def latest_characteristic_snapshot(characteristics: pd.DataFrame) -> pd.DataFrame:
    """Return the latest month with transparent eligibility and exclusion fields."""
    if characteristics.empty:
        return characteristics.copy()
    latest_month = characteristics["observation_month"].max()
    columns = [
        "observation_month",
        "ticker",
        "close",
        "fiscal_period",
        "effective_from",
        "effective_date_source",
        "market_cap",
        "book_to_market",
        "size_rank",
        "value_rank",
        "size_eligible",
        "value_eligible",
        "size_exclusion_reason",
        "value_exclusion_reason",
        "source_id",
    ]
    return characteristics.loc[
        characteristics["observation_month"] == latest_month, columns
    ].sort_values(["size_eligible", "size_rank", "ticker"], ascending=[False, True, True])
