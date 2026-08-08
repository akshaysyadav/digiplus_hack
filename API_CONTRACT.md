# Zepto Support Ticket Manager — API Contract

> **Status**: Draft / Coordination Specification  
> **Notice**: All request/response JSON schemas are **TO BE FINALIZED BY BACKEND DEVELOPER**.  
> This contract serves as an agreement between Developer 1 (Backend) and Developer 2 (Frontend).

---

## High-Level API Responsibilities

The API must expose endpoints to support the two-lane dashboard and ticket evaluation workflow:

1. **Ticket List Retrieval**: Fetch all incoming customer tickets with filter by decision status (All, Auto-Resolved, Needs-Human).
2. **Ticket Detail Retrieval**: Fetch full context for a single ticket, including linked order context.
3. **Precedents Search**: Fetch top-3 historical resolved tickets matching an incoming ticket.
4. **Decision Engine & Evaluation**: Run automated evaluation (similarity check, action agreement check, business rule validation).
5. **Simulated Action Execution**: Generate simulated resolution (refund, redelivery, coupon, etc.).
6. **Draft Reply & Explanation Generation**: Retrieve customer draft message and explanation of "why this action?".

---

## Planned API Endpoints Summary

### 1. Health Check
* **Endpoint**: `GET /api/health`
* **Purpose**: Verify backend API status.
* **Status**: TO BE FINALIZED BY BACKEND DEVELOPER

---

### 2. Get All Tickets
* **Endpoint**: `GET /api/tickets`
* **Purpose**: Fetch list of tickets for dashboard rendering.
* **Query Parameters** (Planned):
  * `lane`: `all` | `auto_resolve` | `human_review` (optional)
* **Response Schema**: TO BE FINALIZED BY BACKEND DEVELOPER

---

### 3. Get Ticket Details
* **Endpoint**: `GET /api/tickets/{ticket_id}`
* **Purpose**: Fetch full detail of a specific incoming ticket including associated `orders_context`.
* **Response Schema**: TO BE FINALIZED BY BACKEND DEVELOPER

---

### 4. Evaluate Ticket (Core Engine)
* **Endpoint**: `POST /api/tickets/{ticket_id}/evaluate`
* **Purpose**: Run end-to-end processing pipeline on a ticket:
  1. Retrieve top-3 precedents from `resolved_tickets.csv`
  2. Compute confidence / similarity score
  3. Verify historical action agreement
  4. Fetch order details from `orders_context.csv`
  5. Apply business rule guardrails (cancelled order check, refund cap check)
  6. Output decision: `AUTO_RESOLVE` or `HUMAN_REVIEW`
  7. Generate simulated action, draft reply, and explanation text
* **Response Schema**: TO BE FINALIZED BY BACKEND DEVELOPER

---

### 5. Get Decision Log
* **Endpoint**: `GET /api/decisions`
* **Purpose**: Retrieve historical decision logs and audit trail for executed tickets.
* **Response Schema**: TO BE FINALIZED BY BACKEND DEVELOPER

---

## Data Model Contract Placeholders

The following data models will be formally defined in `backend/app/models/schemas.py`:

* `TicketSchema`: TO BE FINALIZED BY BACKEND DEVELOPER
* `OrderContextSchema`: TO BE FINALIZED BY BACKEND DEVELOPER
* `PrecedentSchema`: TO BE FINALIZED BY BACKEND DEVELOPER
* `DecisionResultSchema`: TO BE FINALIZED BY BACKEND DEVELOPER
* `ActionSimulationSchema`: TO BE FINALIZED BY BACKEND DEVELOPER
* `DraftReplySchema`: TO BE FINALIZED BY BACKEND DEVELOPER
