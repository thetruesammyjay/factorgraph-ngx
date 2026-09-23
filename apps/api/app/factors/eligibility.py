"""Factor input gates for the public-data NGX pilot."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Literal

import pandas as pd

EligibilityStatus = Literal["eligible", "preliminary", "blocked"]


@dataclass(frozen=True)
class FactorEligibility:
    factor: str
    status: EligibilityStatus
    reasons: list[str]
    metrics: dict[str, int | float | bool | str]

    def to_dict(self) -> dict:
        return asdict(self)


def evaluate_factor_eligibility(
    prices: pd.DataFrame,
    monthly_returns: pd.DataFrame,
    fundamentals: pd.DataFrame,
    *,
    expected_tickers: int = 15,
    expected_fundamentals: int = 30,
    benchmark_available: bool = False,
    risk_free_available: bool = False,
) -> list[FactorEligibility]:
    """Evaluate factor readiness from observed coverage rather than configuration."""
    ticker_count = prices["ticker"].nunique()
    month_count = monthly_returns["observation_month"].nunique()
    fundamental_rows = len(fundamentals)
    fundamental_tickers = fundamentals["ticker"].nunique() if not fundamentals.empty else 0
    positive_book_rows = (
        int((pd.to_numeric(fundamentals["book_equity"], errors="coerce") > 0).sum())
        if "book_equity" in fundamentals
        else 0
    )
    liquidity_fields = ["volume", "trading_value", "number_of_transactions"]
    liquidity_counts = {
        column: int(
            pd.to_numeric(
                prices[column] if column in prices else pd.Series(dtype="float64"),
                errors="coerce",
            ).notna().sum()
        )
        for column in liquidity_fields
    }

    market_reasons = ["15-security equal-weight market proxy is available"]
    if not benchmark_available:
        market_reasons.append("NGX All-Share Index history is unavailable")
    if not risk_free_available:
        market_reasons.append("risk-free series is unavailable; excess returns are blocked")

    standard_momentum_ready = month_count >= 13
    momentum_status: EligibilityStatus = "eligible" if standard_momentum_ready else "preliminary"
    momentum_reasons = (
        ["at least 13 monthly endpoints support 12-1 formation"]
        if standard_momentum_ready
        else [
            f"only {month_count} monthly endpoints are available",
            "short-horizon momentum is permitted; conventional 12-1 momentum is blocked",
        ]
    )

    fundamentals_complete = fundamental_rows >= expected_fundamentals
    size_value_status: EligibilityStatus = "eligible" if fundamentals_complete else "preliminary"
    shared_reasons = [
        f"{fundamental_rows} of {expected_fundamentals} issuer-period observations are validated",
        f"fundamentals currently cover {fundamental_tickers} issuers",
    ]

    liquidity_ready = liquidity_counts["volume"] > 0 and liquidity_counts["trading_value"] > 0
    liquidity_status: EligibilityStatus = "eligible" if liquidity_ready else "blocked"
    liquidity_reasons = (
        ["verified volume and traded value observations are available"]
        if liquidity_ready
        else ["verified daily volume and traded value are unavailable"]
    )

    return [
        FactorEligibility(
            "market",
            "eligible" if benchmark_available and risk_free_available else "preliminary",
            market_reasons,
            {
                "price_tickers": ticker_count,
                "expected_tickers": expected_tickers,
                "benchmark_available": benchmark_available,
                "risk_free_available": risk_free_available,
            },
        ),
        FactorEligibility(
            "size",
            size_value_status,
            shared_reasons.copy(),
            {
                "validated_fundamental_rows": fundamental_rows,
                "expected_fundamental_rows": expected_fundamentals,
                "fundamental_tickers": fundamental_tickers,
            },
        ),
        FactorEligibility(
            "value",
            size_value_status,
            shared_reasons
            + [f"{positive_book_rows} observations have positive book equity"],
            {
                "validated_fundamental_rows": fundamental_rows,
                "positive_book_equity_rows": positive_book_rows,
                "fundamental_tickers": fundamental_tickers,
            },
        ),
        FactorEligibility(
            "momentum",
            momentum_status,
            momentum_reasons,
            {
                "monthly_endpoints": month_count,
                "standard_12_1_ready": standard_momentum_ready,
            },
        ),
        FactorEligibility(
            "liquidity",
            liquidity_status,
            liquidity_reasons,
            liquidity_counts,
        ),
    ]
