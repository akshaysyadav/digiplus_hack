# Zepto Support Ticket Manager

[![Hackathon](https://img.shields.io/badge/Hackathon-DigiPlus%20IT%20Agentic%20AI-blue.svg)](https://digiplus.it)
[![Problem Statement](https://img.shields.io/badge/Problem%20Statement-Q4%20Zepto%20Support-orange.svg)]()
[![Status](https://img.shields.io/badge/Status-Initial%20Structure%20%2F%20Setup-brightgreen.svg)]()

> **DigiPlus IT Agentic AI Hackathon — Problem Statement Q4**  
> An intelligent customer support ticket resolution system powered by similarity search, precedent analysis, deterministic business rules, and simulated automated actions.

---

## About The System

Zepto Support Ticket Manager automates customer support ticket evaluation while upholding strict quality and safety standards:

1. **Ingests Incoming Support Tickets**: Ingests new support tickets and retrieves linked order contexts.
2. **Precedent Similarity Search**: Searches historical resolved tickets using TF-IDF vector similarity to identify the **top 3 precedents**.
3. **Action Agreement Evaluation**: Checks whether past similar tickets agree on the appropriate resolution action.
4. **Order Context & Guardrail Verification**: Enforces critical business guardrails:
   * Cancelled orders must **never** trigger redelivery.
   * Refund amounts must **never** exceed the original order value.
   * Precedent disagreements or low similarity score force **Human Review**.
5. **Two-Lane Routing**: Directs tickets to **AUTO RESOLVE** or **HUMAN REVIEW**.
6. **Action Simulation & Draft Generation**: Simulates resolutions (refund, redelivery, coupon, etc.), drafts customer-facing responses, and provides audit explanations ("Why this action?").

---

## High-Level Architecture

```
[ Incoming Customer Ticket ]
            │
            ▼
┌───────────────────────────────┐
│     Similarity Engine         │ ───► Retrieves Top 3 Precedents
│   (TF-IDF + Cosine Similarity)│      from resolved_tickets.csv
└───────────────┬───────────────┘
                │
                ▼
┌───────────────────────────────┐
│   Deterministic Guardrails    │ ───► Validates Order Context & Values
│      & Decision Engine        │      from orders_context.csv
└───────────────┬───────────────┘
                │
        ┌───────┴───────┐
        ▼               ▼
 ┌─────────────┐ ┌──────────────┐
 │ AUTO        │ │ HUMAN        │
 │ RESOLVE     │ │ REVIEW       │
 └──────┬──────┘ └──────────────┘
        │
        ▼
┌───────────────────────────────┐
│  Action Simulation & Draft    │ ───► Simulated Action + Customer Reply
│      Customer Reply           │      + Audit Explanation
└───────────────────────────────┘
```

---

## Datasets Overview

Located in `data/sample_data/`:

* **`resolved_tickets.csv`** (`RESOLV~1.CSV`): 300 historical resolved tickets  
  *Columns*: `ticket_id`, `category`, `description`, `resolution_action`, `resolution_note`, `time_to_resolve_min`, `csat`
* **`new_tickets.csv`** (`NEW_TI~1.CSV`): 30 incoming test tickets  
  *Columns*: `ticket_id`, `created_at`, `order_id`, `description`
* **`orders_context.csv`** (`ORDERS~1.CSV`): 30 customer order context records  
  *Columns*: `order_id`, `items`, `value_inr`, `delivery_time_min`, `delivery_status`


---

## Tech Stack & Project Organization

* **Frontend**: React application (`frontend/`) 
* **Backend**: FastAPI REST API (`backend/`) 
* **Documentation**: Architecture specs & decision logs (`docs/`, `PROJECT_CONTEXT.md`, `DECISIONS.md`).

---

## Setup & Development Instructions

> Note: Project features are currently in the initial project setup phase. 

### Backend Setup
```bash
cd backend
python -m venv venv
# Activate venv (Windows: venv\Scripts\activate | Unix: source venv/bin/activate)
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend Setup 
```bash
cd frontend
npm install
npm run dev
```

---

## Deployment Plan

* **Backend**: FastAPI deployed to public REST host.
* **Frontend**: React Dashboard deployed to public web host.
* **Repository**: Public GitHub Repository.


