import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))
sys.stdout.reconfigure(encoding='utf-8')

from app.services import data_service
from app.api.routes.tickets import process_ticket

for tid in ['N-005', 'N-002', 'N-029']:
    raw = data_service.get_new_ticket_by_id(tid)
    res = process_ticket(raw)
    order_id = res.order.order_id if res.order else "N/A"
    deliv_status = res.order.delivery_status if res.order else "N/A"
    
    print("=" * 70)
    print(f"Ticket ID:        {res.ticket_id}")
    print(f"Description:      {res.description}")
    print(f"Order ID:         {order_id}")
    print(f"Delivery Status:  {deliv_status}")
    print(f"Decision:         {res.evaluation.decision}")
    print(f"Selected Action:  {res.evaluation.selected_action}")
    print(f"Suggested Action: {res.evaluation.suggested_action}")
    print(f"Reply Source:     {res.draft_reply.generation_source}")
    print(f"Draft Subject:    {res.draft_reply.subject}")
    print(f"Draft Body:       {res.draft_reply.body}")
    print(f"Explanation:      {res.draft_reply.explanation}")
print("=" * 70)
