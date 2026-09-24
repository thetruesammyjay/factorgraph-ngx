import pandas as pd

from app.graph.state import ResearchState
from app.quant.characteristic_portfolios import build_characteristic_portfolios
from app.quant.momentum_pilot import run_momentum_pilot
from app.quant.regimes import build_regime_analysis
from app.quant.regressions import build_factor_regressions

NODE_ORDER = ["prepare_dataset", "factor_construction", "validation", "regime_estimation", "stock_ranking", "portfolio_construction", "historical_backtest", "benchmark_comparison", "persist_results"]

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
        },
    )


def estimate_regimes(state: ResearchState) -> ResearchState:
    report = state.get("pilot_report", {})
    config = state.get("config", {})
    market_factor = pd.DataFrame(report.get("market_factor", []))
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
            )
            results["characteristic_portfolios"] = characteristic_result
            outputs["characteristic_portfolios"] = {
                "status": characteristic_result["status"],
                "coverage": characteristic_result["coverage"],
                "factors": {
                    factor: characteristic_result["factors"][factor]
                    for factor in sorted(requested.intersection({"size", "value"}))
                },
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
            )
            results["momentum_portfolio"] = momentum_result
            outputs["momentum_portfolio"] = {
                "status": momentum_result["status"],
                "methodology": momentum_result["methodology"],
                "coverage": momentum_result["coverage"],
                "statistics": momentum_result["statistics"],
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


def summarize_backtest(state: ResearchState) -> ResearchState:
    """Summarize the portfolio streams produced earlier in this graph run."""
    report = state.get("pilot_report", {})
    portfolios = state.get("portfolio_results", {}) or {}
    characteristic = portfolios.get("characteristic_portfolios", {})
    momentum = portfolios.get("momentum_portfolio", {})
    outputs = {
        "market_factor": report.get("market_factor_statistics") or {},
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
    market_inputs = pd.DataFrame(report.get("market_factor", []))
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
        "aligned_market_months": coverage.get("aligned_months", 0),
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
        coverage = report.get("market_input_coverage", {})
        fundamentals = report.get("fundamentals_validation", {})
        return {
            "price_observations": price_coverage.get("observations", 0),
            "carried_price_rows": price_coverage.get("carried_price_rows", 0),
            "official_trade_returns": price_coverage.get("official_trade_returns", 0),
            "aligned_market_months": coverage.get("aligned_months", 0),
            "benchmark_months": coverage.get("benchmark_months", 0),
            "risk_free_months": coverage.get("risk_free_months", 0),
            "fundamental_errors": len(fundamentals.get("errors", [])),
            "fundamental_warnings": len(fundamentals.get("warnings", [])),
        }
    if name == "stock_ranking":
        characteristics = report.get("latest_characteristics", [])
        return {
            "latest_observations": len(characteristics),
            "size_eligible": sum(item.get("size_eligible", False) for item in characteristics),
            "value_eligible": sum(item.get("value_eligible", False) for item in characteristics),
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
