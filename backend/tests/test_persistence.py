"""
Unit and Integration Tests for Simulated Ticket JSON Persistence
"""

import json
import os
import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient

from app.main import app
from app.core.config import (
    SIMULATED_TICKETS_JSON,
    NEW_TICKETS_CSV,
    RESOLVED_TICKETS_CSV,
    ORDERS_CONTEXT_CSV
)
from app.services.data_service import DataService, data_service

client = TestClient(app)


@pytest.fixture(autouse=True)
def clean_persistence_state():
    data_service.clear_simulated_tickets(delete_storage=True)
    with patch("app.services.gemini_service.gemini_service.generate_reply_and_explanation", return_value=None):
        yield
    data_service.clear_simulated_tickets(delete_storage=True)


def test_backend_starts_without_json_file():
    """Verify backend starts safely when simulated_tickets.json does not exist."""
    if SIMULATED_TICKETS_JSON.exists():
        SIMULATED_TICKETS_JSON.unlink()

    ds = DataService()
    assert len(ds._simulated_tickets) == 0
    assert len(ds.get_all_new_tickets()) == 30


def test_simulated_ticket_created_and_persisted_to_file():
    """Verify creating a simulated ticket writes valid JSON to disk."""
    resp = client.post(
        "/api/tickets/simulate",
        json={"description": "milk packet missing from my order", "order_id": "ORD-9905"}
    )
    assert resp.status_code == 200
    ticket_id = resp.json()["ticket_id"]
    assert ticket_id == "SIM-001"

    # Verify file was written to disk
    assert SIMULATED_TICKETS_JSON.exists()
    with open(SIMULATED_TICKETS_JSON, "r", encoding="utf-8") as f:
        stored_data = json.load(f)
    assert isinstance(stored_data, list)
    assert len(stored_data) == 1
    assert stored_data[0]["ticket_id"] == "SIM-001"
    assert stored_data[0]["evaluation"]["decision"] == "AUTO_RESOLVE"


def test_ticket_survives_service_reload():
    """Simulate backend restart by creating a new DataService instance from persisted storage."""
    # Create SIM-001
    resp = client.post(
        "/api/tickets/simulate",
        json={"description": "milk packet missing from my order", "order_id": "ORD-9905"}
    )
    assert resp.status_code == 200

    # Simulate fresh backend startup
    new_ds = DataService()
    assert len(new_ds._simulated_tickets) == 1
    persisted_ticket = new_ds.get_new_ticket_by_id("SIM-001")
    assert persisted_ticket is not None
    assert persisted_ticket["ticket_id"] == "SIM-001"
    assert persisted_ticket["description"] == "milk packet missing from my order"
    assert persisted_ticket["order_id"] == "ORD-9905"


def test_sequential_id_generation_survives_restart():
    """Verify IDs continue sequentially after restart (e.g. SIM-001 -> restart -> SIM-002)."""
    # Create SIM-001
    resp1 = client.post(
        "/api/tickets/simulate",
        json={"description": "milk packet missing from my order", "order_id": "ORD-9905"}
    )
    assert resp1.status_code == 200
    assert resp1.json()["ticket_id"] == "SIM-001"

    # Reload data service (simulating backend restart)
    data_service.load_all_data()

    # Create next ticket -> must be SIM-002
    resp2 = client.post(
        "/api/tickets/simulate",
        json={"description": "got salted butter instead of unsalted", "order_id": "ORD-9929"}
    )
    assert resp2.status_code == 200
    assert resp2.json()["ticket_id"] == "SIM-002"

    # Reload again
    data_service.load_all_data()

    # Create third ticket -> must be SIM-003
    resp3 = client.post(
        "/api/tickets/simulate",
        json={"description": "the delivery person was rude", "order_id": "ORD-9908"}
    )
    assert resp3.status_code == 200
    assert resp3.json()["ticket_id"] == "SIM-003"


def test_get_tickets_api_includes_persisted_tickets_after_restart():
    """Verify GET /api/tickets and lane filtering work seamlessly after backend reload."""
    client.post(
        "/api/tickets/simulate",
        json={"description": "milk packet missing from my order", "order_id": "ORD-9905"}
    )
    client.post(
        "/api/tickets/simulate",
        json={"description": "got salted butter instead of unsalted", "order_id": "ORD-9929"}
    )

    # Reload backend state
    data_service.load_all_data()

    # GET /api/tickets should return 30 CSV + 2 persisted = 32 tickets
    list_resp = client.get("/api/tickets")
    assert list_resp.status_code == 200
    tickets = list_resp.json()
    assert len(tickets) == 32
    assert any(t["ticket_id"] == "SIM-001" for t in tickets)
    assert any(t["ticket_id"] == "SIM-002" for t in tickets)

    # Test auto_resolve lane
    auto_resp = client.get("/api/tickets?lane=auto_resolve")
    assert auto_resp.status_code == 200
    auto_tickets = auto_resp.json()
    assert any(t["ticket_id"] == "SIM-001" for t in auto_tickets)

    # Test human_review lane
    human_resp = client.get("/api/tickets?lane=human_review")
    assert human_resp.status_code == 200
    human_tickets = human_resp.json()
    assert any(t["ticket_id"] == "SIM-002" for t in human_tickets)


def test_get_ticket_detail_after_restart():
    """Verify GET /api/tickets/SIM-001 restores identical evaluation details after reload."""
    create_resp = client.post(
        "/api/tickets/simulate",
        json={"description": "milk packet missing from my order", "order_id": "ORD-9905"}
    )
    original_detail = create_resp.json()

    # Reload backend state
    data_service.load_all_data()

    detail_resp = client.get("/api/tickets/SIM-001")
    assert detail_resp.status_code == 200
    reloaded_detail = detail_resp.json()

    assert reloaded_detail["ticket_id"] == "SIM-001"
    assert reloaded_detail["evaluation"]["decision"] == original_detail["evaluation"]["decision"]
    assert reloaded_detail["evaluation"]["confidence_score"] == original_detail["evaluation"]["confidence_score"]
    assert reloaded_detail["evaluation"]["selected_action"] == original_detail["evaluation"]["selected_action"]
    assert reloaded_detail["draft_reply"]["subject"] == original_detail["draft_reply"]["subject"]
    assert reloaded_detail["draft_reply"]["body"] == original_detail["draft_reply"]["body"]


def test_corrupted_json_handled_safely_without_crashing():
    """Verify corrupted JSON storage does not crash backend startup."""
    SIMULATED_TICKETS_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(SIMULATED_TICKETS_JSON, "w", encoding="utf-8") as f:
        f.write("{ invalid json corrupted content [[[")

    ds = DataService()
    assert len(ds._simulated_tickets) == 0
    assert len(ds.get_all_new_tickets()) == 30


def test_non_list_json_handled_safely():
    """Verify non-list JSON (e.g. integer or object) falls back safely."""
    with open(SIMULATED_TICKETS_JSON, "w", encoding="utf-8") as f:
        f.write(json.dumps({"error": "invalid format"}))

    ds = DataService()
    assert len(ds._simulated_tickets) == 0
    assert len(ds.get_all_new_tickets()) == 30


def test_original_csv_datasets_remain_unmodified():
    """Verify the original CSV files are 100% untouched."""
    assert os.path.exists(RESOLVED_TICKETS_CSV)
    assert os.path.exists(NEW_TICKETS_CSV)
    assert os.path.exists(ORDERS_CONTEXT_CSV)

    ds = DataService()
    assert len(ds.resolved_tickets_df) == 300
    assert len(ds.new_tickets_df) == 30
    assert len(ds.orders_df) == 30
