"""
API Routes Package Initialization
"""

from fastapi import APIRouter
from app.api.routes.tickets import router as tickets_router
from app.api.routes.decisions import router as decisions_router

api_router = APIRouter(prefix="/api")
api_router.include_router(tickets_router)
api_router.include_router(decisions_router)

__all__ = ["api_router"]
