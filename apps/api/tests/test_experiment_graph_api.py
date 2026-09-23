from fastapi.testclient import TestClient

from app.main import app


def test_experiment_run_returns_ordered_graph_trace():
    client = TestClient(app)
    created = client.post(
        "/api/v1/experiments",
        json={"name": "graph trace test", "factors": ["market"]},
    )
    assert created.status_code == 201
    experiment_id = created.json()["id"]

    response = client.post(f"/api/v1/experiments/{experiment_id}/run")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "completed"
    assert payload["last_completed_node"] == "persist_results"
    assert [item["node"] for item in payload["execution_trace"]] == [
        "prepare_dataset",
        "factor_construction",
        "validation",
        "regime_estimation",
        "stock_ranking",
        "portfolio_construction",
        "historical_backtest",
        "benchmark_comparison",
        "persist_results",
    ]
    assert payload["execution_trace"][0]["outputs"]["observations"] > 0
    assert payload["node_outputs"]["regime_estimation"]["status"] == "blocked"
    assert payload["node_outputs"]["persist_results"]["fingerprint"]

    stored = client.get(f"/api/v1/experiments/{experiment_id}")
    assert stored.json()["status"] == "completed"

    latest = client.get(f"/api/v1/experiments/{experiment_id}/run")
    assert latest.status_code == 200
    assert latest.json()["last_completed_node"] == "persist_results"
    assert len(latest.json()["execution_trace"]) == 9
    assert latest.json()["node_outputs"]["prepare_dataset"]["tickers"] == 15

    node = client.get(f"/api/v1/experiments/{experiment_id}/run/nodes/regime_estimation")
    assert node.status_code == 200
    assert node.json()["outputs"]["status"] == "blocked"


def test_experiment_run_rejects_unknown_id():
    response = TestClient(app).post("/api/v1/experiments/exp_missing/run")

    assert response.status_code == 404


def test_latest_experiment_run_rejects_unknown_id():
    response = TestClient(app).get("/api/v1/experiments/exp_missing/run")

    assert response.status_code == 404


def test_experiment_node_run_rejects_unknown_node():
    client = TestClient(app)
    created = client.post(
        "/api/v1/experiments",
        json={"name": "node lookup test", "factors": ["market"]},
    )
    experiment_id = created.json()["id"]
    client.post(f"/api/v1/experiments/{experiment_id}/run")

    response = client.get(f"/api/v1/experiments/{experiment_id}/run/nodes/not_a_node")

    assert response.status_code == 404
