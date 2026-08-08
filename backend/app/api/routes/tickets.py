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
    SimulatedAction,
    SimulateTicketRequest
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


def evaluate_for_list_item(ticket_dict: dict) -> TicketListItem:
    """
    Fast decision evaluation for list views (omits heavyweight LLM draft generation):
    1. Lookup linked order context
    2. Retrieve top-3 historical precedents via TF-IDF cosine similarity
    3. Evaluate decision, agreement, confidence, and guardrails
    """
    ticket_id = str(ticket_dict["ticket_id"])
    created_at = str(ticket_dict.get("created_at", ""))
    order_id = str(ticket_dict.get("order_id", ""))
    description = str(ticket_dict.get("description", ""))

    order = order_context_service.get_order(order_id)

    # If already evaluated and persisted, extract directly
    if isinstance(ticket_dict.get("evaluation"), dict):
        eval_dict = ticket_dict["evaluation"]
        order_dict = ticket_dict.get("order") or {}
        return TicketListItem(
            ticket_id=ticket_id,
            created_at=created_at,
            order_id=order_id,
            description=description,
            decision=str(eval_dict.get("decision", "HUMAN_REVIEW")),
            confidence_score=float(eval_dict.get("confidence_score", 0.0)),
            selected_action=str(eval_dict.get("selected_action", "human_review")),
            suggested_action=eval_dict.get("suggested_action"),
            delivery_status=order_dict.get("delivery_status") or (order.delivery_status if order else None)
        )

    precedents = similarity_service.get_top_k_precedents(description, k=3)
    evaluation = decision_service.evaluate(description, precedents, order)

    return TicketListItem(
        ticket_id=ticket_id,
        created_at=created_at,
        order_id=order_id,
        description=description,
        decision=evaluation.decision,
        confidence_score=evaluation.confidence_score,
        selected_action=evaluation.selected_action,
        suggested_action=evaluation.suggested_action,
        delivery_status=order.delivery_status if order else None
    )


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
        item = evaluate_for_list_item(raw)
        
        # Check lane filter
        if lane:
            filter_lane = lane.lower().strip()
            if filter_lane in ["auto_resolve", "autoresolve", "auto"] and item.decision != "AUTO_RESOLVE":
                continue
            elif filter_lane in ["human_review", "humanreview", "needs_human", "human"] and item.decision != "HUMAN_REVIEW":
                continue

        ticket_items.append(item)

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
    
    # If this is a persisted simulated ticket with full details already computed, restore directly
    if isinstance(raw.get("evaluation"), dict) and isinstance(raw.get("draft_reply"), dict):
        try:
            return TicketDetailResponse(**raw)
        except Exception:
            pass

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


@router.post("/simulate", response_model=TicketDetailResponse)
def simulate_ticket(request: SimulateTicketRequest):
    """
    Simulates ingesting a new customer ticket in real time:
    1. Validates non-empty description
    2. Validates order_id exists in verified order context dataset (orders_context.csv)
    3. Generates unique in-memory simulated ticket ID (e.g. SIM-001)
    4. Evaluates end-to-end against 300 historical precedents using existing decision engine
    5. Drafts grounded customer reply & agent explanation (Gemini AI with deterministic fallback)
    6. Records decision audit log and returns full ticket detail
    """
    description = (request.description or "").strip()
    if not description:
        raise HTTPException(
            status_code=400,
            detail="Ticket description cannot be empty."
        )

    order_id = (request.order_id or "").strip()
    if not order_id:
        raise HTTPException(
            status_code=400,
            detail="Order ID cannot be empty."
        )

    # Validate that order exists in verified dataset
    order = order_context_service.get_order(order_id)
    if not order:
        raise HTTPException(
            status_code=400,
            detail=f"Order '{order_id}' not found in order context dataset."
        )

    # Ingest in-memory simulated ticket
    simulated_raw = data_service.add_simulated_ticket(description, order_id)

    # Run existing end-to-end evaluation pipeline
    response = process_ticket(simulated_raw)

    # Persist full evaluated detail
    data_service.save_simulated_ticket_detail(response.ticket_id, response.model_dump())

    return response



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

