"""
Live API Verification Script
Tests all live endpoints on http://127.0.0.1:8000
"""

import sys
import json
import urllib.request
import urllib.error

sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://127.0.0.1:8000"

def get(endpoint):
    url = f"{BASE_URL}{endpoint}"
    req = urllib.request.Request(url, headers={"User-Agent": "VerificationScript"})
    with urllib.request.urlopen(req) as resp:
        return resp.status, json.loads(resp.read().decode('utf-8'))

def post(endpoint, data=None):
    url = f"{BASE_URL}{endpoint}"
    payload = json.dumps(data or {}).encode('utf-8')
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json", "User-Agent": "VerificationScript"})
    with urllib.request.urlopen(req) as resp:
        return resp.status, json.loads(resp.read().decode('utf-8'))

print("=== 1. VERIFY ROOT & HEALTH ===")
status, data = get("/")
print(f"GET / -> Status: {status}, Data: {data}")

status, data = get("/api/health")
print(f"GET /api/health -> Status: {status}, Data: {data}")

print("\n=== 2. VERIFY TICKET LISTS & FILTERS ===")
status, data = get("/api/tickets")
print(f"GET /api/tickets -> Status: {status}, Count: {len(data)}")

status, data_auto = get("/api/tickets?lane=auto_resolve")
print(f"GET /api/tickets?lane=auto_resolve -> Status: {status}, Count: {len(data_auto)} -> IDs: {[t['ticket_id'] for t in data_auto]}")

status, data_human = get("/api/tickets?lane=human_review")
print(f"GET /api/tickets?lane=human_review -> Status: {status}, Count: {len(data_human)}")

print("\n=== 3. EXAMPLE 1: AUTO_RESOLVE TICKET (N-005) ===")
status, n005 = get("/api/tickets/N-005")
print(f"GET /api/tickets/N-005 -> Status: {status}")
print(json.dumps(n005, indent=2))

print("\n=== 4. EXAMPLE 2: CANCELLED-ORDER HUMAN_REVIEW TICKET (N-002) ===")
status, n002 = get("/api/tickets/N-002")
print(f"GET /api/tickets/N-002 -> Status: {status}")
print(json.dumps(n002, indent=2))

print("\n=== 5. EXAMPLE 3: CONFLICTING-ACTION HUMAN_REVIEW TICKET (N-001) ===")
status, n001 = get("/api/tickets/N-001")
print(f"GET /api/tickets/N-001 -> Status: {status}")
print(json.dumps(n001, indent=2))

print("\n=== 6. VERIFY POST /api/tickets/{ticket_id}/evaluate & resolve ===")
status, eval_res = post("/api/tickets/N-005/evaluate")
print(f"POST /api/tickets/N-005/evaluate -> Status: {status}, Decision: {eval_res['evaluation']['decision']}")

status, resolve_res = post("/api/tickets/N-005/resolve")
print(f"POST /api/tickets/N-005/resolve -> Status: {status}, Action status: {resolve_res['status']}")

print("\n=== 7. VERIFY GET /api/decisions ===")
status, decisions = get("/api/decisions")
print(f"GET /api/decisions -> Status: {status}, Logged count: {len(decisions)}")
print("Latest decision log:")
print(json.dumps(decisions[-1], indent=2))

print("\n=== ALL LIVE ENDPOINTS VERIFIED SUCCESSFULLY ===")
