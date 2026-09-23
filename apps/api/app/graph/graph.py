from itertools import pairwise

from app.graph.nodes import NODE_ORDER, mark_node, prepare_dataset
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
    for name in NODE_ORDER[1:]: graph.add_node(name, mark_node(name))
    graph.add_edge(START, "prepare_dataset")
    for previous, current in pairwise(NODE_ORDER): graph.add_edge(previous, current)
    graph.add_edge(NODE_ORDER[-1], END)
    return graph.compile()
