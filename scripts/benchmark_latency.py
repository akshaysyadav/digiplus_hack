import time
import httpx

client = httpx.Client(base_url="http://localhost:8000")

print("Measuring API latency...")

# 1. Test GET /api/tickets
t0 = time.perf_counter()
resp_list = client.get("/api/tickets")
t_list = (time.perf_counter() - t0) * 1000
print(f"GET /api/tickets: {resp_list.status_code} in {t_list:.1f}ms (loaded {len(resp_list.json())} tickets)")

# 2. Test POST /api/tickets/simulate
payload = {
    "description": "milk packet missing from my order",
    "order_id": "ORD-9905"
}
t0 = time.perf_counter()
resp_sim = client.post("/api/tickets/simulate", json=payload)
t_sim = (time.perf_counter() - t0) * 1000
data = resp_sim.json()
print(f"POST /api/tickets/simulate: {resp_sim.status_code} in {t_sim:.1f}ms (created {data.get('ticket_id')}, decision: {data.get('evaluation', {}).get('decision')})")

# 3. Test repeat simulation
t0 = time.perf_counter()
resp_sim2 = client.post("/api/tickets/simulate", json={
    "description": "got salted butter instead of unsalted",
    "order_id": "ORD-9929"
})
t_sim2 = (time.perf_counter() - t0) * 1000
data2 = resp_sim2.json()
print(f"POST /api/tickets/simulate (Scenario 4): {resp_sim2.status_code} in {t_sim2:.1f}ms (created {data2.get('ticket_id')}, decision: {data2.get('evaluation', {}).get('decision')})")
