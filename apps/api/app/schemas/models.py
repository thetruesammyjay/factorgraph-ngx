from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field

FactorName = Literal["market", "size", "value", "momentum", "liquidity"]

class HealthResponse(BaseModel):
    status: str
    service: str
    version: str

class ExperimentConfig(BaseModel):
    name: str = "ngx-five-factor-baseline"
    start_date: date = date(2019, 1, 1)
    end_date: date = date(2025, 12, 31)
    factors: list[FactorName] = ["market", "size", "value", "momentum", "liquidity"]
    portfolio_method: str = "equal_weight"
    portfolio_size: int = Field(10, ge=1, le=100)
    rebalance_frequency: str = "monthly"
    regime_count: int = Field(3, ge=2, le=8)
    bootstrap_iterations: int = Field(10_000, ge=100)
    newey_west_threshold: float = 2.5
    fundamental_availability_policy: str = "actual_or_fixed_lag"
    fixed_reporting_lag_days: int = 90

class ExperimentCreate(ExperimentConfig):
    pass

class ExperimentResponse(ExperimentConfig):
    id: str
    status: str
    dataset_version: str
    git_commit: str | None = None
    created_at: datetime
    completed_at: datetime | None = None

class FactorStatistics(BaseModel):
    factor: FactorName
    mean_return: float
    annualised_return: float
    volatility: float
    sharpe: float
    newey_west_t: float
    max_drawdown: float


class DatasetQualityResponse(BaseModel):
    dataset_id: str
    structural_status: Literal["passed", "failed"]
    research_readiness: str
    source_pdf_count: int
    observation_count: int
    tickers: list[str]
    date_min: date
    date_max: date
    observations_by_ticker: dict[str, int]
    missing_ticker_dates: dict[str, int]
    duplicate_keys: int
    non_positive_closes: int
    carried_market_prices_by_ticker: dict[str, int]
    unique_closes_by_ticker: dict[str, int]
    longest_unchanged_close_run_by_ticker: dict[str, int]
    missing_liquidity_fields: dict[str, int]
    interpretation: str
