"""
Pydantic Schemas Placeholder

All data model schemas in this file are TO BE FINALIZED BY BACKEND DEVELOPER
once dataset CSV structures are inspected and validated.

Planned Schemas:
- TicketBase / TicketCreate / TicketResponse
- OrderContext
- PrecedentMatch
- DecisionResult
- ActionSimulation
- DraftReply
"""

from pydantic import BaseModel
from typing import Optional, List

class TicketPlaceholder(BaseModel):
    """
    Placeholder schema for incoming tickets.
    TO BE FINALIZED BY BACKEND DEVELOPER
    """
    ticket_id: str
    issue_description: Optional[str] = None

class PrecedentPlaceholder(BaseModel):
    """
    Placeholder schema for historical precedent matches.
    TO BE FINALIZED BY BACKEND DEVELOPER
    """
    precedent_id: str
    similarity_score: float
    historical_action: str

class DecisionResultPlaceholder(BaseModel):
    """
    Placeholder schema for automated decision output.
    TO BE FINALIZED BY BACKEND DEVELOPER
    """
    ticket_id: str
    decision: str  # AUTO_RESOLVE or HUMAN_REVIEW
    confidence_score: float
    reasoning: str
