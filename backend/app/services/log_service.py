"""
Decision Logging Service

Responsible for:
- Persisting structured decision logs and audit history in memory
- Providing audit trail retrieval for dashboard inspection
"""

from datetime import datetime, timezone
from typing import List, Dict, Optional
from app.models.schemas import DecisionLogEntry, TicketDetailResponse


class DecisionLogService:
    def __init__(self):
        self._logs: List[DecisionLogEntry] = []

    def log_decision(self, ticket_detail: TicketDetailResponse) -> DecisionLogEntry:
        """Records a decision log entry from a ticket evaluation result."""
        entry = DecisionLogEntry(
            ticket_id=ticket_detail.ticket_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            order_id=ticket_detail.order.order_id if ticket_detail.order else "N/A",
            decision=ticket_detail.evaluation.decision,
            confidence_score=ticket_detail.evaluation.confidence_score,
            selected_action=ticket_detail.evaluation.selected_action,
            suggested_action=ticket_detail.evaluation.suggested_action,
            reasoning=ticket_detail.evaluation.reasoning,
            top_precedent_ids=[p.precedent_id for p in ticket_detail.precedents],
            simulated_action_status=ticket_detail.simulated_action.status
        )
        # Update or append
        existing_idx = next((i for i, log in enumerate(self._logs) if log.ticket_id == entry.ticket_id), None)
        if existing_idx is not None:
            self._logs[existing_idx] = entry
        else:
            self._logs.append(entry)
        return entry

    def get_all_logs(self) -> List[DecisionLogEntry]:
        """Returns all recorded decision logs."""
        return self._logs

    def get_log_for_ticket(self, ticket_id: str) -> Optional[DecisionLogEntry]:
        """Returns decision log for a specific ticket."""
        for log in self._logs:
            if log.ticket_id == ticket_id:
                return log
        return None


    def clear_logs(self) -> None:
        """Clears in-memory decision logs (for test resets)."""
        self._logs.clear()


# Global singleton instance
log_service = DecisionLogService()

