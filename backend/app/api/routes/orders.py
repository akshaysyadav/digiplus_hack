"""
Orders API Routes

Provides endpoints for:
- Listing available order contexts from verified dataset
"""

from fastapi import APIRouter
from typing import List
from app.models.schemas import OrderContext
from app.services.data_service import data_service

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.get("", response_model=List[OrderContext])
def list_orders():
    """
    Returns list of all verified order contexts from dataset.
    Used by frontend simulation form for dropdown selection.
    """
    return data_service.get_all_orders()
