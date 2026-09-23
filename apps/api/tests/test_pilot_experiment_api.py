from fastapi.testclient import TestClient

from app.main import app


def test_latest_pilot_experiment_exposes_computed_results():
    response = TestClient(app).get("/api/v1/experiments/pilot/latest")

    assert response.status_code == 200
    payload = response.json()
    assert payload["experiment_id"] == "ngx-public-data-2024-pilot-v1"
    assert payload["coverage"]["observations"] == 3255
    statuses = {
        item["factor"]: item["status"] for item in payload["factor_eligibility"]
    }
    assert statuses["momentum"] == "preliminary"
    assert statuses["liquidity"] == "blocked"
    assert len(payload["market_proxy"]) == 12
    assert payload["market_proxy_statistics"]["marked_price"]["observations"] == 11
