from fastapi.testclient import TestClient

from app.main import app


def test_factor_api_returns_eligibility_instead_of_placeholder_statistics():
    client = TestClient(app)
    response = client.get("/api/v1/factors")

    assert response.status_code == 200
    items = {item["factor"]: item for item in response.json()["items"]}
    assert items["market"]["status"] == "preliminary"
    assert items["liquidity"]["status"] == "blocked"
    assert "annualised_return" not in items["market"]

    history = client.get("/api/v1/factors/market/history").json()
    assert len(history["items"]) == 12
    assert history["dataset_version"] == "ngx-public-data-2024-pilot-v1"
