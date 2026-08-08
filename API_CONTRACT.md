# Zepto Support Ticket Manager — API Contract

> **Status**: Finalized (Backend Implemented & Verified)  
> **Base URL**: `http://localhost:8000` (or configured public host)  
> **Prefix**: `/api`

---

## 1. Endpoints Summary

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/health` | Service health status and dataset readiness |
| `GET` | `/api/tickets` | List incoming tickets with decision lanes (supports `?lane=auto_resolve` or `?lane=human_review`) |
| `GET` | `/api/tickets/{ticket_id}` | Full ticket detail with order context, top-3 precedents, evaluation, simulated action, and draft reply |
| `POST` | `/api/tickets/{ticket_id}/evaluate` | Run/re-evaluate ticket through decision pipeline and record audit log |
| `POST` | `/api/tickets/{ticket_id}/resolve` | Execute / confirm simulated resolution action |
| `GET` | `/api/decisions` | Retrieve decision audit history log |

---

## 2. Detailed Endpoint Contracts

### 1. Health Check
* **Endpoint**: `GET /api/health`
* **Response `200 OK`**:
```json
{
  "status": "healthy",
  "datasets": "3 CSV files loaded and cached",
  "similarity_engine": "TF-IDF + Cosine Similarity ready",
  "decision_engine": "Deterministic guardrails active"
}
```

---

### 2. List Tickets
* **Endpoint**: `GET /api/tickets`
* **Query Parameters**:
  * `lane` (optional, string): `all` | `auto_resolve` | `human_review`
* **Response `200 OK`**:
```json
[
  {
    "ticket_id": "N-005",
    "created_at": "2026-08-07T14:24:00",
    "order_id": "ORD-9905",
    "description": "milk packet missing from my order",
    "decision": "AUTO_RESOLVE",
    "confidence_score": 1.0,
    "selected_action": "redelivery",
    "delivery_status": "delivered"
  }
]
```

---

### 3. Get Ticket Details & 4. Evaluate Ticket
* **Endpoints**: 
  * `GET /api/tickets/{ticket_id}`
  * `POST /api/tickets/{ticket_id}/evaluate`
* **Response `200 OK`**:
```json
{
  "ticket_id": "N-005",
  "created_at": "2026-08-07T14:24:00",
  "description": "milk packet missing from my order",
  "order": {
    "order_id": "ORD-9905",
    "items": 1,
    "value_inr": 412,
    "delivery_time_min": 41,
    "delivery_status": "delivered"
  },
  "precedents": [
    {
      "precedent_id": "H-1000",
      "category": "missing_item",
      "description": "milk packet missing from my order",
      "resolution_action": "redelivery",
      "resolution_note": "missing item re-sent",
      "similarity_score": 1.0,
      "csat": 5
    },
    {
      "precedent_id": "H-1007",
      "category": "missing_item",
      "description": "milk packet missing from my order",
      "resolution_action": "redelivery",
      "resolution_note": "missing item re-sent",
      "similarity_score": 1.0,
      "csat": 4
    },
    {
      "precedent_id": "H-1038",
      "category": "missing_item",
      "description": "milk packet missing from my order",
      "resolution_action": "redelivery",
      "resolution_note": "missing item re-sent",
      "similarity_score": 1.0,
      "csat": 3
    }
  ],
  "evaluation": {
    "similarity_score": 1.0,
    "exact_action_agreement": true,
    "action_family_agreement": true,
    "decision": "AUTO_RESOLVE",
    "confidence_score": 1.0,
    "selected_action": "redelivery",
    "reasoning": "High similarity (1.00) with unanimous precedent agreement (3/3: redelivery). All order context guardrails passed.",
    "guardrails": {
      "similarity_threshold_passed": true,
      "cancelled_redelivery_blocked": false,
      "refund_cap_enforced": false,
      "escalation_precedent_detected": false
    }
  },
  "simulated_action": {
    "action": "redelivery",
    "amount_inr": null,
    "status": "SIMULATED_SUCCESS",
    "note": "Simulated dispatch: Replacement items scheduled for immediate redelivery.",
    "is_simulated": true
  },
  "draft_reply": {
    "recipient": "Customer",
    "subject": "Your replacement items for Order #ORD-9905 are on their way",
    "body": "Hi there, we sincerely apologize that items were missing or incorrect in your order #ORD-9905. We have arranged an immediate priority redelivery at no extra cost to you. Our delivery partner will be at your doorstep shortly.",
    "explanation": "Auto-resolved via REDELIVERY based on unanimous historical precedent agreement (3/3). Order #ORD-9905 is active/delivered, satisfying all safety guardrails."
  }
}
```

---

### 5. Resolve Ticket Action
* **Endpoint**: `POST /api/tickets/{ticket_id}/resolve`
* **Response `200 OK`**:
```json
{
  "action": "redelivery",
  "amount_inr": null,
  "status": "SIMULATED_SUCCESS",
  "note": "Simulated dispatch: Replacement items scheduled for immediate redelivery.",
  "is_simulated": true
}
```

---

### 6. Get Decision Audit Log
* **Endpoint**: `GET /api/decisions`
* **Response `200 OK`**:
```json
[
  {
    "ticket_id": "N-005",
    "timestamp": "2026-08-08T10:50:00.000000+00:00",
    "order_id": "ORD-9905",
    "decision": "AUTO_RESOLVE",
    "confidence_score": 1.0,
    "selected_action": "redelivery",
    "reasoning": "High similarity (1.00) with unanimous precedent agreement (3/3: redelivery). All order context guardrails passed.",
    "top_precedent_ids": ["H-1000", "H-1007", "H-1038"],
    "simulated_action_status": "SIMULATED_SUCCESS"
  }
]
```

---

## 3. Pydantic Models Reference

All schemas are declared in `backend/app/models/schemas.py`:
- `OrderContext`: Order status and pricing context.
- `PrecedentMatch`: Historical ticket match with similarity score and CSAT.
- `GuardrailResults`: Explicit boolean flags for guardrails.
- `EvaluationResult`: Decision, similarity score, exact & family agreement flags, confidence, and reasoning.
- `SimulatedAction`: Simulated action payload clearly designated as simulated.
- `DraftReply`: Customer-facing draft reply and "Why this action?" explanation.
- `TicketDetailResponse`: Consolidated envelope for ticket detail view.
- `TicketListItem`: Summary item for dashboard lane lists.
- `DecisionLogEntry`: Audit trail entry.
