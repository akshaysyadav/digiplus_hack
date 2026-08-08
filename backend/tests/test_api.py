"""
API Endpoint Integration Tests
"""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "online"


def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_list_tickets_all():
    response = client.get("/api/tickets")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 30


def test_list_tickets_lane_filter():
    # Auto-resolve lane
    resp_auto = client.get("/api/tickets?lane=auto_resolve")
    assert resp_auto.status_code == 200
    auto_data = resp_auto.json()
    assert len(auto_data) > 0
    for item in auto_data:
        assert item["decision"] == "AUTO_RESOLVE"

    # Human-review lane
    resp_human = client.get("/api/tickets?lane=human_review")
    assert resp_human.status_code == 200
    human_data = resp_human.json()
    assert len(human_data) > 0
    for item in human_data:
        assert item["decision"] == "HUMAN_REVIEW"

    # Total should sum to 30
    assert len(auto_data) + len(human_data) == 30


def test_get_ticket_detail():
    response = client.get("/api/tickets/N-005")
    assert response.status_code == 200
    data = response.json()
    assert data["ticket_id"] == "N-005"
    assert data["order"]["order_id"] == "ORD-9905"
    assert len(data["precedents"]) == 3
    assert data["evaluation"]["decision"] == "AUTO_RESOLVE"
    assert data["simulated_action"]["status"] == "SIMULATED_SUCCESS"
    assert "explanation" in data["draft_reply"]


def test_evaluate_and_decision_log():
    # Evaluate ticket
    eval_resp = client.post("/api/tickets/N-002/evaluate")
    assert eval_resp.status_code == 200
    eval_data = eval_resp.json()
    assert eval_data["evaluation"]["decision"] == "HUMAN_REVIEW"
    assert eval_data["evaluation"]["guardrails"]["cancelled_redelivery_blocked"] is True

    # Check decision log
    log_resp = client.get("/api/decisions")
    assert log_resp.status_code == 200
    logs = log_resp.json()
    assert len(logs) > 0
    n002_log = next((l for l in logs if l["ticket_id"] == "N-002"), None)
    assert n002_log is not None
    assert n002_log["decision"] == "HUMAN_REVIEW"
