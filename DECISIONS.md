# Zepto Support Ticket Manager — Architecture Decision Log (ADR)

> **Purpose**: Record key architectural decisions made by the team.  
> Only append decisions that have been formally agreed upon. Do NOT invent unapproved architectural choices.

---

## Decision 1: Problem Statement Selection
* **Date**: 2026-08-08
* **Status**: Accepted
* **Context**: Participated in DigiPlus IT Agentic AI Hackathon.
* **Decision**: Select **Problem Statement Q4: Zepto Support Ticket Manager**.
* **Rationale**: Problem Q4 offers a clear combination of vector/text similarity search, deterministic business rule verification, automated decision routing, and customer interaction simulation.

---

## Decision 2: Two-Developer Setup & Repository Organization
* **Date**: 2026-08-08
* **Status**: Accepted
* **Context**: Team consists of two developers working concurrently using AI coding assistants.
* **Decision**: 
  * Developer 1 owns Backend (`backend/`).
  * Developer 2 owns Frontend (`frontend/`).
  * Shared documentation resides at repository root (`/`) and `docs/`.
* **Rationale**: Clear folder boundaries prevent file conflicts during concurrent Git workflow and parallel AI-assisted development.

---

## Decision 3: Frontend / Backend Separation
* **Date**: 2026-08-08
* **Status**: Accepted
* **Context**: Need a scalable, maintainable web architecture with public deployment capability.
* **Decision**: Build a separate React-based dashboard frontend and FastAPI-based Python REST API backend.
* **Rationale**: Decouples UI rendering from heavy Python data manipulation, vector similarity algorithms, and business logic execution.

---

## Decision 4: TF-IDF + Cosine Similarity for MVP
* **Date**: 2026-08-08
* **Status**: Accepted
* **Context**: Need fast, reliable, lightweight similarity matching for 300 historical resolved tickets without complex heavy infrastructure dependencies.
* **Decision**: Use `scikit-learn` TF-IDF Vectorizer + Cosine Similarity as the initial similarity engine for MVP.
* **Rationale**: Simple, deterministic, fast, zero-cost, easy to run locally and deploy without requiring vector database cloud services.

---

## Decision 5: Prioritize Core Functionality Over Bonus Features
* **Date**: 2026-08-08
* **Status**: Accepted
* **Context**: Hackathon deadline and evaluation requirements.
* **Decision**: Focus on core requirements (similarity search, top-3 precedents, business rules, decision engine, simulated action, draft reply, explanation, two-lane frontend UI) before considering bonus features.
* **Rationale**: Ensures a complete, working, robust submission that meets all official criteria.

---

## Decision 6: AI Provider Selection Deferred
* **Date**: 2026-08-08
* **Status**: Accepted
* **Context**: Multiple LLM providers available (OpenAI, Gemini, Anthropic, local models).
* **Decision**: Keep AI model provider choice open. Do NOT hardcode or lock the project to a specific AI provider during setup.
* **Rationale**: Ensures backend deterministic logic and decision rules remain fully decoupled from LLM text generation capabilities.

---

## Decision 7: Use Actual CSV Datasets Without Fabrication
* **Date**: 2026-08-08
* **Status**: Accepted
* **Context**: Hackathon dataset provided (`resolved_tickets.csv`, `new_tickets.csv`, `orders_context.csv`).
* **Decision**: Process raw CSV files as provided in `data/`. Do NOT invent fake datasets or modify raw column structures.
* **Rationale**: Guarantees system compatibility with evaluation data and preserves ground-truth test scenarios.

---

## Decision 8: Deterministic Business Rules Enforced in Backend
* **Date**: 2026-08-08
* **Status**: Accepted
* **Context**: Crucial safety rules (e.g. cancelled orders cannot be redelivered; refunds cannot exceed order value; precedent disagreements cannot be guessed).
* **Decision**: All business rules and guardrails must be deterministically checked in Python service code (`order_context_service.py`, `decision_service.py`), not delegated to non-deterministic LLM prompts.
* **Rationale**: Ensures strict compliance, 100% predictability, and safe automated decision-making.
