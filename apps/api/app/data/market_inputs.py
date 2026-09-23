"""Validation and monthly alignment for benchmark and risk-free observations."""

from __future__ import annotations

from dataclasses import asdict, dataclass

import pandas as pd

BENCHMARK_COLUMNS = {
    "observation_date",
    "index_code",
    "index_name",
    "close",
    "source_id",
}
RISK_FREE_COLUMNS = {
    "observation_date",
    "series_name",
    "tenor",
    "annual_rate_percent",
    "source_id",
}


@dataclass(frozen=True)
class MarketInputCoverage:
    benchmark_observations: int
    benchmark_months: int
    risk_free_observations: int
    risk_free_months: int
    aligned_months: int
    benchmark_code: str | None
    risk_free_tenor: str | None
    first_aligned_month: str | None
    last_aligned_month: str | None

    def to_dict(self) -> dict[str, int | str | None]:
        return asdict(self)


def _require_columns(frame: pd.DataFrame, required: set[str], label: str) -> None:
    missing = sorted(required.difference(frame.columns))
    if missing:
        raise ValueError(f"{label} data missing columns: {', '.join(missing)}")


def validate_benchmark_observations(frame: pd.DataFrame) -> pd.DataFrame:
    """Normalize benchmark observations and reject ambiguous or invalid rows."""
    _require_columns(frame, BENCHMARK_COLUMNS, "benchmark")
    result = frame.copy()
    result["observation_date"] = pd.to_datetime(result["observation_date"], errors="coerce")
    result["index_code"] = result["index_code"].astype("string").str.strip().str.upper()
    result["close"] = pd.to_numeric(result["close"], errors="coerce")
    if result.empty:
        return result
    if result["observation_date"].isna().any():
        raise ValueError("benchmark data contains invalid observation dates")
    if result["index_code"].isna().any() or result["index_code"].eq("").any():
        raise ValueError("benchmark data contains missing index codes")
    if result["close"].isna().any() or (result["close"] <= 0).any():
        raise ValueError("benchmark data contains missing or non-positive closes")
    if result[["index_code", "observation_date"]].duplicated().any():
        raise ValueError("benchmark data contains duplicate index-date keys")
    return result.sort_values(["index_code", "observation_date"]).reset_index(drop=True)


def validate_risk_free_observations(frame: pd.DataFrame) -> pd.DataFrame:
    """Normalize annual percentage rates and reject invalid observations."""
    _require_columns(frame, RISK_FREE_COLUMNS, "risk-free")
    result = frame.copy()
    result["observation_date"] = pd.to_datetime(result["observation_date"], errors="coerce")
    result["tenor"] = result["tenor"].astype("string").str.strip().str.upper()
    result["annual_rate_percent"] = pd.to_numeric(
        result["annual_rate_percent"], errors="coerce"
    )
    if result.empty:
        return result
    if result["observation_date"].isna().any():
        raise ValueError("risk-free data contains invalid observation dates")
    if result["tenor"].isna().any() or result["tenor"].eq("").any():
        raise ValueError("risk-free data contains missing tenors")
    if result["annual_rate_percent"].isna().any():
        raise ValueError("risk-free data contains missing or non-numeric rates")
    if (result["annual_rate_percent"] <= -100).any():
        raise ValueError("risk-free annual rates must be greater than -100 percent")
    if result[["tenor", "observation_date"]].duplicated().any():
        raise ValueError("risk-free data contains duplicate tenor-date keys")
    return result.sort_values(["tenor", "observation_date"]).reset_index(drop=True)


def build_monthly_market_inputs(
    benchmark: pd.DataFrame,
    risk_free: pd.DataFrame,
    *,
    benchmark_code: str = "NGXASI",
    risk_free_tenor: str = "91D",
) -> tuple[pd.DataFrame, MarketInputCoverage]:
    """Align month-end benchmark returns with effective monthly risk-free returns."""
    benchmark = validate_benchmark_observations(benchmark)
    risk_free = validate_risk_free_observations(risk_free)
    code = benchmark_code.strip().upper()
    tenor = risk_free_tenor.strip().upper()

    selected_benchmark = benchmark[benchmark["index_code"] == code].copy()
    selected_risk_free = risk_free[risk_free["tenor"] == tenor].copy()

    if selected_benchmark.empty or selected_risk_free.empty:
        aligned = pd.DataFrame(
            columns=[
                "observation_month",
                "benchmark_close",
                "market_return",
                "annual_rate_percent",
                "risk_free_return",
                "market_excess_return",
            ]
        )
    else:
        selected_benchmark["month"] = selected_benchmark["observation_date"].dt.to_period("M")
        benchmark_monthly = selected_benchmark.groupby("month", as_index=False).tail(1).copy()
        benchmark_monthly["market_return"] = benchmark_monthly["close"].pct_change(
            fill_method=None
        )
        benchmark_monthly = benchmark_monthly.rename(columns={"close": "benchmark_close"})

        selected_risk_free["month"] = selected_risk_free["observation_date"].dt.to_period("M")
        risk_free_monthly = selected_risk_free.groupby("month", as_index=False).tail(1).copy()
        annual_decimal = risk_free_monthly["annual_rate_percent"] / 100
        risk_free_monthly["risk_free_return"] = (1 + annual_decimal) ** (1 / 12) - 1

        aligned = benchmark_monthly[
            ["month", "benchmark_close", "market_return"]
        ].merge(
            risk_free_monthly[["month", "annual_rate_percent", "risk_free_return"]],
            on="month",
            how="inner",
        )
        aligned["market_excess_return"] = (
            aligned["market_return"] - aligned["risk_free_return"]
        )
        aligned["observation_month"] = aligned["month"].astype(str)
        aligned = aligned.drop(columns="month")[
            [
                "observation_month",
                "benchmark_close",
                "market_return",
                "annual_rate_percent",
                "risk_free_return",
                "market_excess_return",
            ]
        ]

    months = aligned["observation_month"] if not aligned.empty else pd.Series(dtype="string")
    coverage = MarketInputCoverage(
        benchmark_observations=len(selected_benchmark),
        benchmark_months=(
            selected_benchmark["observation_date"].dt.to_period("M").nunique()
            if not selected_benchmark.empty
            else 0
        ),
        risk_free_observations=len(selected_risk_free),
        risk_free_months=(
            selected_risk_free["observation_date"].dt.to_period("M").nunique()
            if not selected_risk_free.empty
            else 0
        ),
        aligned_months=len(aligned),
        benchmark_code=code if not selected_benchmark.empty else None,
        risk_free_tenor=tenor if not selected_risk_free.empty else None,
        first_aligned_month=str(months.min()) if not months.empty else None,
        last_aligned_month=str(months.max()) if not months.empty else None,
    )
    return aligned, coverage
