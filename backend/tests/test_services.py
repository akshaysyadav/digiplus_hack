"""
Unit and Integration Tests for Zepto Support Ticket Decision Engine
"""

import pytest
from app.services import (
    data_service,
    similarity_service,
    order_context_service,
    decision_service,
    action_service,
    reply_service,
    log_service
)
from app.models.schemas import OrderContext, PrecedentMatch


def test_data_service_loading():
    """Verify all datasets load properly with exact record counts."""
    assert len(data_service.resolved_tickets_df) == 300
    assert len(data_service.new_tickets_df) == 30
    assert len(data_service.orders_df) == 30
    
    # Check ticket retrieval
    ticket = data_service.get_new_ticket_by_id("N-000")
    assert ticket is not None
    assert ticket["order_id"] == "ORD-9900"


def test_similarity_service():
    """Verify top-3 precedent retrieval returns valid matches."""
    precedents = similarity_service.get_top_k_precedents("milk packet missing from my order", k=3)
    assert len(precedents) == 3
    assert precedents[0].similarity_score == 1.0
    for p in precedents:
        assert p.precedent_id.startswith("H-")


def test_decision_auto_resolve_on_exact_agreement():
    """Verify AUTO_RESOLVE for exact precedent agreement and delivered order (N-005)."""
    precedents = [
        PrecedentMatch(
            precedent_id="H-1000", category="missing_item",
            description="milk packet missing", resolution_action="redelivery",
            resolution_note="item re-sent", similarity_score=1.0, csat=5
        ),
        PrecedentMatch(
            precedent_id="H-1007", category="missing_item",
            description="milk packet missing", resolution_action="redelivery",
            resolution_note="item re-sent", similarity_score=1.0, csat=4
        ),
        PrecedentMatch(
            precedent_id="H-1038", category="missing_item",
            description="milk packet missing", resolution_action="redelivery",
            resolution_note="item re-sent", similarity_score=1.0, csat=3
        ),
    ]
    order = OrderContext(
        order_id="ORD-9905", items=1, value_inr=412, delivery_time_min=41, delivery_status="delivered"
    )
    result = decision_service.evaluate("milk packet missing from my order", precedents, order)
    
    assert result.decision == "AUTO_RESOLVE"
    assert result.exact_action_agreement is True
    assert result.selected_action == "redelivery"
    # Confidence: 0.60*1.0 + 0.30*1.0 + 0.10*1.0 = 1.00
    assert result.confidence_score == 1.0


def test_guardrail_cancelled_order_blocks_redelivery():
    """Verify Guardrail: Cancelled order blocks redelivery even if precedents agree (N-002)."""
    precedents = [
        PrecedentMatch(
            precedent_id="H-1000", category="missing_item",
            description="milk packet missing", resolution_action="redelivery",
            resolution_note="item re-sent", similarity_score=1.0, csat=5
        ),
        PrecedentMatch(
            precedent_id="H-1007", category="missing_item",
            description="milk packet missing", resolution_action="redelivery",
            resolution_note="item re-sent", similarity_score=1.0, csat=4
        ),
        PrecedentMatch(
            precedent_id="H-1038", category="missing_item",
            description="milk packet missing", resolution_action="redelivery",
            resolution_note="item re-sent", similarity_score=1.0, csat=3
        ),
    ]
    order = OrderContext(
        order_id="ORD-9902", items=5, value_inr=999, delivery_time_min=42, delivery_status="cancelled"
    )
    result = decision_service.evaluate("milk packet missing from my order", precedents, order)
    
    assert result.decision == "HUMAN_REVIEW"
    assert result.guardrails.cancelled_redelivery_blocked is True
    assert "cancelled" in result.reasoning.lower()


def test_guardrail_precedent_disagreement_routes_to_human():
    """Verify precedent disagreement forces HUMAN_REVIEW (no guessing)."""
    precedents = [
        PrecedentMatch(
            precedent_id="H-1", category="wrong_item",
            description="wrong item", resolution_action="redelivery",
            resolution_note="re-sent", similarity_score=1.0, csat=4
        ),
        PrecedentMatch(
            precedent_id="H-2", category="wrong_item",
            description="wrong item", resolution_action="partial_refund",
            resolution_note="refunded", similarity_score=1.0, csat=4
        ),
        PrecedentMatch(
            precedent_id="H-3", category="wrong_item",
            description="wrong item", resolution_action="redelivery",
            resolution_note="re-sent", similarity_score=1.0, csat=3
        ),
    ]
    order = OrderContext(
        order_id="ORD-9901", items=2, value_inr=189, delivery_time_min=28, delivery_status="delivered"
    )
    result = decision_service.evaluate("wrong brand of rice delivered", precedents, order)
    
    assert result.decision == "HUMAN_REVIEW"
    assert result.exact_action_agreement is False


def test_guardrail_weak_similarity():
    """Verify weak similarity (< 0.65) forces HUMAN_REVIEW."""
    precedents = [
        PrecedentMatch(
            precedent_id="H-1", category="general",
            description="some text", resolution_action="full_refund",
            resolution_note="refunded", similarity_score=0.42, csat=4
        ),
        PrecedentMatch(
            precedent_id="H-2", category="general",
            description="some text", resolution_action="full_refund",
            resolution_note="refunded", similarity_score=0.35, csat=4
        ),
        PrecedentMatch(
            precedent_id="H-3", category="general",
            description="some text", resolution_action="full_refund",
            resolution_note="refunded", similarity_score=0.30, csat=4
        ),
    ]
    order = OrderContext(
        order_id="ORD-1234", items=1, value_inr=500, delivery_time_min=20, delivery_status="delivered"
    )
    result = decision_service.evaluate("novel unknown issue text", precedents, order)
    
    assert result.decision == "HUMAN_REVIEW"
    assert result.guardrails.similarity_threshold_passed is False


def test_refund_cap_guardrail():
    """Verify refund amount never exceeds order value."""
    order = OrderContext(
        order_id="ORD-9900", items=1, value_inr=500, delivery_time_min=24, delivery_status="delivered"
    )
    capped = order_context_service.cap_refund_amount(order, 800)
    assert capped == 500
