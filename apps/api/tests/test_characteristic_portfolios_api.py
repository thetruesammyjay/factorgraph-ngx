from fastapi.testclient import TestClient

from app.main import app


def test_size_and_value_portfolio_endpoints_expose_computed_preliminary_results():
    client = TestClient(app)
    history = client.get("/api/v1/factors/size/history")
    statistics = client.get("/api/v1/factors/value/statistics")

    assert history.status_code == 200
    assert history.json()["status"] == "preliminary"
    assert history.json()["coverage"]["months_with_size_spread"] == 22
    assert history.json()["items"]
    assert statistics.status_code == 200
    assert statistics.json()["statistics"]["newey_west_t"] is not None
    assert "partial point-in-time" in statistics.json()["reason"]
