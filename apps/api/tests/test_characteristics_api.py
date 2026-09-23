from fastapi.testclient import TestClient

from app.main import app


def test_size_and_value_characteristic_endpoints_expose_eligible_and_excluded_rows():
    client = TestClient(app)
    size = client.get("/api/v1/factors/size/characteristics").json()
    value = client.get("/api/v1/factors/value/characteristics").json()

    assert size["status"] == "preliminary"
    assert size["coverage"]["fundamental_tickers"] == 4
    assert len(size["items"]) == 4
    assert len(value["items"]) == 3
    assert any(
        row["ticker"] == "MTNN"
        and row["value_exclusion_reason"] == "non_positive_or_missing_book_equity"
        for row in value["excluded"]
    )


def test_characteristics_reject_non_characteristic_factor():
    response = TestClient(app).get("/api/v1/factors/market/characteristics")
    assert response.status_code == 400
