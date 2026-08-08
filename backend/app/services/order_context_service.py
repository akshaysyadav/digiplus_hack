"""
Order Context & Guardrails Service

Responsible for:
- Fetching order context for tickets
- Validating business guardrails:
  1. Cancelled Order Redelivery Block: A cancelled order must never trigger redelivery.
  2. Refund Amount Cap: Refund amount must never exceed the order value.
"""

from typing import Optional, Tuple
from app.models.schemas import OrderContext
from app.services.data_service import data_service


class OrderContextService:
    def get_order(self, order_id: str) -> Optional[OrderContext]:
        """Fetches order context for an order_id."""
        return data_service.get_order_context(order_id)

    def validate_redelivery_guardrail(self, order: Optional[OrderContext], proposed_action: str) -> bool:
        """
        Guardrail: If order is cancelled and proposed action is redelivery, returns False (blocked).
        Returns True if valid.
        """
        if order is None:
            return True
        if order.delivery_status.lower() == "cancelled" and proposed_action.lower() == "redelivery":
            return False
        return True

    def cap_refund_amount(self, order: Optional[OrderContext], proposed_amount: Optional[int]) -> Optional[int]:
        """
        Guardrail: Capping refund amount to not exceed order value.
        """
        if proposed_amount is None or order is None:
            return proposed_amount
        return min(proposed_amount, order.value_inr)


# Global singleton instance
order_context_service = OrderContextService()
