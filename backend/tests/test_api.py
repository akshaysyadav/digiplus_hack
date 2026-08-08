"""
API Endpoint Integration Tests
"""

import pytest
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


def test_list_tickets_invalid_lane():
    response = client.get("/api/tickets?lane=unknown_lane")
    assert response.status_code == 400
    assert "Invalid lane filter" in response.json()["detail"]


def test_get_ticket_detail():
    response = client.get("/api/tickets/N-005")
    assert response.status_code == 200
    data = response.json()
    assert data["ticket_id"] == "N-005"
    assert data["order"]["order_id"] == "ORD-9905"
    assert len(data["precedents"]) == 3
    assert data["evaluation"]["decision"] == "AUTO_RESOLVE"
    assert data["evaluation"]["selected_action"] == "redelivery"
    assert data["evaluation"]["suggested_action"] == "redelivery"
    assert data["simulated_action"]["status"] == "SIMULATED_SUCCESS"
    assert "explanation" in data["draft_reply"]
    assert data["draft_reply"]["generation_source"] in ["gemini", "fallback"]


def test_get_ticket_detail_human_review_n029():
    response = client.get("/api/tickets/N-029")
    assert response.status_code == 200
    data = response.json()
    assert data["ticket_id"] == "N-029"
    assert data["evaluation"]["decision"] == "HUMAN_REVIEW"
    assert data["evaluation"]["selected_action"] == "human_review"
    assert data["evaluation"]["suggested_action"] == "redelivery"


def test_get_ticket_detail_cancelled_guardrail_n002():
    response = client.get("/api/tickets/N-002")
    assert response.status_code == 200
    data = response.json()
    assert data["ticket_id"] == "N-002"
    assert data["evaluation"]["decision"] == "HUMAN_REVIEW"
    assert data["evaluation"]["selected_action"] == "human_review"
    assert data["evaluation"]["suggested_action"] is None
    assert data["evaluation"]["guardrails"]["cancelled_redelivery_blocked"] is True


def test_get_ticket_detail_not_found():
    response = client.get("/api/tickets/INVALID-999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


def test_evaluate_and_decision_log():
    # Evaluate ticket
    eval_resp = client.post("/api/tickets/N-002/evaluate")
    assert eval_resp.status_code == 200
    eval_data = eval_resp.json()
    assert eval_data["evaluation"]["decision"] == "HUMAN_REVIEW"
    assert eval_data["evaluation"]["selected_action"] == "human_review"
    assert eval_data["evaluation"]["suggested_action"] is None
    assert eval_data["evaluation"]["guardrails"]["cancelled_redelivery_blocked"] is True

    # Check decision log
    log_resp = client.get("/api/decisions")
    assert log_resp.status_code == 200
    logs = log_resp.json()
    assert len(logs) > 0
    n002_log = next((l for l in logs if l["ticket_id"] == "N-002"), None)
    assert n002_log is not None
    assert n002_log["decision"] == "HUMAN_REVIEW"
    assert n002_log["selected_action"] == "human_review"
    assert n002_log["suggested_action"] is None


def test_resolve_auto_resolve_ticket():
    # N-005 is AUTO_RESOLVE
    resp = client.post("/api/tickets/N-005/resolve")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "SIMULATED_SUCCESS"
    assert data["action"] == "redelivery"


def test_resolve_human_review_ticket_blocked():
    # N-002 is HUMAN_REVIEW -> should be blocked with 400
    resp = client.post("/api/tickets/N-002/resolve")
    assert resp.status_code == 400
    assert "Cannot auto-resolve" in resp.json()["detail"]

