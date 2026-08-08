"""
API Routes Package Initialization
"""

from fastapi import APIRouter
from app.api.routes.tickets import router as tickets_router
from app.api.routes.decisions import router as decisions_router
from app.api.routes.orders import router as orders_router

api_router = APIRouter(prefix="/api")
api_router.include_router(tickets_router)
api_router.include_router(decisions_router)
api_router.include_router(orders_router)

__all__ = ["api_router"]

