"""
Script to evaluate all 30 incoming tickets end-to-end and display the breakdown
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')

from app.services import data_service
from app.api.routes.tickets import process_ticket

new_tickets = data_service.get_all_new_tickets()
print(f"Total tickets to evaluate: {len(new_tickets)}\n")

auto_count = 0
human_count = 0

print(f"{'TICKET':<8} | {'ORDER':<9} | {'STATUS':<9} | {'SIM':<5} | {'AGREE':<5} | {'CONF':<5} | {'DECISION':<14} | {'ACTION':<18} | REASON")
print("-" * 125)

for t in new_tickets:
    res = process_ticket(t)
    dec = res.evaluation.decision
    if dec == "AUTO_RESOLVE":
        auto_count += 1
    else:
        human_count += 1
    
    order_id = res.order.order_id if res.order else "N/A"
    status = res.order.delivery_status if res.order else "N/A"
    sim = f"{res.evaluation.similarity_score:.2f}"
    agree = str(res.evaluation.exact_action_agreement)
    conf = f"{res.evaluation.confidence_score:.2f}"
    action = res.simulated_action.action
    reason = res.evaluation.reasoning

    print(f"{res.ticket_id:<8} | {order_id:<9} | {status:<9} | {sim:<5} | {agree:<5} | {conf:<5} | {dec:<14} | {action:<18} | {reason}")

print("-" * 125)
print(f"TOTAL: {len(new_tickets)} tickets | AUTO_RESOLVE: {auto_count} | HUMAN_REVIEW: {human_count}")
