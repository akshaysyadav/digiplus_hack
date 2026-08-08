"""
Tickets API Routes

Provides endpoints for:
- Listing incoming tickets (with optional lane filtering: all, auto_resolve, human_review)
- Fetching full ticket details with order context, precedents, evaluation, simulated action, and draft reply
- Evaluating a ticket end-to-end
- Resolving/approving simulated actions on a ticket (strictly guards against resolving HUMAN_REVIEW tickets)
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from app.models.schemas import (
    TicketDetailResponse,
    TicketListItem,
    SimulatedAction
)
from app.services import (
    data_service,
    similarity_service,
    order_context_service,
    decision_service,
    action_service,
    reply_service,
    log_service
)

router = APIRouter(prefix="/tickets", tags=["Tickets"])


def process_ticket(ticket_dict: dict) -> TicketDetailResponse:
    """
    End-to-end processing pipeline for an incoming ticket:
    1. Lookup linked order context
    2. Retrieve top-3 historical precedents via TF-IDF cosine similarity
    3. Evaluate decision, agreement, confidence, and guardrails
    4. Simulate resolution action
    5. Draft customer reply and explanation
    6. Record decision audit log
    """
    ticket_id = str(ticket_dict["ticket_id"])
    created_at = str(ticket_dict.get("created_at", ""))
    order_id = str(ticket_dict.get("order_id", ""))
    description = str(ticket_dict.get("description", ""))

    # 1. Fetch Order Context
    order = order_context_service.get_order(order_id)

    # 2. Similarity Search (Top 3 precedents)
    precedents = similarity_service.get_top_k_precedents(description, k=3)

    # 3. Decision & Confidence Evaluation
    evaluation = decision_service.evaluate(description, precedents, order)

    # 4. Simulate Action
    simulated_action = action_service.simulate_action(evaluation, order)

    # 5. Draft Customer Reply & Explanation
    draft_reply = reply_service.generate_draft_reply(
        ticket_id=ticket_id,
        description=description,
        order=order,
        evaluation=evaluation,
        simulated_action=simulated_action,
        precedents=precedents
    )

    response = TicketDetailResponse(
        ticket_id=ticket_id,
        created_at=created_at,
        description=description,
        order=order,
        precedents=precedents,
        evaluation=evaluation,
        simulated_action=simulated_action,
        draft_reply=draft_reply
    )

    # 6. Record decision in audit log
    log_service.log_decision(response)

    return response


@router.get("", response_model=List[TicketListItem])
def list_tickets(lane: Optional[str] = Query(None, description="Filter by lane: 'all', 'auto_resolve', 'human_review'")):
    """
    Returns list of all incoming tickets evaluated against the decision engine.
    Supports filtering by lane: 'auto_resolve' or 'human_review'.
    """
    VALID_LANES = ["all", "auto_resolve", "autoresolve", "auto", "human_review", "humanreview", "needs_human", "human"]
    
    if lane:
        normalized_lane = lane.lower().strip()
        if normalized_lane not in VALID_LANES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid lane filter '{lane}'. Allowed values: 'all', 'auto_resolve', 'human_review'."
            )

    all_raw_tickets = data_service.get_all_new_tickets()
    ticket_items: List[TicketListItem] = []

    for raw in all_raw_tickets:
        detail = process_ticket(raw)
        
        # Check lane filter
        if lane:
            filter_lane = lane.lower().strip()
            if filter_lane in ["auto_resolve", "autoresolve", "auto"] and detail.evaluation.decision != "AUTO_RESOLVE":
                continue
            elif filter_lane in ["human_review", "humanreview", "needs_human", "human"] and detail.evaluation.decision != "HUMAN_REVIEW":
                continue

        ticket_items.append(
            TicketListItem(
                ticket_id=detail.ticket_id,
                created_at=detail.created_at,
                order_id=detail.order.order_id if detail.order else raw.get("order_id", ""),
                description=detail.description,
                decision=detail.evaluation.decision,
                confidence_score=detail.evaluation.confidence_score,
                selected_action=detail.evaluation.selected_action,
                suggested_action=detail.evaluation.suggested_action,
                delivery_status=detail.order.delivery_status if detail.order else None
            )
        )

    return ticket_items


@router.get("/{ticket_id}", response_model=TicketDetailResponse)
def get_ticket_detail(ticket_id: str):
    """
    Returns full detail for a single ticket, including order context, top-3 precedents,
    decision engine evaluation, simulated action, and drafted reply.
    """
    raw = data_service.get_new_ticket_by_id(ticket_id)
    if not raw:
        raise HTTPException(status_code=404, detail=f"Ticket '{ticket_id}' not found in incoming dataset.")
    return process_ticket(raw)


@router.post("/{ticket_id}/evaluate", response_model=TicketDetailResponse)
def evaluate_ticket(ticket_id: str):
    """
    Runs or re-evaluates a ticket through the decision pipeline and updates the decision log.
    """
    raw = data_service.get_new_ticket_by_id(ticket_id)
    if not raw:
        raise HTTPException(status_code=404, detail=f"Ticket '{ticket_id}' not found in incoming dataset.")
    return process_ticket(raw)


@router.post("/{ticket_id}/resolve", response_model=SimulatedAction)
def resolve_ticket(ticket_id: str):
    """
    Simulates executing the resolution action for a ticket.
    Strict Guardrail: If the ticket was evaluated as HUMAN_REVIEW, automated resolution
    execution is blocked with a 400 Bad Request to protect business operations.
    """
    raw = data_service.get_new_ticket_by_id(ticket_id)
    if not raw:
        raise HTTPException(status_code=404, detail=f"Ticket '{ticket_id}' not found in incoming dataset.")
    
    detail = process_ticket(raw)
    
    if detail.evaluation.decision == "HUMAN_REVIEW":
        raise HTTPException(
            status_code=400,
            detail=(
                f"Cannot auto-resolve ticket '{ticket_id}'. Ticket decision is 'HUMAN_REVIEW' "
                f"({detail.evaluation.reasoning}). Manual intervention is required."
            )
        )
    
    return detail.simulated_action
