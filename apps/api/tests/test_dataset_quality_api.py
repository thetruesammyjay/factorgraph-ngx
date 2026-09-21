from fastapi.testclient import TestClient

from app.main import app


def test_latest_dataset_quality_exposes_blocked_research_gate():
    response = TestClient(app).get("/api/v1/datasets/quality/latest")

    assert response.status_code == 200
    payload = response.json()
    assert payload["structural_status"] == "passed"
    assert payload["research_readiness"].startswith("blocked_")
    assert payload["price_universe_expansion"] == "proceed_with_stale_price_controls"
    assert payload["valid_dol_document_count"] == 217
    assert payload["observation_count"] >= 600
    assert payload["missing_liquidity_fields"]["volume"] == payload["observation_count"]
