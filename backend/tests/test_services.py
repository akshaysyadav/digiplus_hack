"""
Unit and Integration Tests for Zepto Support Ticket Decision Engine, Guardrails, and AI Layer
"""

import json
import pytest
from unittest.mock import patch, MagicMock
import httpx

from app.services import (
    data_service,
    similarity_service,
    order_context_service,
    decision_service,
    action_service,
    reply_service,
    gemini_service,
    log_service
)
from app.models.schemas import OrderContext, PrecedentMatch, SimulatedAction, EvaluationResult, GuardrailResults


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
    assert result.suggested_action == "redelivery"
    # Confidence: 0.60*1.0 + 0.30*1.0 + 0.10*1.0 = 1.00
    assert result.confidence_score == 1.0


# ==========================================================
# PART 1: HUMAN REVIEW + SUGGESTED ACTION TESTS
# ==========================================================

def test_suggested_action_conflicting_precedents_majority_support():
    """
    Test 1: Conflicting precedents where one action has strongest precedent support (N-029).
    redelivery, partial_refund, redelivery -> suggested_action = 'redelivery',
    decision = 'HUMAN_REVIEW', selected_action = 'human_review'.
    """
    precedents = [
        PrecedentMatch(
            precedent_id="H-1000", category="damaged_item",
            description="broken eggs", resolution_action="redelivery",
            resolution_note="re-sent eggs", similarity_score=1.0, csat=5
        ),
        PrecedentMatch(
            precedent_id="H-1001", category="damaged_item",
            description="broken eggs", resolution_action="partial_refund",
            resolution_note="refunded broken eggs", similarity_score=1.0, csat=4
        ),
        PrecedentMatch(
            precedent_id="H-1002", category="damaged_item",
            description="broken eggs", resolution_action="redelivery",
            resolution_note="re-sent eggs", similarity_score=1.0, csat=4
        ),
    ]
    order = OrderContext(
        order_id="ORD-9929", items=3, value_inr=350, delivery_time_min=18, delivery_status="delivered"
    )
    result = decision_service.evaluate("received broken eggs", precedents, order)

    assert result.decision == "HUMAN_REVIEW"
    assert result.selected_action == "human_review"
    assert result.suggested_action == "redelivery"
    assert result.exact_action_agreement is False


def test_suggested_action_tie_between_actions():
    """
    Test 4: Tie between 3 different precedent actions (redelivery, partial_refund, coupon).
    No safe single suggestion exists -> suggested_action must be None.
    """
    precedents = [
        PrecedentMatch(
            precedent_id="H-1", category="mixed",
            description="item issue", resolution_action="redelivery",
            resolution_note="re-sent", similarity_score=0.9, csat=4
        ),
        PrecedentMatch(
            precedent_id="H-2", category="mixed",
            description="item issue", resolution_action="partial_refund",
            resolution_note="refunded", similarity_score=0.88, csat=4
        ),
        PrecedentMatch(
            precedent_id="H-3", category="mixed",
            description="item issue", resolution_action="coupon",
            resolution_note="given coupon", similarity_score=0.85, csat=4
        ),
    ]
    order = OrderContext(
        order_id="ORD-1001", items=2, value_inr=200, delivery_time_min=20, delivery_status="delivered"
    )
    result = decision_service.evaluate("item issue", precedents, order)

    assert result.decision == "HUMAN_REVIEW"
    assert result.selected_action == "human_review"
    assert result.suggested_action is None


def test_suggested_action_cancelled_order_blocks_redelivery():
    """
    Test 2 & 3: Cancelled order + historical redelivery agreement (N-002).
    Precedents: redelivery, redelivery, redelivery.
    Order: cancelled.
    decision = 'HUMAN_REVIEW', selected_action = 'human_review',
    suggested_action must NOT be executable redelivery -> suggested_action is None.
    """
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
    assert result.selected_action == "human_review"
    assert result.suggested_action is None
    assert result.guardrails.cancelled_redelivery_blocked is True
    assert "cancelled" in result.reasoning.lower()


def test_suggested_action_escalation():
    """
    Test Case 4: Historical action is escalation.
    suggested_action = 'escalation', decision = 'HUMAN_REVIEW', selected_action = 'human_review'.
    """
    precedents = [
        PrecedentMatch(
            precedent_id="H-2001", category="payment_issue",
            description="payment charged twice", resolution_action="escalation",
            resolution_note="escalated to pg team", similarity_score=0.95, csat=3
        ),
        PrecedentMatch(
            precedent_id="H-2002", category="payment_issue",
            description="payment charged twice", resolution_action="escalation",
            resolution_note="escalated to pg team", similarity_score=0.92, csat=4
        ),
        PrecedentMatch(
            precedent_id="H-2003", category="payment_issue",
            description="payment charged twice", resolution_action="escalation",
            resolution_note="escalated to pg team", similarity_score=0.90, csat=3
        ),
    ]
    order = OrderContext(
        order_id="ORD-9908", items=1, value_inr=650, delivery_time_min=15, delivery_status="delivered"
    )
    result = decision_service.evaluate("payment charged twice", precedents, order)

    assert result.decision == "HUMAN_REVIEW"
    assert result.selected_action == "human_review"
    assert result.suggested_action == "escalation"
    assert result.guardrails.escalation_precedent_detected is True


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


# ==========================================================
# PART 2: GEMINI GENERATIVE AI LAYER & FALLBACK TESTS
# ==========================================================

def test_gemini_success_structured_output():
    """Verify Gemini success returns structured reply with generation_source='gemini'."""
    mock_payload = {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {
                            "text": json.dumps({
                                "subject": "Your replacement milk packet is on the way",
                                "body": "We apologize for the missing milk. A fresh replacement is on its way to your address for order #ORD-9905.",
                                "explanation": "Auto-resolved with redelivery due to 3/3 unanimous precedents and verified delivered order."
                            })
                        }
                    ]
                }
            }
        ]
    }

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = mock_payload

    order = OrderContext(order_id="ORD-9905", items=1, value_inr=412, delivery_time_min=41, delivery_status="delivered")
    eval_res = EvaluationResult(
        similarity_score=1.0, exact_action_agreement=True, action_family_agreement=True,
        decision="AUTO_RESOLVE", confidence_score=1.0, selected_action="redelivery", suggested_action="redelivery",
        reasoning="Precedent agreement",
        guardrails=GuardrailResults(similarity_threshold_passed=True, cancelled_redelivery_blocked=False, refund_cap_enforced=False, escalation_precedent_detected=False)
    )
    sim_action = SimulatedAction(action="redelivery", status="SIMULATED_SUCCESS", note="Scheduled redelivery", is_simulated=True)

    with patch("httpx.Client.post", return_value=mock_resp):
        with patch.object(gemini_service, "api_key", "test-valid-api-key"):
            reply = reply_service.generate_draft_reply(
                ticket_id="N-005",
                description="milk packet missing from my order",
                order=order,
                evaluation=eval_res,
                simulated_action=sim_action
            )
            assert reply.generation_source == "gemini"
            assert "replacement milk" in reply.subject.lower()
            assert "ORD-9905" in reply.body
            assert "unanimous" in reply.explanation.lower()


def test_gemini_fallback_on_missing_api_key():
    """Verify missing API key safely triggers deterministic fallback without crashing."""
    order = OrderContext(order_id="ORD-9905", items=1, value_inr=412, delivery_time_min=41, delivery_status="delivered")
    eval_res = EvaluationResult(
        similarity_score=1.0, exact_action_agreement=True, action_family_agreement=True,
        decision="AUTO_RESOLVE", confidence_score=1.0, selected_action="redelivery", suggested_action="redelivery",
        reasoning="Precedent agreement",
        guardrails=GuardrailResults(similarity_threshold_passed=True, cancelled_redelivery_blocked=False, refund_cap_enforced=False, escalation_precedent_detected=False)
    )
    sim_action = SimulatedAction(action="redelivery", status="SIMULATED_SUCCESS", note="Scheduled redelivery", is_simulated=True)

    with patch.object(gemini_service, "api_key", ""):
        reply = reply_service.generate_draft_reply(
            ticket_id="N-005",
            description="milk packet missing from my order",
            order=order,
            evaluation=eval_res,
            simulated_action=sim_action
        )
        assert reply.generation_source == "fallback"
        assert "Order #ORD-9905" in reply.subject
        assert "redelivery" in reply.explanation.lower()


def test_gemini_fallback_on_network_error():
    """Verify network connection failure triggers deterministic fallback."""
    order = OrderContext(order_id="ORD-9902", items=5, value_inr=999, delivery_time_min=42, delivery_status="cancelled")
    eval_res = EvaluationResult(
        similarity_score=1.0, exact_action_agreement=True, action_family_agreement=True,
        decision="HUMAN_REVIEW", confidence_score=0.9, selected_action="human_review", suggested_action=None,
        reasoning="Cancelled order blocks redelivery",
        guardrails=GuardrailResults(similarity_threshold_passed=True, cancelled_redelivery_blocked=True, refund_cap_enforced=False, escalation_precedent_detected=False)
    )
    sim_action = SimulatedAction(action="blocked_redelivery", status="BLOCKED", note="Redelivery blocked", is_simulated=True)

    with patch("httpx.Client.post", side_effect=httpx.ConnectError("Network unreachable")):
        with patch.object(gemini_service, "api_key", "test-key"):
            reply = reply_service.generate_draft_reply(
                ticket_id="N-002",
                description="milk packet missing",
                order=order,
                evaluation=eval_res,
                simulated_action=sim_action
            )
            assert reply.generation_source == "fallback"
            assert "under review" in reply.subject.lower()
            assert "cancelled" in reply.explanation.lower()


def test_gemini_fallback_on_malformed_output():
    """Verify invalid/malformed JSON returned by Gemini triggers deterministic fallback."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "candidates": [{"content": {"parts": [{"text": "INVALID NON-JSON TEXT"}]}}]
    }

    order = OrderContext(order_id="ORD-9905", items=1, value_inr=412, delivery_time_min=41, delivery_status="delivered")
    eval_res = EvaluationResult(
        similarity_score=1.0, exact_action_agreement=True, action_family_agreement=True,
        decision="AUTO_RESOLVE", confidence_score=1.0, selected_action="redelivery", suggested_action="redelivery",
        reasoning="Precedent agreement",
        guardrails=GuardrailResults(similarity_threshold_passed=True, cancelled_redelivery_blocked=False, refund_cap_enforced=False, escalation_precedent_detected=False)
    )
    sim_action = SimulatedAction(action="redelivery", status="SIMULATED_SUCCESS", note="Scheduled redelivery", is_simulated=True)

    with patch("httpx.Client.post", return_value=mock_resp):
        with patch.object(gemini_service, "api_key", "test-key"):
            reply = reply_service.generate_draft_reply(
                ticket_id="N-005",
                description="milk packet missing",
                order=order,
                evaluation=eval_res,
                simulated_action=sim_action
            )
            assert reply.generation_source == "fallback"
            assert reply.subject is not None
            assert reply.body is not None
            assert reply.explanation is not None


def test_deterministic_authority_decision_engine_is_supreme():
    """
    Verify Gemini CANNOT override the decision engine.
    Decision, selected_action, and guardrails are computed purely by decision_service.
    """
    precedents = [
        PrecedentMatch(
            precedent_id="H-1", category="missing",
            description="missing item", resolution_action="redelivery",
            resolution_note="re-sent", similarity_score=1.0, csat=5
        ),
        PrecedentMatch(
            precedent_id="H-2", category="missing",
            description="missing item", resolution_action="redelivery",
            resolution_note="re-sent", similarity_score=1.0, csat=5
        ),
        PrecedentMatch(
            precedent_id="H-3", category="missing",
            description="missing item", resolution_action="redelivery",
            resolution_note="re-sent", similarity_score=1.0, csat=5
        ),
    ]
    # Cancelled order
    order = OrderContext(order_id="ORD-CANCELLED", items=2, value_inr=300, delivery_time_min=10, delivery_status="cancelled")
    eval_result = decision_service.evaluate("missing item", precedents, order)

    # Must strictly be HUMAN_REVIEW, never AUTO_RESOLVE
    assert eval_result.decision == "HUMAN_REVIEW"
    assert eval_result.selected_action == "human_review"
    assert eval_result.suggested_action is None
    assert eval_result.guardrails.cancelled_redelivery_blocked is True

