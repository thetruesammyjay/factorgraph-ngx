from app.graph.state import ResearchState

NODE_ORDER = ["prepare_dataset", "factor_construction", "validation", "regime_estimation", "stock_ranking", "portfolio_construction", "historical_backtest", "benchmark_comparison", "persist_results"]

def _completed(state: ResearchState, name: str, outputs: dict | None = None) -> ResearchState:
    trace = [
        *state.get("execution_trace", []),
        {"node": name, "status": "completed", "outputs": outputs or {}},
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
        },
    )


def _report_outputs(name: str, report: dict) -> dict:
    if name == "factor_construction":
        eligibility = report.get("factor_eligibility", [])
        return {
            "factors": len(eligibility),
            "eligible": sum(item.get("status") == "eligible" for item in eligibility),
            "preliminary": sum(item.get("status") == "preliminary" for item in eligibility),
            "blocked": sum(item.get("status") == "blocked" for item in eligibility),
        }
    if name == "validation":
        coverage = report.get("market_input_coverage", {})
        return {
            "aligned_market_months": coverage.get("aligned_months", 0),
            "fundamentals_status": report.get("fundamentals_validation", {}).get("status", "unknown"),
        }
    if name == "regime_estimation":
        regime = report.get("regime_analysis", {})
        return {
            "status": regime.get("status", "unknown"),
            "monthly_endpoints": regime.get("coverage", {}).get("monthly_endpoints", 0),
            "reason": regime.get("reason"),
        }
    if name == "stock_ranking":
        characteristics = report.get("latest_characteristics", [])
        return {
            "latest_observations": len(characteristics),
            "size_eligible": sum(item.get("size_eligible", False) for item in characteristics),
            "value_eligible": sum(item.get("value_eligible", False) for item in characteristics),
        }
    if name == "portfolio_construction":
        portfolios = report.get("characteristic_portfolios", {})
        momentum = report.get("momentum_portfolio", {})
        return {
            "characteristic_status": portfolios.get("status", "unknown"),
            "size_spread_months": portfolios.get("coverage", {}).get("months_with_size_spread", 0),
            "value_spread_months": portfolios.get("coverage", {}).get("months_with_value_spread", 0),
            "momentum_status": momentum.get("status", "unknown"),
        }
    if name == "historical_backtest":
        statistics = report.get("market_factor_statistics") or {}
        momentum = report.get("momentum_portfolio", {}).get("statistics") or {}
        return {
            "market_observations": statistics.get("observations", 0),
            "market_sharpe": statistics.get("sharpe"),
            "momentum_observations": momentum.get("observations", 0),
        }
    if name == "benchmark_comparison":
        coverage = report.get("market_input_coverage", {})
        return {
            "benchmark_code": coverage.get("benchmark_code"),
            "risk_free_tenor": coverage.get("risk_free_tenor"),
            "aligned_months": coverage.get("aligned_months", 0),
        }
    if name == "persist_results":
        reproducibility = report.get("reproducibility", {})
        return {
            "fingerprint": reproducibility.get("fingerprint"),
            "generated_at": report.get("generated_at"),
        }
    return {}

def mark_node(name: str):
    def node(state: ResearchState) -> ResearchState:
        return _completed(state, name, _report_outputs(name, state.get("pilot_report", {})))
    return node
