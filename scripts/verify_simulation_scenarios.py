import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))
sys.stdout.reconfigure(encoding='utf-8')

from app.services import data_service
from app.api.routes.tickets import process_ticket

data_service.clear_simulated_tickets()

scenarios = [
    {
        "name": "SCENARIO 1 — STRONG MATCH (Delivered Order)",
        "description": "milk packet missing from my order",
        "order_id": "ORD-9905",
    },
    {
        "name": "SCENARIO 2 — CANCELLED ORDER SAFETY",
        "description": "milk packet missing from my order",
        "order_id": "ORD-9902",
    },
    {
        "name": "SCENARIO 3 — NOVEL QUERY (Weak Similarity)",
        "description": "the delivery person was rude and shouted at me",
        "order_id": "ORD-9908",
    },
    {
        "name": "SCENARIO 4 — CONFLICTING PRECEDENTS",
        "description": "got salted butter instead of unsalted",
        "order_id": "ORD-9929",
    },
]

for sc in scenarios:
    print("\n" + "=" * 70)
    print(sc["name"])
    print("=" * 70)
    sim_raw = data_service.add_simulated_ticket(sc["description"], sc["order_id"])
    result = process_ticket(sim_raw)
    
    print(f"Ticket ID:        {result.ticket_id}")
    print(f"Customer Issue:   {result.description}")
    print(f"Order ID:         {result.order.order_id} ({result.order.delivery_status})")
    print(f"Decision:         {result.evaluation.decision}")
    print(f"Confidence:       {int(result.evaluation.confidence_score * 100)}%")
    print(f"Selected Action:  {result.evaluation.selected_action}")
    print(f"Suggested Action: {result.evaluation.suggested_action}")
    print(f"Precedents Agree: {result.evaluation.exact_action_agreement}")
    print(f"Guardrails:")
    print(f"  - Similarity Passed:  {result.evaluation.guardrails.similarity_threshold_passed}")
    print(f"  - Cancelled Blocked:  {result.evaluation.guardrails.cancelled_redelivery_blocked}")
    print(f"Simulated Action: {result.simulated_action.action} ({result.simulated_action.status})")
    print(f"Draft Body:       {result.draft_reply.body}")
    print(f"Why this action?: {result.draft_reply.explanation}")

print("\n" + "=" * 70)
print(f"Total in-memory simulated tickets created: {len(data_service._simulated_tickets)}")
print(f"Total all incoming tickets (30 CSV + 4 SIM): {len(data_service.get_all_new_tickets())}")
print("=" * 70)
