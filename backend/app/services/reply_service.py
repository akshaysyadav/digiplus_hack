"""
Customer Reply & Explanation Service Placeholder

Future Responsibility:
- Generating customer-facing draft responses based on ticket context and simulated action
- Generating "Why this action?" audit explanations detailing similarity score, top precedents, and guardrail verification

TO BE IMPLEMENTED BY BACKEND DEVELOPER
"""

class ReplyService:
    def __init__(self):
        pass

    def generate_draft_reply(self, ticket_data: dict, action_details: dict) -> str:
        """Generates customer-facing draft message."""
        pass

    def generate_explanation(self, decision_result: dict, precedents: list, rule_checks: dict) -> str:
        """Generates clear audit explanation ("Why this action?")."""
        pass
