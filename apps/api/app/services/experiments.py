from app.graph.graph import build_research_graph
from app.graph.state import ResearchState

def execute_experiment(experiment_id: str, config: dict) -> ResearchState:
    state: ResearchState = {"experiment_id": experiment_id, "config": config, "errors": []}
    graph = build_research_graph()
    return graph.invoke(state) if graph else state