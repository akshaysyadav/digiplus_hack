"""
Gemini Generative AI Service

Responsible for:
- Natural-language generation for customer draft replies and agent "Why this action?" explanations
- Grounding all generated text strictly in deterministic backend evidence
- Providing safe JSON-structured output
- Guaranteeing complete isolation from the deterministic decision engine
- Never breaking the ticket pipeline if the API key is missing or calls fail (graceful fallback)
"""

import json
import logging
from typing import Optional, Tuple, List
import httpx

from app.core.config import GEMINI_API_KEY, GEMINI_MODEL
from app.models.schemas import (
    OrderContext,
    EvaluationResult,
    SimulatedAction,
    PrecedentMatch
)

logger = logging.getLogger(__name__)


class GeminiService:
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        timeout_seconds: float = 2.5
    ):
        self.api_key = api_key if api_key is not None else GEMINI_API_KEY
        self.model = model or GEMINI_MODEL or "gemini-1.5-flash"
        self.timeout_seconds = timeout_seconds

    def is_configured(self) -> bool:
        """Returns True if a non-empty API key is configured."""
        return bool(self.api_key and self.api_key.strip())

    def generate_reply_and_explanation(
        self,
        ticket_id: str,
        description: str,
        order: Optional[OrderContext],
        evaluation: EvaluationResult,
        simulated_action: SimulatedAction,
        precedents: Optional[List[PrecedentMatch]] = None
    ) -> Optional[Tuple[str, str, str]]:
        """
        Calls Gemini Generative AI to produce a customer reply and an internal decision explanation.
        Returns (subject, body, explanation) if successful, or None if fallback should be used.
        
        Gemini is strictly prohibited from altering or overriding backend decisions.
        """
        if not self.is_configured():
            return None

        # Build grounded structured evidence payload for prompt
        order_id = order.order_id if order else "N/A"
        order_val = f"₹{order.value_inr}" if order else "N/A"
        deliv_status = order.delivery_status if order else "N/A"
        deliv_time = f"{order.delivery_time_min} mins" if order else "N/A"

        prec_lines = []
        if precedents:
            for idx, p in enumerate(precedents, 1):
                prec_lines.append(
                    f"  {idx}. Action: '{p.resolution_action}', Note: '{p.resolution_note}', Similarity: {p.similarity_score:.2f}, CSAT: {p.csat}"
                )
        precedents_summary = "\n".join(prec_lines) if prec_lines else "None available"

        prompt = f"""You are an expert AI assistant for Zepto Support Operations.
Your task is to draft a customer-facing reply and an internal agent decision explanation based STRICTLY AND EXCLUSIVELY on the verified backend evidence below.

VERIFIED BACKEND EVIDENCE:
- Ticket ID: {ticket_id}
- Customer Issue: {description}
- Order ID: {order_id}
- Order Value: {order_val}
- Delivery Status: {deliv_status}
- Delivery Time: {deliv_time}
- Decision: {evaluation.decision} ("AUTO_RESOLVE" or "HUMAN_REVIEW")
- Selected Executable Action: {evaluation.selected_action}
- Suggested Advisory Action: {evaluation.suggested_action or 'None'}
- Confidence Score: {evaluation.confidence_score}
- Exact Precedent Agreement: {evaluation.exact_action_agreement}
- Guardrail Flags:
  * Cancelled Redelivery Blocked: {evaluation.guardrails.cancelled_redelivery_blocked}
  * Escalation Detected: {evaluation.guardrails.escalation_precedent_detected}
  * Similarity Passed: {evaluation.guardrails.similarity_threshold_passed}
- Simulated Resolution Action:
  * Action: {simulated_action.action}
  * Status: {simulated_action.status}
  * Refund Amount: {f'₹{simulated_action.amount_inr}' if simulated_action.amount_inr else 'None'}
  * Note: {simulated_action.note}
- Top Historical Precedents:
{precedents_summary}

STRICT CONSTRAINTS & GUIDELINES:
1. AUTHORITY: You MUST NOT decide or change whether an action is approved or rejected. The backend deterministic engine is the sole authority.
2. CUSTOMER REPLY:
   - Must directly refer to the specific customer issue stated above: '{description}'.
   - NEVER mention items, details, or issues from other tickets or historical precedents (e.g. if the customer issue is 'received broken eggs', speak ONLY about eggs; if 'milk packet missing', speak ONLY about milk).
   - Must use the exact Order ID #{order_id}.
   - If Decision is "AUTO_RESOLVE": Write a clear, empathetic customer message communicating the simulated resolution ({simulated_action.action}). Mention refund amount only if given above (₹{simulated_action.amount_inr or ''}); NEVER invent ungrounded amounts.
   - If Decision is "HUMAN_REVIEW": Write a professional holding message acknowledging their request regarding '{description}' for order #{order_id} and explaining that our support team is reviewing it. NEVER promise a specific refund, redelivery, or compensation amount, and NEVER claim an action has already been completed or dispatched (especially for cancelled orders).
   - NEVER expose internal precedent IDs (like H-1000), similarity numbers, TF-IDF, Gemini, AI, or internal algorithms to the customer.
   - NEVER claim that real money was transferred or a physical Zepto dispatch occurred (it is simulated).
3. EXPLANATION ("Why this action?"):
   - Provide an internal 1-2 sentence audit explanation for the support agent grounded entirely in the evidence above.
   - For AUTO_RESOLVE: Explain high similarity and precedent agreement.
   - For CANCELLED ORDER: Explain that historical precedents suggest redelivery, but redelivery is blocked because order #{order_id} is cancelled, requiring human review.
   - For PRECEDENT CONFLICT: Explain ambiguity across historical resolution actions.
   - For ESCALATION: Explain requirement for specialized team escalation.

RESPONSE FORMAT:
Return a valid JSON object matching this schema:
{{
  "subject": "Clear email/notification subject line",
  "body": "Customer-facing reply text",
  "explanation": "Internal agent explanation of why this action was chosen"
}}
"""

        endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        request_body = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ],
            "generationConfig": {
                "responseMimeType": "application/json",
                "temperature": 0.2
            }
        }

        try:
            with httpx.Client(timeout=self.timeout_seconds) as client:
                response = client.post(endpoint, json=request_body)
                if response.status_code != 200:
                    logger.warning(f"Gemini API returned HTTP status {response.status_code}: {response.text[:150]}")
                    return None

                response_data = response.json()
                raw_text = (
                    response_data.get("candidates", [{}])[0]
                    .get("content", {})
                    .get("parts", [{}])[0]
                    .get("text", "")
                )
                if not raw_text:
                    return None

                parsed = json.loads(raw_text)
                if not isinstance(parsed, dict):
                    return None

                subject = str(parsed.get("subject", "")).strip()
                body = str(parsed.get("body", "")).strip()
                explanation = str(parsed.get("explanation", "")).strip()

                if subject and body and explanation:
                    return (subject, body, explanation)
                return None

        except Exception as ex:
            logger.warning(f"Gemini generation failed or timed out: {type(ex).__name__}")
            return None


# Global singleton instance
gemini_service = GeminiService()
