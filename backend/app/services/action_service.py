"""
Action Simulation Service

Responsible for:
- Simulating resolution actions (refund, redelivery, coupon, apology, escalation)
- Enforcing order-value refund caps
- Setting realistic simulation metadata without calling real Zepto backend APIs
"""

from typing import Optional, Tuple
from app.models.schemas import (
    SimulatedAction,
    EvaluationResult,
    OrderContext
)
from app.core.config import COUPON_AMOUNT_INR
from app.services.order_context_service import order_context_service


class ActionService:
    def simulate_action(
        self,
        evaluation: EvaluationResult,
        order: Optional[OrderContext]
    ) -> SimulatedAction:
        """
        Simulates the appropriate resolution action based on the evaluation result and order context.
        """
        action_type = evaluation.selected_action.lower()
        decision = evaluation.decision

        if decision == "HUMAN_REVIEW":
            if evaluation.guardrails.cancelled_redelivery_blocked:
                return SimulatedAction(
                    action="blocked_redelivery",
                    amount_inr=None,
                    status="BLOCKED",
                    note="Redelivery blocked because order is cancelled. Queued for human review.",
                    is_simulated=True
                )
            if action_type == "escalation":
                return SimulatedAction(
                    action="escalation",
                    amount_inr=None,
                    status="QUEUED_FOR_HUMAN",
                    note="Sent to payments/specialized team for investigation.",
                    is_simulated=True
                )
            return SimulatedAction(
                action="queued_for_review",
                amount_inr=None,
                status="QUEUED_FOR_HUMAN",
                note="Ticket queued in Needs-Human lane for agent review.",
                is_simulated=True
            )

        # Auto-resolved scenarios
        if action_type == "full_refund":
            amount = order.value_inr if order else None
            capped_amount = order_context_service.cap_refund_amount(order, amount)
            return SimulatedAction(
                action="full_refund",
                amount_inr=capped_amount,
                status="SIMULATED_SUCCESS",
                note=f"Simulated full refund of ₹{capped_amount} credited to customer.",
                is_simulated=True
            )

        elif action_type == "refund_reissue":
            amount = order.value_inr if order else None
            capped_amount = order_context_service.cap_refund_amount(order, amount)
            return SimulatedAction(
                action="refund_reissue",
                amount_inr=capped_amount,
                status="SIMULATED_SUCCESS",
                note=f"Simulated refund reissue of ₹{capped_amount} re-triggered.",
                is_simulated=True
            )

        elif action_type == "partial_refund":
            # Per design requirements: Do not invent ungrounded item-level rupee prices.
            return SimulatedAction(
                action="partial_refund",
                amount_inr=None,
                status="SIMULATED_SUCCESS",
                note="Simulated partial refund initiated (exact item amount to be finalized via item breakdown).",
                is_simulated=True
            )

        elif action_type == "redelivery":
            return SimulatedAction(
                action="redelivery",
                amount_inr=None,
                status="SIMULATED_SUCCESS",
                note="Simulated dispatch: Replacement items scheduled for immediate redelivery.",
                is_simulated=True
            )

        elif action_type == "coupon":
            amount = COUPON_AMOUNT_INR
            if order:
                amount = min(amount, order.value_inr)
            return SimulatedAction(
                action="coupon",
                amount_inr=amount,
                status="SIMULATED_SUCCESS",
                note=f"Simulated ₹{amount} discount coupon credited to customer wallet.",
                is_simulated=True
            )

        elif action_type == "apology_no_action":
            return SimulatedAction(
                action="apology_no_action",
                amount_inr=None,
                status="SIMULATED_SUCCESS",
                note="Simulated resolution: Apology message issued. SLA breach < threshold.",
                is_simulated=True
            )

        else:
            return SimulatedAction(
                action=action_type,
                amount_inr=None,
                status="SIMULATED_SUCCESS",
                note=f"Simulated resolution action '{action_type}' processed.",
                is_simulated=True
            )


# Global singleton instance
action_service = ActionService()
