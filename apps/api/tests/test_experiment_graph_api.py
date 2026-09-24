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
    assert [item["sequence"] for item in payload["execution_trace"]] == list(range(1, 10))
    assert payload["execution_trace"][0]["outputs"]["observations"] > 0
    assert payload["execution_trace"][0]["outputs"]["requested_period"] == [
        "2024-01-02",
        "2024-12-31",
    ]
    assert payload["execution_trace"][0]["outputs"]["portfolio_size"] == 10
    assert payload["node_outputs"]["factor_construction"]["requested_factors"] == ["market"]
    assert payload["node_outputs"]["factor_construction"]["selected_factors"] == ["market"]
    assert payload["node_outputs"]["factor_construction"]["factor_statuses"]["liquidity"] == "blocked"
    assert payload["node_outputs"]["validation"]["price_observations"] == 6375
    assert payload["node_outputs"]["validation"]["fundamental_warnings"] == 1
    assert payload["node_outputs"]["regime_estimation"]["status"] == "blocked"
    assert payload["node_outputs"]["persist_results"]["fingerprint"]
    assert len(payload["run_fingerprint"]) == 64
    assert payload["node_outputs"]["persist_results"]["run_fingerprint"] == payload["run_fingerprint"]

    stored = client.get(f"/api/v1/experiments/{experiment_id}")
    assert stored.json()["status"] == "completed"

    latest = client.get(f"/api/v1/experiments/{experiment_id}/run")
    assert latest.status_code == 200
    assert latest.json()["last_completed_node"] == "persist_results"
    assert len(latest.json()["execution_trace"]) == 9
    assert latest.json()["node_outputs"]["prepare_dataset"]["tickers"] == 15

    manifest = client.get(f"/api/v1/experiments/{experiment_id}/manifest")
    assert manifest.status_code == 200
    assert manifest.json()["run_fingerprint"] == payload["run_fingerprint"]
    assert manifest.json()["configuration"]["factors"] == ["market"]
    assert manifest.json()["execution"]["node_count"] == 9

    node = client.get(f"/api/v1/experiments/{experiment_id}/run/nodes/regime_estimation")
    assert node.status_code == 200
    assert node.json()["sequence"] == 4
    assert node.json()["outputs"]["status"] == "blocked"


def test_experiment_run_rejects_unknown_id():
    response = TestClient(app).post("/api/v1/experiments/exp_missing/run")

    assert response.status_code == 404


def test_experiment_run_surfaces_requested_factor_constraints():
    client = TestClient(app)
    created = client.post(
        "/api/v1/experiments",
        json={"name": "liquidity constraint test", "factors": ["liquidity"]},
    )
    experiment_id = created.json()["id"]

    response = client.post(f"/api/v1/experiments/{experiment_id}/run")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "completed_with_constraints"
    assert payload["message"] == "Research graph completed with constraints."
    assert payload["constraints"][0]["factor"] == "liquidity"
    assert payload["constraints"][0]["status"] == "blocked"


def test_identical_experiment_inputs_share_a_reproducibility_fingerprint():
    client = TestClient(app)
    first = client.post(
        "/api/v1/experiments",
        json={"name": "fingerprint test one", "factors": ["market"]},
    ).json()
    second = client.post(
        "/api/v1/experiments",
        json={"name": "fingerprint test two", "factors": ["market"]},
    ).json()

    first_run = client.post(f"/api/v1/experiments/{first['id']}/run").json()
    second_run = client.post(f"/api/v1/experiments/{second['id']}/run").json()

    assert first_run["run_fingerprint"] == second_run["run_fingerprint"]


def test_latest_experiment_run_rejects_unknown_id():
    response = TestClient(app).get("/api/v1/experiments/exp_missing/run")

    assert response.status_code == 404


def test_experiment_plan_exposes_factor_gates_before_execution():
    client = TestClient(app)
    created = client.post(
        "/api/v1/experiments",
        json={"name": "preflight plan test", "factors": ["market", "liquidity"]},
    )
    assert created.status_code == 201
    experiment_id = created.json()["id"]

    response = client.get(f"/api/v1/experiments/{experiment_id}/plan")

    assert response.status_code == 200
    payload = response.json()
    assert payload["experiment_id"] == experiment_id
    assert payload["requested_factors"] == ["market", "liquidity"]
    assert payload["factor_statuses"] == {"market": "eligible", "liquidity": "blocked"}
    assert payload["constraints"][0]["factor"] == "liquidity"
    assert len(payload["planned_nodes"]) == 9
    assert payload["planned_nodes"][0] == "prepare_dataset"
    assert len(payload["run_fingerprint"]) == 64
    assert payload["configuration"]["factors"] == ["market", "liquidity"]


def test_experiment_plan_rejects_unknown_id():
    response = TestClient(app).get("/api/v1/experiments/exp_missing/plan")

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
