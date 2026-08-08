"""
API Endpoint Integration Tests
"""

import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app
from app.services.data_service import data_service

client = TestClient(app)


@pytest.fixture(autouse=True)
def clean_test_state():
    data_service.clear_simulated_tickets()
    # Mock network Gemini call during batch API tests for fast deterministic runs
    with patch("app.services.gemini_service.gemini_service.generate_reply_and_explanation", return_value=None):
        yield
    data_service.clear_simulated_tickets()



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


# --- Real-Time Simulation & Orders Endpoint Tests ---

def test_get_orders_endpoint():
    resp = client.get("/api/orders")
    assert resp.status_code == 200
    orders = resp.json()
    assert len(orders) == 30
    assert any(o["order_id"] == "ORD-9905" for o in orders)
    assert any(o["order_id"] == "ORD-9902" for o in orders)


def test_simulate_ticket_auto_resolve_scenario1():
    # Scenario 1: Strong match on delivered order -> AUTO_RESOLVE
    payload = {
        "description": "milk packet missing from my order",
        "order_id": "ORD-9905"
    }
    resp = client.post("/api/tickets/simulate", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["ticket_id"].startswith("SIM-")
    assert data["description"] == "milk packet missing from my order"
    assert data["order"]["order_id"] == "ORD-9905"
    assert data["evaluation"]["decision"] == "AUTO_RESOLVE"
    assert data["evaluation"]["selected_action"] == "redelivery"
    assert data["simulated_action"]["status"] == "SIMULATED_SUCCESS"


def test_simulate_ticket_cancelled_guardrail_scenario2():
    # Scenario 2: Strong match on CANCELLED order -> HUMAN_REVIEW (guardrail triggered)
    payload = {
        "description": "milk packet missing from my order",
        "order_id": "ORD-9902"
    }
    resp = client.post("/api/tickets/simulate", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["evaluation"]["decision"] == "HUMAN_REVIEW"
    assert data["evaluation"]["selected_action"] == "human_review"
    assert data["evaluation"]["suggested_action"] is None
    assert data["evaluation"]["guardrails"]["cancelled_redelivery_blocked"] is True
    # Customer draft must not promise redelivery
    assert "re-delivery" not in data["draft_reply"]["body"].lower()


def test_simulate_ticket_novel_query_weak_similarity_scenario3():
    # Scenario 3: Novel query with weak similarity -> HUMAN_REVIEW
    payload = {
        "description": "the delivery person was rude and shouted at me",
        "order_id": "ORD-9908"
    }
    resp = client.post("/api/tickets/simulate", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["evaluation"]["decision"] == "HUMAN_REVIEW"
    assert data["evaluation"]["guardrails"]["similarity_threshold_passed"] is False


def test_simulate_ticket_conflicting_precedents_scenario4():
    # Scenario 4: Conflicting precedents -> HUMAN_REVIEW
    payload = {
        "description": "got salted butter instead of unsalted",
        "order_id": "ORD-9929"
    }
    resp = client.post("/api/tickets/simulate", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["evaluation"]["decision"] == "HUMAN_REVIEW"
    assert data["evaluation"]["selected_action"] == "human_review"
    assert data["evaluation"]["suggested_action"] == "redelivery"


def test_simulate_ticket_validation_errors():
    # Invalid order_id
    resp_invalid_order = client.post(
        "/api/tickets/simulate",
        json={"description": "milk missing", "order_id": "ORD-999999"}
    )
    assert resp_invalid_order.status_code == 400
    assert "not found" in resp_invalid_order.json()["detail"].lower()

    # Empty description
    resp_empty_desc = client.post(
        "/api/tickets/simulate",
        json={"description": "   ", "order_id": "ORD-9905"}
    )
    assert resp_empty_desc.status_code == 400
    assert "empty" in resp_empty_desc.json()["detail"].lower()


def test_simulate_ticket_in_memory_persistence_and_resolve():
    # Simulate a ticket
    payload = {
        "description": "milk packet missing from my order",
        "order_id": "ORD-9905"
    }
    resp = client.post("/api/tickets/simulate", json=payload)
    assert resp.status_code == 200
    sim_id = resp.json()["ticket_id"]

    # Check detail endpoint for SIM-xxx
    detail_resp = client.get(f"/api/tickets/{sim_id}")
    assert detail_resp.status_code == 200
    assert detail_resp.json()["ticket_id"] == sim_id

    # Check that it appears in GET /api/tickets
    list_resp = client.get("/api/tickets")
    assert list_resp.status_code == 200
    all_tickets = list_resp.json()
    assert any(t["ticket_id"] == sim_id for t in all_tickets)

    # Check resolve on AUTO_RESOLVE simulated ticket
    resolve_resp = client.post(f"/api/tickets/{sim_id}/resolve")
    assert resolve_resp.status_code == 200
    assert resolve_resp.json()["status"] == "SIMULATED_SUCCESS"


