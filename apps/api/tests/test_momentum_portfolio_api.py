from fastapi.testclient import TestClient

from app.main import app

EXPERIMENT_ID = "ngx-public-data-2024-pilot-v1"


def test_momentum_portfolio_endpoints_return_computed_pilot():
    client = TestClient(app)

    summary = client.get(f"/api/v1/portfolios/{EXPERIMENT_ID}")
    assert summary.status_code == 200
    assert summary.json()["status"] == "preliminary"
    assert summary.json()["coverage"]["invested_months"] > 0

    holdings = client.get(f"/api/v1/portfolios/{EXPERIMENT_ID}/holdings").json()
    assert holdings["items"]
    assert set(holdings["items"][0]) == {
        "observation_month",
        "ticker",
        "rank",
        "formation_return",
        "weight",
    }

    performance = client.get(
        f"/api/v1/portfolios/{EXPERIMENT_ID}/performance"
    ).json()
    assert len(performance["items"]) == 12


def test_unknown_portfolio_experiment_returns_404():
    response = TestClient(app).get("/api/v1/portfolios/unknown")
    assert response.status_code == 404
