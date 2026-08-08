# Decision Flow Logic — Zepto Support Ticket Manager

> **Conceptual Decision Tree & Routing Rules**

---

## Decision Logic Specification

When a new customer support ticket arrives, the decision engine executes the following evaluation pipeline:

```
                          [ Incoming Ticket ]
                                   │
                                   ▼
                   [ Compute Top 3 Precedents & Scores ]
                                   │
                    Is Similarity Score >= Threshold?
                                ├── NO ──► [ HUMAN REVIEW (Weak Similarity) ]
                                │
                               YES
                                │
                                ▼
               Do Top 3 Precedents Agree on Action?
                                ├── NO ──► [ HUMAN REVIEW (Action Disagreement) ]
                                │
                               YES
                                │
                                ▼
                  Is Associated Order Cancelled?
                  AND Proposed Action is Redelivery?
                                ├── YES ──► [ HUMAN REVIEW (Cancelled Order Guardrail) ]
                                │
                                NO
                                │
                                ▼
                  Is Proposed Refund Amount > Order Total?
                                ├── YES ──► [ HUMAN REVIEW (Refund Cap Exceeded) ]
                                │
                                NO
                                │
                                ▼
                       [ AUTO RESOLVE ]
                Simulate Action + Draft Reply
```

---

## Detailed Gate Explanations

### Gate 1: Similarity Threshold
* Evaluates TF-IDF cosine similarity score between incoming ticket and top historical resolved tickets.
* If similarity score is below `SIMILARITY_THRESHOLD_HIGH`, system routes to **HUMAN REVIEW**.

### Gate 2: Precedent Action Agreement
* Inspects the resolution actions taken in top-3 historical matches.
* If past precedents contain conflicting actions (e.g. 1 refund, 1 redelivery, 1 escalation), system **does not guess** and routes to **HUMAN REVIEW**.

### Gate 3: Cancelled Order Safety Guardrail
* Fetches linked order details from `orders_context.csv`.
* If order status is `CANCELLED` and proposed action is `redelivery`, system flags a violation and routes to **HUMAN REVIEW**.

### Gate 4: Refund Amount Cap Guardrail
* Calculates maximum allowable refund based on `order_total` in `orders_context.csv`.
* If proposed refund exceeds order value, system caps refund or routes to **HUMAN REVIEW**.
