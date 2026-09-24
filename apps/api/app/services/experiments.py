import hashlib
import json

from app.data.experiment_reports import load_pilot_report
from app.graph.graph import build_research_graph
from app.graph.nodes import NODE_ORDER
from app.graph.state import ResearchState

VOLATILE_EXPERIMENT_FIELDS = {
    "id",
    "name",
    "status",
    "dataset_version",
    "created_at",
    "completed_at",
    "git_commit",
    "execution_trace",
    "node_outputs",
    "constraints",
    "run_fingerprint",
    "last_completed_node",
    "errors",
}


def stable_experiment_config(config: dict) -> dict:
    return {
        key: value for key, value in config.items() if key not in VOLATILE_EXPERIMENT_FIELDS
    }


def build_experiment_plan(config: dict, report: dict) -> dict:
    eligibility = {
        item.get("factor"): item
        for item in report.get("factor_eligibility", [])
    }
    requested = config.get("factors", [])
    constraints = [
        {
            "factor": factor,
            "status": eligibility.get(factor, {}).get("status", "unavailable"),
            "reasons": eligibility.get(factor, {}).get("reasons", ["No eligibility record"]),
        }
        for factor in requested
        if eligibility.get(factor, {}).get("status") != "eligible"
    ]
    fingerprint_input = {
        "dataset_fingerprint": report.get("reproducibility", {}).get("fingerprint"),
        "configuration": stable_experiment_config(config),
    }
    run_fingerprint = hashlib.sha256(
        json.dumps(fingerprint_input, sort_keys=True, default=str).encode("utf-8")
    ).hexdigest()
    start_month = str(config.get("start_date", ""))[:7] or None
    end_month = str(config.get("end_date", ""))[:7] or None

    def selected(month: str) -> bool:
        return (not start_month or month >= start_month) and (
            not end_month or month <= end_month
        )

    market_months = sorted(
        {
            str(item.get("observation_month", ""))[:7]
            for item in report.get("market_factor", [])
            if item.get("observation_month") and selected(str(item["observation_month"])[:7])
        }
    )
    characteristic_months = sorted(
        {
            str(item.get("observation_month", ""))[:7]
            for item in report.get("characteristics", [])
            if item.get("observation_month") and selected(str(item["observation_month"])[:7])
        }
    )
    return {
        "dataset_version": report.get("dataset_version"),
        "analysis_window": {
            "granularity": "calendar month",
            "start_month": start_month,
            "end_month": end_month,
            "market_months": len(market_months),
            "characteristic_months": len(characteristic_months),
        },
        "requested_factors": requested,
        "factor_statuses": {
            factor: eligibility.get(factor, {}).get("status", "unavailable")
            for factor in requested
        },
        "constraints": constraints,
        "planned_nodes": list(NODE_ORDER),
        "run_fingerprint": run_fingerprint,
    }


def execute_experiment(experiment_id: str, config: dict) -> ResearchState:
    state: ResearchState = {
        "experiment_id": experiment_id,
        "config": config,
        "errors": [],
        "status": "running",
        "execution_trace": [],
        "node_outputs": {},
        "constraints": [],
    }
    try:
        state["pilot_report"] = load_pilot_report()
    except (FileNotFoundError, ValueError) as exc:
        return {**state, "status": "blocked", "errors": [{"message": str(exc)}]}
    plan = build_experiment_plan(config, state["pilot_report"])
    state["run_fingerprint"] = plan["run_fingerprint"]
    state["constraints"] = plan["constraints"]
    graph = build_research_graph()
    if graph is None:
        return {**state, "status": "blocked", "errors": [{"message": "LangGraph is unavailable"}]}
    result = graph.invoke(state)
    return {
        **result,
        "status": "completed_with_constraints" if result.get("constraints") else "completed",
    }
