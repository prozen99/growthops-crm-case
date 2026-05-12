from fastapi.testclient import TestClient

from api import app
from main import main


client = TestClient(app)


def setup_module() -> None:
    main()


def test_health_endpoint_success():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_lead_scores_endpoint_success():
    response = client.get("/lead-scores")

    assert response.status_code == 200
    assert len(response.json()) == 12


def test_campaign_metrics_endpoint_success():
    response = client.get("/campaign-metrics")

    assert response.status_code == 200
    assert len(response.json()) == 4


def test_data_quality_report_endpoint_success():
    response = client.get("/data-quality-report")

    assert response.status_code == 200
    assert any(row["issue_type"] == "suspicious_bot_behavior" for row in response.json())


def test_missing_lead_score_returns_404():
    response = client.get("/lead-scores/UNKNOWN_LEAD")

    assert response.status_code == 404
