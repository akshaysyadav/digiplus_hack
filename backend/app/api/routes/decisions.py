"""
Decisions Audit API Routes

Provides endpoints for:
- Retrieving logged decision history and audit trail
"""

from fastapi import APIRouter
from typing import List
from app.models.schemas import DecisionLogEntry
from app.services import log_service

router = APIRouter(prefix="/decisions", tags=["Decisions"])


@router.get("", response_model=List[DecisionLogEntry])
def list_decisions():
    """
    Returns all logged decisions and audit history.
    """
    return log_service.get_all_logs()
