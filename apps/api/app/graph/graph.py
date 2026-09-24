from itertools import pairwise

from app.graph.nodes import (
    NODE_ORDER,
    compare_benchmarks,
    construct_portfolios,
    estimate_regimes,
    mark_node,
    prepare_dataset,
    summarize_backtest,
)
from app.graph.state import ResearchState

try:
    from langgraph.graph import END, START, StateGraph
except ImportError:  # Keep the module importable before uv sync.
    StateGraph = None


def build_research_graph():
    if StateGraph is None:
        return None
    graph = StateGraph(ResearchState)
    graph.add_node("prepare_dataset", prepare_dataset)
    for name in NODE_ORDER[1:]:
        graph.add_node(
            name,
            {
                "regime_estimation": estimate_regimes,
                "portfolio_construction": construct_portfolios,
                "historical_backtest": summarize_backtest,
                "benchmark_comparison": compare_benchmarks,
            }.get(name, mark_node(name)),
        )
    graph.add_edge(START, "prepare_dataset")
    for previous, current in pairwise(NODE_ORDER):
        graph.add_edge(previous, current)
    graph.add_edge(NODE_ORDER[-1], END)
    return graph.compile()
