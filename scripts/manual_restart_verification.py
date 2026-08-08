import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))
sys.stdout.reconfigure(encoding='utf-8')

import json
from app.core.config import SIMULATED_TICKETS_JSON
from app.services.data_service import DataService, data_service
from app.api.routes.tickets import process_ticket

print("=" * 70)
print("MANUAL RESTART PERSISTENCE VERIFICATION")
print("=" * 70)

# 1. Clean slate
data_service.clear_simulated_tickets(delete_storage=True)
print("\n[Step 1] Initialized clean environment. simulated_tickets.json exists:", SIMULATED_TICKETS_JSON.exists())

# 2. Ingest SIM-001
sim_raw_1 = data_service.add_simulated_ticket("milk packet missing from my order", "ORD-9905")
detail_1 = process_ticket(sim_raw_1)
data_service.save_simulated_ticket_detail(detail_1.ticket_id, detail_1.model_dump())
print(f"\n[Step 2] Created ticket {detail_1.ticket_id}:")
print(f"  - Decision:    {detail_1.evaluation.decision}")
print(f"  - Confidence:  {int(detail_1.evaluation.confidence_score * 100)}%")
print(f"  - Action:      {detail_1.simulated_action.action}")
print(f"  - Draft Body:  {detail_1.draft_reply.body[:80]}...")

# 3. Check JSON file on disk
assert SIMULATED_TICKETS_JSON.exists(), "Storage file was not written!"
with open(SIMULATED_TICKETS_JSON, "r", encoding="utf-8") as f:
    disk_data = json.load(f)
print(f"\n[Step 3] Disk verification: {SIMULATED_TICKETS_JSON} contains {len(disk_data)} ticket(s).")
print(f"  - Stored Ticket ID: {disk_data[0]['ticket_id']}")

# 4. Simulate Backend Restart (new DataService instance)
print("\n[Step 4] Simulating backend restart (instantiating fresh DataService)...")
restarted_ds = DataService()
persisted_tickets = restarted_ds._simulated_tickets
print(f"  - Restored in-memory simulated tickets: {len(persisted_tickets)}")
restored_t1 = restarted_ds.get_new_ticket_by_id("SIM-001")
assert restored_t1 is not None, "SIM-001 not found after restart!"
print(f"  - SIM-001 restored: Description = '{restored_t1['description']}', Order = '{restored_t1['order_id']}'")
print(f"  - Persisted Decision = {restored_t1['evaluation']['decision']}, Confidence = {int(restored_t1['evaluation']['confidence_score'] * 100)}%")

# 5. Ingest Next Ticket after Restart -> Must be SIM-002
sim_raw_2 = restarted_ds.add_simulated_ticket("got salted butter instead of unsalted", "ORD-9929")
detail_2 = process_ticket(sim_raw_2)
restarted_ds.save_simulated_ticket_detail(detail_2.ticket_id, detail_2.model_dump())
print(f"\n[Step 5] Created second ticket after restart:")
print(f"  - Expected ID: SIM-002 | Actual ID: {detail_2.ticket_id}")
assert detail_2.ticket_id == "SIM-002", f"Expected SIM-002, got {detail_2.ticket_id}"

# 6. Verify Baseline 30 CSV Tickets
print("\n[Step 6] Verifying baseline 30 CSV tickets are untouched...")
csv_tickets = restarted_ds.new_tickets_df.to_dict(orient="records")
assert len(csv_tickets) == 30, f"Expected 30, got {len(csv_tickets)}"
auto_count = 0
human_count = 0
for raw in csv_tickets:
    res = process_ticket(raw)
    if res.evaluation.decision == "AUTO_RESOLVE":
        auto_count += 1
    else:
        human_count += 1
print(f"  - Baseline CSV count: {len(csv_tickets)}")
print(f"  - AUTO_RESOLVE: {auto_count}")
print(f"  - HUMAN_REVIEW: {human_count}")
assert auto_count == 2
assert human_count == 28

# 7. Verify Total Tickets in System
all_tickets = restarted_ds.get_all_new_tickets()
print(f"\n[Step 7] Total tickets across system: {len(all_tickets)} (30 CSV + 2 Persisted SIM)")
assert len(all_tickets) == 32

print("\n" + "=" * 70)
print("ALL MANUAL RESTART PERSISTENCE CHECKS PASSED PERFECTLY!")
print("=" * 70)
