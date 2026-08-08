"""
Draft Reply & Explanation Service

Responsible for:
- Drafting empathetic customer-facing replies based on ticket description, order context, and decision
- Providing clear "Why this action?" explanations for human agents and audit trails
"""

from typing import Optional
from app.models.schemas import (
    DraftReply,
    EvaluationResult,
    OrderContext,
    SimulatedAction
)


class ReplyService:
    def generate_draft_reply(
        self,
        ticket_id: str,
        description: str,
        order: Optional[OrderContext],
        evaluation: EvaluationResult,
        simulated_action: SimulatedAction
    ) -> DraftReply:
        """
        Generates a structured customer draft reply and an explanation of why this action was chosen.
        """
        order_id = order.order_id if order else "N/A"
        decision = evaluation.decision
        action = simulated_action.action

        if decision == "AUTO_RESOLVE":
            if action == "redelivery":
                subject = f"Your replacement items for Order #{order_id} are on their way"
                body = (
                    f"Hi there, we sincerely apologize that items were missing or incorrect in your order #{order_id}. "
                    f"We have arranged an immediate priority redelivery at no extra cost to you. "
                    f"Our delivery partner will be at your doorstep shortly."
                )
                explanation = (
                    f"Auto-resolved via REDELIVERY based on unanimous historical precedent agreement (3/3). "
                    f"Order #{order_id} is active/delivered, satisfying all safety guardrails."
                )

            elif action == "full_refund":
                amount_str = f"₹{simulated_action.amount_inr}" if simulated_action.amount_inr else "the full order amount"
                subject = f"Refund processed for Order #{order_id}"
                body = (
                    f"Hi there, we are very sorry to hear about the issue with your order #{order_id}. "
                    f"We have processed a full refund of {amount_str} back to your original payment method. "
                    f"It should reflect in your account within 3-5 business days."
                )
                explanation = (
                    f"Auto-resolved via FULL_REFUND based on unanimous precedent agreement. "
                    f"Refund amount capped at order total (₹{order.value_inr if order else 0})."
                )

            elif action == "coupon":
                subject = f"A special credit for Order #{order_id}"
                body = (
                    f"Hi there, thank you for contacting Zepto Support regarding order #{order_id}. "
                    f"We apologize for the inconvenience and have credited a ₹50 discount coupon to your wallet "
                    f"for your next order."
                )
                explanation = (
                    f"Auto-resolved via COUPON (₹50) in accordance with historical precedent for late delivery SLA."
                )

            elif action == "apology_no_action":
                subject = f"Apology regarding your delivery time for Order #{order_id}"
                body = (
                    f"Hi there, thank you for reaching out. We sincerely apologize for the delay with order #{order_id}. "
                    f"Our operations team has been notified to ensure faster turnaround in your area for upcoming orders."
                )
                explanation = (
                    f"Auto-resolved via APOLOGY_NO_ACTION based on unanimous historical precedents (SLA breach < threshold)."
                )

            else:
                subject = f"Update regarding your Order #{order_id}"
                body = (
                    f"Hi there, thank you for contacting us regarding order #{order_id}. "
                    f"We have taken action to resolve your issue: {simulated_action.note}."
                )
                explanation = f"Auto-resolved based on high similarity and unanimous precedent agreement for {action}."

        else:
            # HUMAN_REVIEW cases
            subject = f"Your support request #{ticket_id} is under review"
            body = (
                f"Hi there, thank you for reaching out regarding order #{order_id}. "
                f"We are reviewing your request '{description}' with our senior support team "
                f"to ensure we provide the best possible resolution. We will update you shortly."
            )

            if evaluation.guardrails.cancelled_redelivery_blocked:
                explanation = (
                    f"Routed to HUMAN_REVIEW because Order #{order_id} is cancelled. "
                    f"Automated redelivery is blocked on cancelled orders to prevent inventory loss."
                )
            elif evaluation.guardrails.escalation_precedent_detected:
                explanation = (
                    f"Routed to HUMAN_REVIEW because historical precedents require specialized escalation (e.g. payment gateway investigation)."
                )
            elif not evaluation.exact_action_agreement:
                if evaluation.action_family_agreement:
                    explanation = (
                        f"Routed to HUMAN_REVIEW due to action ambiguity between sub-actions in historical precedents. "
                        f"Human agent must decide exact compensation."
                    )
                else:
                    explanation = (
                        f"Routed to HUMAN_REVIEW due to conflicting historical precedent actions. "
                        f"System strictly queues tickets when past resolutions disagree rather than guessing."
                    )
            elif not evaluation.guardrails.similarity_threshold_passed:
                explanation = (
                    f"Routed to HUMAN_REVIEW due to low similarity confidence (< {evaluation.similarity_score:.2f})."
                )
            else:
                explanation = f"Routed to HUMAN_REVIEW: {evaluation.reasoning}"

        return DraftReply(
            recipient="Customer",
            subject=subject,
            body=body,
            explanation=explanation
        )


# Global singleton instance
reply_service = ReplyService()
