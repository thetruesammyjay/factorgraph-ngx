from typing import Any, TypedDict


class ResearchState(TypedDict, total=False):
    experiment_id: str
    config: dict[str, Any]
    status: str
    execution_trace: list[dict[str, Any]]
    node_outputs: dict[str, dict[str, Any]]
    pilot_report: dict[str, Any]
    constraints: list[dict[str, Any]]
    run_fingerprint: str
    last_completed_node: str
    dataset_version: str
    eligible_universe: list[str]
    market_factor: dict[str, Any] | None
    size_factor: dict[str, Any] | None
    value_factor: dict[str, Any] | None
    momentum_factor: dict[str, Any] | None
    liquidity_factor: dict[str, Any] | None
    validation_results: dict[str, Any] | None
    regime_results: dict[str, Any] | None
    stock_scores: dict[str, Any] | None
    portfolio_results: dict[str, Any] | None
    backtest_results: dict[str, Any] | None
    benchmark_results: dict[str, Any] | None
    errors: list[dict[str, Any]]
