"""
Decision Service

Responsible for:
- Evaluating precedent action agreement (Exact vs Action Family)
- Computing deterministic confidence score using explicit weighted components
- Applying business guardrails (similarity gate, cancelled redelivery block, escalation check)
- Making the final decision: AUTO_RESOLVE vs HUMAN_REVIEW
"""

from collections import Counter
from typing import List, Tuple, Optional
from app.models.schemas import (
    PrecedentMatch,
    OrderContext,
    EvaluationResult,
    GuardrailResults
)
from app.core.config import (
    SIMILARITY_THRESHOLD,
    WEIGHT_SIMILARITY,
    WEIGHT_AGREEMENT,
    WEIGHT_VALIDITY
)
from app.services.order_context_service import order_context_service


def get_action_family(action: str) -> str:
    """Maps raw resolution action to its higher-level action family."""
    act = action.lower()
    if "refund" in act:
        return "REFUND"
    if act == "redelivery":
        return "REDELIVERY"
    if act == "coupon":
        return "COUPON"
    if act == "escalation":
        return "ESCALATION"
    if act == "apology_no_action":
        return "APOLOGY"
    return "OTHER"


class DecisionService:
    def evaluate(
        self,
        description: str,
        precedents: List[PrecedentMatch],
        order: Optional[OrderContext]
    ) -> EvaluationResult:
        """
        Executes deterministic evaluation pipeline on precedents and order context.
        Computes both selected_action (executable) and suggested_action (advisory for human lane).
        """
        if not precedents:
            return EvaluationResult(
                similarity_score=0.0,
                exact_action_agreement=False,
                action_family_agreement=False,
                decision="HUMAN_REVIEW",
                confidence_score=0.0,
                selected_action="human_review",
                suggested_action=None,
                reasoning="No historical precedents found.",
                guardrails=GuardrailResults(
                    similarity_threshold_passed=False,
                    cancelled_redelivery_blocked=False,
                    refund_cap_enforced=False,
                    escalation_precedent_detected=False
                )
            )

        top1_similarity = precedents[0].similarity_score
        prec_actions = [p.resolution_action.lower().strip() for p in precedents]
        prec_families = [get_action_family(a) for a in prec_actions]

        # Agreement evaluation
        exact_agreement = (len(set(prec_actions)) == 1)
        family_agreement = (len(set(prec_families)) == 1)
        primary_action = prec_actions[0]

        # Guardrails evaluation
        similarity_passed = (top1_similarity >= SIMILARITY_THRESHOLD)
        is_escalation = (primary_action == "escalation") or any(a == "escalation" for a in prec_actions)
        
        # Check redelivery on cancelled order
        redelivery_valid = order_context_service.validate_redelivery_guardrail(order, primary_action)
        is_cancelled_order = bool(order and order.delivery_status.lower() == "cancelled")
        cancelled_redelivery_blocked = not redelivery_valid

        # Validity component for confidence
        order_valid = redelivery_valid and (not is_escalation)
        validity_component = 1.0 if order_valid else 0.0
        agreement_component = 1.0 if exact_agreement else 0.0
        similarity_component = top1_similarity

        # Deterministic confidence calculation
        confidence = (
            WEIGHT_SIMILARITY * similarity_component +
            WEIGHT_AGREEMENT * agreement_component +
            WEIGHT_VALIDITY * validity_component
        )
        confidence_score = round(confidence, 4)

        # Suggested Action Computation (Advisory recommendation based on top-3 precedents)
        suggested_action: Optional[str] = None
        if is_escalation:
            # Case 4: Historical action is escalation
            suggested_action = "escalation"
        else:
            action_counts = Counter(prec_actions)
            most_common = action_counts.most_common()
            
            # Check for a tie between different actions (Case 3)
            if len(most_common) > 1 and most_common[0][1] == most_common[1][1]:
                suggested_action = None
            else:
                top_candidate = most_common[0][0]
                # Case 5: Cancelled order + historical redelivery -> guardrail strictly blocks suggesting redelivery
                if top_candidate == "redelivery" and is_cancelled_order:
                    suggested_action = None
                else:
                    # Case 1 & Case 2: Unanimous agreement or strongest precedent support
                    suggested_action = top_candidate

        # Decision Determination Logic
        decision: str = "HUMAN_REVIEW"
        selected_action: str = "human_review"
        reasoning: str = ""

        if not similarity_passed:
            decision = "HUMAN_REVIEW"
            selected_action = "human_review"
            reasoning = f"Low similarity score ({top1_similarity:.2f} < {SIMILARITY_THRESHOLD:.2f}); weak historical precedent match."
        elif is_escalation:
            decision = "HUMAN_REVIEW"
            selected_action = "human_review"
            reasoning = "Historical precedent requires escalation to specialized support team."
        elif cancelled_redelivery_blocked:
            decision = "HUMAN_REVIEW"
            selected_action = "human_review"
            order_label = f"Order #{order.order_id} " if order else "The order "
            reasoning = f"Historical precedents suggest redelivery, but redelivery is blocked because {order_label}is cancelled. Human review is required."
        elif not exact_agreement:
            decision = "HUMAN_REVIEW"
            selected_action = "human_review"
            if family_agreement:
                reasoning = (
                    f"Action ambiguity: Precedents agree on action family '{prec_families[0]}' but conflict on exact action "
                    f"({', '.join(prec_actions)}). Routed to human agent to determine exact resolution."
                )
            else:
                reasoning = (
                    f"Conflicting precedent actions across historical resolutions ({', '.join(prec_actions)}). "
                    f"System does not guess when precedents disagree."
                )
        else:
            # All conditions met for auto resolution
            decision = "AUTO_RESOLVE"
            selected_action = primary_action
            reasoning = (
                f"High similarity ({top1_similarity:.2f}) with unanimous precedent agreement (3/3: {primary_action}). "
                f"All order context guardrails passed."
            )

        guardrails = GuardrailResults(
            similarity_threshold_passed=similarity_passed,
            cancelled_redelivery_blocked=cancelled_redelivery_blocked,
            refund_cap_enforced=False,  # Evaluated in action service
            escalation_precedent_detected=is_escalation
        )

        return EvaluationResult(
            similarity_score=top1_similarity,
            exact_action_agreement=exact_agreement,
            action_family_agreement=family_agreement,
            decision=decision,
            confidence_score=confidence_score,
            selected_action=selected_action,
            suggested_action=suggested_action,
            reasoning=reasoning,
            guardrails=guardrails
        )


# Global singleton instance
decision_service = DecisionService()

