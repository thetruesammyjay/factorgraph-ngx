from fastapi.testclient import TestClient

from app.main import app


def test_regime_endpoints_do_not_return_placeholder_results():
    client = TestClient(app)
    payload = client.get("/api/v1/regimes").json()

    assert payload["status"] == "blocked"
    assert payload["items"] == []
    assert payload["model"] is None
    assert payload["coverage"]["monthly_endpoints"] == 24
    assert payload["coverage"]["minimum_observations"] == 36

    timeline = client.get("/api/v1/regimes/timeline").json()
    assert timeline["status"] == "blocked"
    assert timeline["dataset_version"] == "ngx-public-data-2023-2024-pilot-v1"
    assert "24 monthly endpoints" in timeline["reason"]
    assert timeline["coverage"]["feature_observations"] == 21
