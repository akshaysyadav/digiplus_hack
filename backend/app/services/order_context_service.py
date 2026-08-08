"""
Order Context & Guardrails Service Placeholder

Future Responsibility:
- Matching incoming tickets to order records in `orders_context.csv`
- Enforcing business guardrails:
  1. Cancelled orders CANNOT trigger redelivery
  2. Refund amounts CANNOT exceed total order value
  3. Validating item availability and order status

TO BE IMPLEMENTED BY BACKEND DEVELOPER
"""

class OrderContextService:
    def __init__(self):
        pass

    def get_order_context(self, order_id: str):
        """Fetch order details for a given order_id."""
        pass

    def validate_action_against_order(self, order_context: dict, proposed_action: str, proposed_refund_amount: float = 0.0) -> bool:
        """
        Validates business rules:
        - Check if order is cancelled before redelivery
        - Check if proposed refund is <= order total value
        Returns (is_valid: bool, violation_reason: str)
        """
        pass
