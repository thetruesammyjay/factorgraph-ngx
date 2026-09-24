import math

import pandas as pd

from app.factors.ranking import build_stock_rankings
from app.graph.state import ResearchState
from app.quant.characteristic_portfolios import build_characteristic_portfolios
from app.quant.momentum_pilot import latest_momentum_scores, run_momentum_pilot
from app.quant.regimes import build_regime_analysis
from app.quant.regressions import build_factor_regressions
from app.quant.statistics import describe_returns

NODE_ORDER = ["prepare_dataset", "factor_construction", "validation", "regime_estimation", "stock_ranking", "portfolio_construction", "historical_backtest", "benchmark_comparison", "persist_results"]


def _json_records(frame: pd.DataFrame) -> list[dict]:
    """Convert result tables to JSON-safe records for the saved run artifact."""
    records = []
    for record in frame.to_dict(orient="records"):
        normalized = {}
        for key, value in record.items():
            if value is None or pd.isna(value):
                normalized[key] = None
                continue
            if isinstance(value, pd.Timestamp):
                normalized[key] = value.isoformat()
                continue
            if hasattr(value, "item"):
                value = value.item()
            if isinstance(value, float) and not math.isfinite(value):
                normalized[key] = None
                continue
            normalized[key] = value
        records.append(normalized)
    return records


def _month_window(config: dict) -> tuple[str | None, str | None]:
    start = config.get("start_date")
    end = config.get("end_date")
    return (str(start)[:7] if start else None, str(end)[:7] if end else None)


def _filter_month_rows(rows: list[dict], config: dict, month_column: str = "observation_month") -> list[dict]:
    start_month, end_month = _month_window(config)
    filtered = []
    for row in rows:
        month = str(row.get(month_column, ""))[:7]
        if len(month) != 7:
            continue
        if start_month and month < start_month:
            continue
        if end_month and month > end_month:
            continue
        filtered.append(row)
    return filtered

def _completed(state: ResearchState, name: str, outputs: dict | None = None) -> ResearchState:
    trace = [
        *state.get("execution_trace", []),
        {
            "sequence": len(state.get("execution_trace", [])) + 1,
            "node": name,
            "status": "completed",
            "outputs": outputs or {},
        },
    ]
    node_outputs = {
        **state.get("node_outputs", {}),
        name: outputs or {},
    }
    return {
        **state,
        "last_completed_node": name,
        "execution_trace": trace,
        "node_outputs": node_outputs,
    }

def prepare_dataset(state: ResearchState) -> ResearchState:
    report = state.get("pilot_report", {})
    coverage = report.get("coverage", {})
    config = state.get("config", {})
    selected_market_rows = _filter_month_rows(report.get("market_factor", []), config)
    selected_characteristic_rows = _filter_month_rows(report.get("characteristics", []), config)
    prepared = {
        **state,
        "dataset_version": report.get("dataset_version", state.get("dataset_version", "ngx_monthly_v3")),
        "eligible_universe": state.get("eligible_universe") or [item["ticker"] for item in report.get("universe", {}).get("securities", [])],
    }
    return _completed(
        prepared,
        "prepare_dataset",
        {
            "dataset_version": prepared["dataset_version"],
            "observations": coverage.get("observations", 0),
            "tickers": coverage.get("tickers", 0),
            "date_range": [coverage.get("first_date"), coverage.get("last_date")],
            "requested_period": [
                str(config.get("start_date")) if config.get("start_date") else None,
                str(config.get("end_date")) if config.get("end_date") else None,
            ],
            "requested_factors": config.get("factors", []),
            "portfolio_size": config.get("portfolio_size"),
            "regime_count": config.get("regime_count"),
            "monthly_window": list(_month_window(config)),
            "market_months_in_window": len(selected_market_rows),
            "characteristic_rows_in_window": len(selected_characteristic_rows),
        },
    )


def estimate_regimes(state: ResearchState) -> ResearchState:
    report = state.get("pilot_report", {})
    config = state.get("config", {})
    market_factor = pd.DataFrame(_filter_month_rows(report.get("market_factor", []), config))
    requested_states = config.get("regime_count")
    if requested_states is None:
        requested_states = report.get("regime_analysis", {}).get("coverage", {}).get("states", 3)
    result = build_regime_analysis(market_factor, states=int(requested_states))
    outputs = {
        "status": result["status"],
        "reason": result["reason"],
        "coverage": result["coverage"],
        "model": result["model"],
        "statistics": result["statistics"],
        "transition_matrix": result["transition_matrix"],
        "timeline": result["timeline"],
    }
    return _completed(
        {**state, "regime_results": result},
        "regime_estimation",
        outputs,
    )


def construct_portfolios(state: ResearchState) -> ResearchState:
    """Rebuild requested characteristic and momentum portfolios for this run."""
    report = state.get("pilot_report", {})
    run_config = state.get("config", {})
    dataset_config = report.get("reproducibility", {}).get("configuration", {})
    characteristics = pd.DataFrame(report.get("characteristics", []))
    requested = set(run_config.get("factors", []))
    results: dict = {}
    outputs: dict = {}

    if requested.intersection({"size", "value"}):
        if characteristics.empty:
            outputs["characteristic_portfolios"] = {
                "status": "blocked",
                "reason": "The pilot report has no point-in-time characteristic rows.",
            }
        else:
            characteristic_result = build_characteristic_portfolios(
                characteristics,
                groups=int(dataset_config.get("characteristic_groups", 2)),
                min_assets=int(dataset_config.get("characteristic_min_assets", 2)),
                bootstrap_iterations=int(run_config.get("bootstrap_iterations", 10_000)),
                holding_start_month=_month_window(run_config)[0],
                holding_end_month=_month_window(run_config)[1],
            )
            results["characteristic_portfolios"] = characteristic_result
            outputs["characteristic_portfolios"] = {
                "status": characteristic_result["status"],
                "coverage": characteristic_result["coverage"],
                "factors": {
                    factor: characteristic_result["factors"][factor]
                    for factor in sorted(requested.intersection({"size", "value"}))
                },
                "performance": _json_records(characteristic_result["performance"]),
                "holdings": _json_records(characteristic_result["holdings"]),
            }
    else:
        outputs["characteristic_portfolios"] = {
            "status": "skipped",
            "reason": "Size and Value were not selected for this experiment.",
        }

    if "momentum" in requested:
        monthly_columns = [
            "observation_month",
            "ticker",
            "marked_monthly_return",
            "official_monthly_return",
        ]
        missing = [column for column in monthly_columns if column not in characteristics]
        if missing:
            outputs["momentum_portfolio"] = {
                "status": "blocked",
                "reason": f"Point-in-time monthly data is missing columns: {', '.join(missing)}.",
            }
        else:
            momentum_result = run_momentum_pilot(
                characteristics[monthly_columns].copy(),
                lookback_months=int(dataset_config.get("momentum_months", 11)),
                skip_months=int(dataset_config.get("momentum_skip_months", 1)),
                portfolio_size=int(run_config.get("portfolio_size", dataset_config.get("momentum_portfolio_size", 5))),
                transaction_cost_bps=float(dataset_config.get("transaction_cost_bps", 50)),
                start_month=_month_window(run_config)[0],
                end_month=_month_window(run_config)[1],
            )
            results["momentum_portfolio"] = momentum_result
            outputs["momentum_portfolio"] = {
                "status": momentum_result["status"],
                "methodology": momentum_result["methodology"],
                "coverage": momentum_result["coverage"],
                "statistics": momentum_result["statistics"],
                "performance": _json_records(momentum_result["performance"]),
                "holdings": _json_records(momentum_result["holdings"]),
            }
    else:
        outputs["momentum_portfolio"] = {
            "status": "skipped",
            "reason": "Momentum was not selected for this experiment.",
        }

    return _completed(
        {**state, "portfolio_results": results},
        "portfolio_construction",
        outputs,
    )


def rank_stocks(state: ResearchState) -> ResearchState:
    """Create independent point-in-time cross-sectional factor rankings."""
    report = state.get("pilot_report", {})
    config = state.get("config", {})
    dataset_config = report.get("reproducibility", {}).get("configuration", {})
    requested = list(config.get("factors", []))
    characteristics = pd.DataFrame(
        _filter_month_rows(report.get("characteristics", []), config)
    )
    if characteristics.empty:
        momentum_scores = pd.DataFrame()
    else:
        latest_month = characteristics["observation_month"].astype(str).max()
        momentum_history = pd.DataFrame(report.get("characteristics", []))
        momentum_history = momentum_history[
            ["observation_month", "ticker", "marked_monthly_return"]
        ].copy()
        momentum_scores = latest_momentum_scores(
            momentum_history,
            lookback_months=int(dataset_config.get("momentum_months", 11)),
            skip_months=int(dataset_config.get("momentum_skip_months", 1)),
            as_of_month=latest_month,
        )
    result = build_stock_rankings(
        characteristics,
        momentum_scores,
        requested_factors=requested,
        portfolio_size=int(config.get("portfolio_size", 10)),
    )
    result["methodology"] = {
        "ranking_date": "latest point-in-time observation month inside the requested window",
        "selection": "top configured portfolio size within each independent factor sort",
        "size": "smallest market capitalization first",
        "value": "highest book-to-market first",
        "momentum": f"{dataset_config.get('momentum_months', 11)}-month prior marked return, skipping {dataset_config.get('momentum_skip_months', 1)} recent month(s)",
    }
    return _completed(
        {**state, "stock_scores": result},
        "stock_ranking",
        result,
    )


def summarize_backtest(state: ResearchState) -> ResearchState:
    """Summarize the portfolio streams produced earlier in this graph run."""
    report = state.get("pilot_report", {})
    portfolios = state.get("portfolio_results", {}) or {}
    characteristic = portfolios.get("characteristic_portfolios", {})
    momentum = portfolios.get("momentum_portfolio", {})
    market_factor = pd.DataFrame(
        _filter_month_rows(report.get("market_factor", []), state.get("config", {}))
    )
    market_returns = (
        pd.to_numeric(market_factor["market_excess_return"], errors="coerce")
        if "market_excess_return" in market_factor
        else pd.Series(dtype=float)
    )
    outputs = {
        "market_factor": describe_returns(market_returns) if market_returns.notna().any() else {},
        "characteristic_factors": characteristic.get("factors", {}),
        "characteristic_coverage": characteristic.get("coverage", {}),
        "momentum_statistics": momentum.get("statistics"),
        "momentum_coverage": momentum.get("coverage", {}),
    }
    return _completed(
        {**state, "backtest_results": outputs},
        "historical_backtest",
        outputs,
    )


def compare_benchmarks(state: ResearchState) -> ResearchState:
    """Estimate HAC market-model alpha and beta for this run's portfolios."""
    report = state.get("pilot_report", {})
    portfolios = state.get("portfolio_results", {}) or {}
    market_inputs = pd.DataFrame(
        _filter_month_rows(report.get("market_factor", []), state.get("config", {}))
    )
    characteristic = portfolios.get("characteristic_portfolios", {})
    momentum = portfolios.get("momentum_portfolio", {})
    characteristic_performance = characteristic.get("performance", pd.DataFrame())
    momentum_performance = momentum.get("performance", pd.DataFrame())

    regressions = build_factor_regressions(
        market_inputs,
        characteristic_performance,
        momentum_performance,
    )
    requested = set(state.get("config", {}).get("factors", []))
    selected = {
        factor: regressions[factor]
        for factor in ("size", "value", "momentum")
        if factor in requested
    }
    coverage = report.get("market_input_coverage", {})
    outputs = {
        "benchmark_code": coverage.get("benchmark_code"),
        "risk_free_tenor": coverage.get("risk_free_tenor"),
        "aligned_market_months": (
            int(pd.to_numeric(market_inputs.get("market_excess_return", pd.Series(dtype=float)), errors="coerce").notna().sum())
            if not market_inputs.empty
            else 0
        ),
        "regressions": selected,
        "methodology": {
            "model": "portfolio return on NGX ASI excess return",
            "inference": "Newey-West HAC standard errors",
            "momentum_target": "monthly net return less matched 91-day T-bill return",
            "characteristic_targets": "zero-investment long-short spread returns",
        },
    }
    return _completed(
        {**state, "benchmark_results": outputs},
        "benchmark_comparison",
        outputs,
    )


def _report_outputs(name: str, report: dict, config: dict | None = None) -> dict:
    if name == "factor_construction":
        eligibility = report.get("factor_eligibility", [])
        requested = (config or {}).get("factors") or [item.get("factor") for item in eligibility]
        available = {item.get("factor") for item in eligibility}
        return {
            "factors": len(eligibility),
            "requested_factors": requested,
            "selected_factors": [factor for factor in requested if factor in available],
            "unavailable_factors": [factor for factor in requested if factor not in available],
            "factor_statuses": {item.get("factor"): item.get("status") for item in eligibility},
            "eligible": sum(item.get("status") == "eligible" for item in eligibility),
            "preliminary": sum(item.get("status") == "preliminary" for item in eligibility),
            "blocked": sum(item.get("status") == "blocked" for item in eligibility),
        }
    if name == "validation":
        price_coverage = report.get("coverage", {})
        market_rows = _filter_month_rows(report.get("market_factor", []), config or {})
        fundamentals = report.get("fundamentals_validation", {})
        return {
            "price_observations": price_coverage.get("observations", 0),
            "carried_price_rows": price_coverage.get("carried_price_rows", 0),
            "official_trade_returns": price_coverage.get("official_trade_returns", 0),
            "aligned_market_months": sum(row.get("market_excess_return") is not None for row in market_rows),
            "benchmark_months": sum(row.get("market_return") is not None for row in market_rows),
            "risk_free_months": sum(row.get("risk_free_return") is not None for row in market_rows),
            "monthly_window": list(_month_window(config or {})),
            "fundamental_errors": len(fundamentals.get("errors", [])),
            "fundamental_warnings": len(fundamentals.get("warnings", [])),
        }
    if name == "persist_results":
        reproducibility = report.get("reproducibility", {})
        return {
            "fingerprint": reproducibility.get("fingerprint"),
            "dataset_provenance": reproducibility,
            "generated_at": report.get("generated_at"),
        }
    return {}

def mark_node(name: str):
    def node(state: ResearchState) -> ResearchState:
        completed = _completed(
            state,
            name,
            _report_outputs(name, state.get("pilot_report", {}), state.get("config", {})),
        )
        if name == "persist_results":
            trace = completed["execution_trace"]
            trace[-1]["outputs"]["run_fingerprint"] = state.get("run_fingerprint")
            completed["node_outputs"][name]["run_fingerprint"] = state.get("run_fingerprint")
        return completed
    return node
