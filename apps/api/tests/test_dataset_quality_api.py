from fastapi.testclient import TestClient

from app.main import app


def test_latest_dataset_quality_exposes_blocked_research_gate():
    response = TestClient(app).get("/api/v1/datasets/quality/latest")

    assert response.status_code == 200
    payload = response.json()
    assert payload["structural_status"] == "passed"
    assert payload["research_readiness"].startswith("blocked_")
    assert payload["observation_count"] == 54
    assert payload["missing_liquidity_fields"]["volume"] == 54
