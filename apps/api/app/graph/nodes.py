from app.graph.state import ResearchState

NODE_ORDER = ["prepare_dataset", "factor_construction", "validation", "regime_estimation", "stock_ranking", "portfolio_construction", "historical_backtest", "benchmark_comparison", "persist_results"]

def prepare_dataset(state: ResearchState) -> ResearchState:
    return {**state, "dataset_version": state.get("dataset_version", "ngx_monthly_v3"), "eligible_universe": state.get("eligible_universe", [])}

def mark_node(name: str):
    def node(state: ResearchState) -> ResearchState:
        return {**state, "last_completed_node": name}
    return node