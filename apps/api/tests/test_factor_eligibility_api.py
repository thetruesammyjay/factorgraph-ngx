from fastapi.testclient import TestClient

from app.main import app


def test_factor_api_returns_eligibility_instead_of_placeholder_statistics():
    client = TestClient(app)
    response = client.get("/api/v1/factors")

    assert response.status_code == 200
    items = {item["factor"]: item for item in response.json()["items"]}
    assert items["market"]["status"] == "eligible"
    assert items["liquidity"]["status"] == "blocked"
    assert "annualised_return" not in items["market"]

    history = client.get("/api/v1/factors/market/history").json()
    assert len(history["items"]) == 24
    assert "market_excess_return" in history["items"][0]
    assert history["dataset_version"] == "ngx-public-data-2023-2024-pilot-v1"

    statistics = client.get("/api/v1/factors/market/statistics").json()
    assert statistics["statistics"]["observations"] == 23
    assert statistics["reason"] is None
