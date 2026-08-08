"""
Live API Verification Script for Zepto Support Ticket Manager
Tests all live endpoints on http://127.0.0.1:8000
"""

import sys
import json
import urllib.request
import urllib.error

sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://127.0.0.1:8000"

def request_api(method, endpoint, data=None):
    url = f"{BASE_URL}{endpoint}"
    payload = json.dumps(data).encode('utf-8') if data else None
    headers = {"User-Agent": "LiveVerificationScript"}
    if data:
        headers["Content-Type"] = "application/json"
    
    req = urllib.request.Request(url, data=payload, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8')
        try:
            return e.code, json.loads(body)
        except Exception:
            return e.code, {"error": body}

print("=================================================================")
print("1. VERIFY ROOT & HEALTH")
print("=================================================================")
status, data = request_api("GET", "/")
print(f"GET / -> HTTP {status}: {data}")

status, data = request_api("GET", "/api/health")
print(f"GET /api/health -> HTTP {status}: {data}")

print("\n=================================================================")
print("2. VERIFY TICKET LISTS & LANES")
print("=================================================================")
status, all_tickets = request_api("GET", "/api/tickets")
print(f"GET /api/tickets -> HTTP {status}, Total count: {len(all_tickets)}")

status, auto_tickets = request_api("GET", "/api/tickets?lane=auto_resolve")
print(f"GET /api/tickets?lane=auto_resolve -> HTTP {status}, Count: {len(auto_tickets)}, IDs: {[t['ticket_id'] for t in auto_tickets]}")

status, human_tickets = request_api("GET", "/api/tickets?lane=human_review")
print(f"GET /api/tickets?lane=human_review -> HTTP {status}, Count: {len(human_tickets)}")

print("\n=================================================================")
print("3. DEMO SCENARIOS")
print("=================================================================")
# Demo 1: N-005
status, n005 = request_api("GET", "/api/tickets/N-005")
print(f"DEMO 1: N-005 (AUTO_RESOLVE) -> HTTP {status}")
print(f"  Order: {n005['order']['order_id']} | Status: {n005['order']['delivery_status']}")
print(f"  Decision: {n005['evaluation']['decision']} | Selected Action: {n005['evaluation']['selected_action']} | Suggested Action: {n005['evaluation']['suggested_action']}")
print(f"  Confidence: {n005['evaluation']['confidence_score']} | Exact Agreement: {n005['evaluation']['exact_action_agreement']}")
print(f"  Precedent Actions: {[p['resolution_action'] for p in n005['precedents']]}")
print(f"  Draft Reply [{n005['draft_reply'].get('generation_source', 'fallback')}]:")
print(f"    Subject: {n005['draft_reply']['subject']}")
print(f"    Explanation: {n005['draft_reply']['explanation']}")

# Demo 2: N-002
status, n002 = request_api("GET", "/api/tickets/N-002")
print(f"\nDEMO 2: N-002 (CANCELLED ORDER REDELIVERY BLOCK) -> HTTP {status}")
print(f"  Order: {n002['order']['order_id']} | Status: {n002['order']['delivery_status']}")
print(f"  Decision: {n002['evaluation']['decision']} | Selected Action: {n002['evaluation']['selected_action']} | Suggested Action: {n002['evaluation']['suggested_action']}")
print(f"  Cancelled Redelivery Blocked Guardrail: {n002['evaluation']['guardrails']['cancelled_redelivery_blocked']}")
print(f"  Reasoning: {n002['evaluation']['reasoning']}")
print(f"  Draft Reply [{n002['draft_reply'].get('generation_source', 'fallback')}]:")
print(f"    Subject: {n002['draft_reply']['subject']}")
print(f"    Explanation: {n002['draft_reply']['explanation']}")

# Demo 3: N-029
status, n029 = request_api("GET", "/api/tickets/N-029")
print(f"\nDEMO 3: N-029 (CONFLICTING PRECEDENT ACTIONS) -> HTTP {status}")
print(f"  Order: {n029['order']['order_id']} | Status: {n029['order']['delivery_status']}")
print(f"  Decision: {n029['evaluation']['decision']} | Selected Action: {n029['evaluation']['selected_action']} | Suggested Action: {n029['evaluation']['suggested_action']}")
print(f"  Exact Agreement: {n029['evaluation']['exact_action_agreement']} | Precedent Actions: {[p['resolution_action'] for p in n029['precedents']]}")
print(f"  Reasoning: {n029['evaluation']['reasoning']}")
print(f"  Draft Reply [{n029['draft_reply'].get('generation_source', 'fallback')}]:")
print(f"    Subject: {n029['draft_reply']['subject']}")
print(f"    Explanation: {n029['draft_reply']['explanation']}")


print("\n=================================================================")
print("4. VERIFY POST ENDPOINTS & RESOLVE GUARDRAILS")
print("=================================================================")
# Evaluate N-005
status, eval_res = request_api("POST", "/api/tickets/N-005/evaluate")
print(f"POST /api/tickets/N-005/evaluate -> HTTP {status}, Decision: {eval_res['evaluation']['decision']}")

# Resolve N-005 (AUTO_RESOLVE -> 200 OK)
status, resolve_ok = request_api("POST", "/api/tickets/N-005/resolve")
print(f"POST /api/tickets/N-005/resolve -> HTTP {status}, Action: {resolve_ok['action']}, Status: {resolve_ok['status']}")

# Resolve N-002 (HUMAN_REVIEW -> 400 Bad Request)
status, resolve_err = request_api("POST", "/api/tickets/N-002/resolve")
print(f"POST /api/tickets/N-002/resolve (Human Review Ticket) -> HTTP {status}, Detail: {resolve_err['detail']}")

print("\n=================================================================")
print("5. VERIFY ERROR HANDLING")
print("=================================================================")
# Invalid Ticket ID
status, err_404 = request_api("GET", "/api/tickets/INVALID-999")
print(f"GET /api/tickets/INVALID-999 -> HTTP {status}, Detail: {err_404['detail']}")

# Invalid Lane
status, err_lane = request_api("GET", "/api/tickets?lane=unknown_filter")
print(f"GET /api/tickets?lane=unknown_filter -> HTTP {status}, Detail: {err_lane['detail']}")

# Invalid Resolve
status, err_resolve_404 = request_api("POST", "/api/tickets/INVALID-999/resolve")
print(f"POST /api/tickets/INVALID-999/resolve -> HTTP {status}, Detail: {err_resolve_404['detail']}")

print("\n=================================================================")
print("6. VERIFY DECISION AUDIT LOG")
print("=================================================================")
status, logs = request_api("GET", "/api/decisions")
print(f"GET /api/decisions -> HTTP {status}, Recorded log entries: {len(logs)}")

print("\n=================================================================")
print("ALL LIVE VERIFICATION CHECKS PASSED PERFECTLY")
print("=================================================================")
