from app.data.experiment_reports import load_pilot_report
from app.graph.graph import build_research_graph
from app.graph.state import ResearchState


def execute_experiment(experiment_id: str, config: dict) -> ResearchState:
    state: ResearchState = {
        "experiment_id": experiment_id,
        "config": config,
        "errors": [],
        "status": "running",
        "execution_trace": [],
        "node_outputs": {},
    }
    try:
        state["pilot_report"] = load_pilot_report()
    except (FileNotFoundError, ValueError) as exc:
        return {**state, "status": "blocked", "errors": [{"message": str(exc)}]}
    graph = build_research_graph()
    if graph is None:
        return {**state, "status": "blocked", "errors": [{"message": "LangGraph is unavailable"}]}
    return {**graph.invoke(state), "status": "completed"}
