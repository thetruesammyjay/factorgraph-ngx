from fastapi.testclient import TestClient

from app.main import app


def test_companies_api_uses_actual_pilot_universe():
    client = TestClient(app)
    payload = client.get("/api/v1/companies").json()

    assert payload["total"] == 15
    assert payload["source"] == "validated_public_data_pilot"
    assert len(payload["dataset_version"].removeprefix("ngx-public-2024-")) == 12
    assert {row["ticker"] for row in payload["items"]} >= {"AIICO", "DANGCEM", "GTCO"}


def test_company_prices_and_fundamentals_are_observed_data():
    client = TestClient(app)
    prices = client.get("/api/v1/companies/DANGCEM/prices").json()
    fundamentals = client.get("/api/v1/companies/DANGCEM/fundamentals").json()

    assert prices["frequency"] == "monthly"
    assert len(prices["items"]) == 12
    assert len(fundamentals["items"]) == 2
    assert fundamentals["items"][-1]["source_id"] == "dangcem-annual-report-2023"


def test_company_api_rejects_ticker_outside_pilot():
    response = TestClient(app).get("/api/v1/companies/NOTREAL")
    assert response.status_code == 404
