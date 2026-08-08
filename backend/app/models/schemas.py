"""
Pydantic Schemas for Zepto Support Ticket Manager API

Defines models for:
- Raw Data Schemas (Historical tickets, New tickets, Order context)
- Precedents & Similarity Search Results
- Deterministic Evaluation & Confidence Scoring
- Simulated Resolution Actions
- Draft Customer Reply & Explanation
- Consolidated Ticket Detail & Evaluation Response
- Decision Log Audit Entries
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


# --- Raw Dataset Models ---

class OrderContext(BaseModel):
    order_id: str
    items: int
    value_inr: int
    delivery_time_min: int
    delivery_status: str  # "delivered" | "cancelled"


class PrecedentMatch(BaseModel):
    precedent_id: str
    category: str
    description: str
    resolution_action: str
    resolution_note: str
    similarity_score: float
    csat: int


class RawNewTicket(BaseModel):
    ticket_id: str
    created_at: str
    order_id: str
    description: str


class SimulateTicketRequest(BaseModel):
    description: str
    order_id: str



# --- Evaluation & Guardrails Models ---

class GuardrailResults(BaseModel):
    similarity_threshold_passed: bool
    cancelled_redelivery_blocked: bool
    refund_cap_enforced: bool
    escalation_precedent_detected: bool


class EvaluationResult(BaseModel):
    similarity_score: float
    exact_action_agreement: bool
    action_family_agreement: bool
    decision: str  # "AUTO_RESOLVE" | "HUMAN_REVIEW"
    confidence_score: float
    selected_action: str
    suggested_action: Optional[str] = None
    reasoning: str
    guardrails: GuardrailResults


# --- Simulated Action & Reply Models ---

class SimulatedAction(BaseModel):
    action: str
    amount_inr: Optional[int] = None
    status: str  # "SIMULATED_SUCCESS" | "QUEUED_FOR_HUMAN" | "BLOCKED"
    note: str
    is_simulated: bool = True


class DraftReply(BaseModel):
    recipient: str = "Customer"
    subject: str
    body: str
    explanation: str
    generation_source: Optional[str] = "fallback"  # "gemini" | "fallback"


# --- Consolidated API Response Models ---

class TicketDetailResponse(BaseModel):
    ticket_id: str
    created_at: str
    description: str
    order: Optional[OrderContext] = None
    precedents: List[PrecedentMatch] = []
    evaluation: EvaluationResult
    simulated_action: SimulatedAction
    draft_reply: DraftReply


class TicketListItem(BaseModel):
    ticket_id: str
    created_at: str
    order_id: str
    description: str
    decision: str
    confidence_score: float
    selected_action: str
    suggested_action: Optional[str] = None
    delivery_status: Optional[str] = None


class DecisionLogEntry(BaseModel):
    ticket_id: str
    timestamp: str
    order_id: str
    decision: str
    confidence_score: float
    selected_action: str
    suggested_action: Optional[str] = None
    reasoning: str
    top_precedent_ids: List[str]
    simulated_action_status: str

