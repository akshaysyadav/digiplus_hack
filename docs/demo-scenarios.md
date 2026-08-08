# Demo Scenarios Specification — Zepto Support Ticket Manager

> **Placeholder Test Scenarios for Verification & Demonstrations**  
> These scenarios outline key ground-truth validation cases that will be tested during system verification.

---

## Scenario 1: Strong Precedent → Auto-Resolve
* **Description**: Incoming ticket matches historical resolved tickets with high similarity (>0.85) and consistent past resolutions (e.g. all 3 past cases issued full refund for missing item).
* **Expected Decision**: `AUTO_RESOLVE`
* **Expected Simulated Action**: `full_refund`
* **Expected Outcome**: Ticket assigned to Auto-Resolved lane; customer draft reply and explanation rendered.

---

## Scenario 2: Weak Similarity → Human Review
* **Description**: Incoming ticket describes an ambiguous or rare issue with low similarity score (<0.60) across all historical resolved tickets.
* **Expected Decision**: `HUMAN_REVIEW`
* **Reason Flag**: `Weak Similarity Score`
* **Expected Outcome**: Ticket assigned to Needs-Human lane for agent inspection.

---

## Scenario 3: Conflicting Actions → Human Review
* **Description**: Top 3 matching historical precedents show inconsistent actions (e.g. Precedent 1: `full_refund`, Precedent 2: `redelivery`, Precedent 3: `apology_no_action`).
* **Expected Decision**: `HUMAN_REVIEW`
* **Reason Flag**: `Precedent Action Disagreement (System Must Not Guess)`
* **Expected Outcome**: System avoids guessing and routes ticket to human agent.

---

## Scenario 4: Cancelled Order → No Redelivery Guardrail
* **Description**: Customer requests redelivery for an item on an order that is marked as `CANCELLED` in `orders_context.csv`.
* **Expected Decision**: `HUMAN_REVIEW`
* **Reason Flag**: `Business Rule Violation: Cancelled Order Cannot Trigger Redelivery`
* **Expected Outcome**: System blocks redelivery simulation and flags for human review.

---

## Scenario 5: Refund Capped by Order Value Guardrail
* **Description**: Customer requests a refund amount that exceeds the original order value recorded in `orders_context.csv`.
* **Expected Decision**: `HUMAN_REVIEW` (or auto-capped refund)
* **Reason Flag**: `Business Rule Violation: Refund Amount Exceeds Order Value`
* **Expected Outcome**: System prevents over-refunding and logs rule enforcement.
