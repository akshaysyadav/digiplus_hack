# Zepto Support Ticket Manager — Project Context

> **Shared Memory & Single Source of Truth**  
> All team members (Developer 1, Developer 2) and AI coding assistants MUST read this file before starting any work.

---

## 1. Project Overview

* **Project Name**: Zepto Support Ticket Manager
* **Hackathon**: DigiPlus IT Agentic AI Hackathon
* **Problem Statement**: Problem Statement Q4 — Zepto Support Ticket Manager

### Problem Summary
Build an intelligent, agentic support ticket handling system for Zepto that receives incoming customer tickets, evaluates historical precedence using similarity search, validates business rules against order context, and decides whether a ticket can be **AUTO RESOLVED** or requires **HUMAN REVIEW**. For auto-resolved tickets, the system simulates the appropriate resolution action (refund, redelivery, coupon, etc.) and generates a customer-facing draft reply with a clear explanation of why that decision was made.

---

## 2. Core Workflow (11 Steps)

1. **Receive New Ticket**: Ingest incoming support ticket payload (`ticket_id`, text, metadata).
2. **Similarity Search**: Find historical resolved tickets matching the issue context.
3. **Top 3 Precedents**: Retrieve top 3 most similar past resolved tickets.
4. **Evaluate Confidence**: Calculate similarity score & confidence metric.
5. **Historical Action Agreement Check**: Check whether historical top precedents agreed on the resolution action.
6. **Order Context & Business Rules Check**: Cross-examine order status (e.g. cancelled vs active) and order values.
7. **Decision Gate**:
   * **AUTO RESOLVE**: High similarity, action agreement, and all business rules satisfied.
   * **HUMAN REVIEW**: Low similarity, precedent disagreement, or rule violation.
8. **Simulate Action**: For auto-resolved cases, simulate action (e.g., refund, redelivery, coupon, escalation, apology).
9. **Draft Customer Reply**: Generate a clear, empathetic customer-facing response.
10. **Explain Decision**: Provide clear "Why this action?" audit explanation.
11. **Log Decision**: Persist structured decision log for auditing and dashboard rendering.

---

## 3. Actual Dataset Summary

The system operates on **3 official CSV datasets** located in `data/sample_data/`:

| Dataset File | Inspected CSV Schema (Columns) | Record Count |
| :--- | :--- | :--- |
| `resolved_tickets.csv` (`RESOLV~1.CSV`) | `ticket_id`, `category`, `description`, `resolution_action`, `resolution_note`, `time_to_resolve_min`, `csat` | 300 records |
| `new_tickets.csv` (`NEW_TI~1.CSV`) | `ticket_id`, `created_at`, `order_id`, `description` | 30 records |
| `orders_context.csv` (`ORDERS~1.CSV`) | `order_id`, `items`, `value_inr`, `delivery_time_min`, `delivery_status` | 30 records |

> **IMPORTANT**: Datasets live in `data/sample_data/`. DO NOT move, rename, modify, or duplicate raw files. DO NOT invent CSV columns. The backend developer will use these exact schemas when building Pydantic models and data services.


---

## 4. Important Business Rules

1. **Strong Historical Precedents**: High similarity with consistent past resolutions allows auto-resolution.
2. **Weak Similarity**: Low similarity scores must force route to **HUMAN REVIEW**.
3. **Precedent Disagreement**: If top-3 precedents disagree on the appropriate action, the system **MUST NOT GUESS** — it must route to **HUMAN REVIEW**.
4. **Cancelled Order Safety**: A cancelled order must **NEVER** trigger a redelivery action.
5. **Refund Cap**: Refund amount must **NEVER** exceed the original order value.
6. **Action Variation Taxonomy**: Historical actions may contain variations that must be handled safely:
   * `partial_refund`
   * `full_refund`
   * `refund_reissue`
   * `redelivery`
   * `coupon`
   * `escalation`
   * `apology_no_action`

---

## 5. Technical Direction & Architecture

* **Frontend**: React-based modern dashboard application (`frontend/`).
* **Backend**: Python-based REST API built with FastAPI (`backend/`).
* **Similarity Matching**: TF-IDF + Cosine Similarity is accepted and recommended for the MVP baseline.
* **LLM / AI Integration**: Decoupled from deterministic decision logic. AI provider choice is kept modular.
* **Separation of Concerns**: Deterministic business rules & decision engine live strictly in backend python services, separate from LLM text generation.

---

## 6. Team Ownership & Setup

| Developer | Scope | Primary Working Directory |
| :--- | :--- | :--- |
| **Developer 1** | Backend (FastAPI, Similarity, Decision Logic, API) | `backend/` |
| **Developer 2** | Frontend (React Dashboard, Two-lane view, UI) | `frontend/` |
| **Shared** | Documentation, Architecture, API Contracts | Root (`/`) & `docs/` |

---

## 7. Mandatory Development Rules

1. **Read `PROJECT_CONTEXT.md`** before making changes.
2. **Read `TASKS.md`** before starting work.
3. **Read `DECISIONS.md`** before changing architecture.
4. **Do not invent dataset columns.**
5. **Do not invent business rules.**
6. **Do not rewrite working code unnecessarily.**
7. **Do not change another developer's area without coordination.**
8. **Backend developer owns `backend/`.**
9. **Frontend developer owns `frontend/`.**
10. **Shared architectural changes must be documented** in `docs/` and `DECISIONS.md`.
11. **AI-generated code must be reviewed** before committing.
12. **Keep the MVP simple and deployable.**
13. **Core functionality comes before bonus features.**
