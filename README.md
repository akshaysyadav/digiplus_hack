# Zepto Support Ticket Manager

[![Hackathon](https://img.shields.io/badge/Hackathon-DigiPlus%20IT%20Agentic%20AI-blue.svg)](https://digiplus.it)
[![Problem Statement](https://img.shields.io/badge/Problem%20Statement-Q4%20Zepto%20Support-orange.svg)]()
[![Tests](https://img.shields.io/badge/Tests-42%2F42%20Passing-brightgreen.svg)]()
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg?logo=fastapi&logoColor=white)]()
[![React](https://img.shields.io/badge/Frontend-React%20%2B%20Vite-61DAFB.svg?logo=react&logoColor=black)]()

> **DigiPlus IT Agentic AI Hackathon — Problem Statement Q4**  
> An intelligent, safety-first customer support ticket resolution engine combining TF-IDF historical precedent matching, deterministic business guardrails, automated action simulation, Gemini AI-assisted draft generation, and real-time persistent ticket simulation.

---

## Table of Contents
1. [System Architecture & Workflow](#system-architecture--workflow)
2. [Hackathon Requirement Mapping](#hackathon-requirement-mapping)
3. [Official Datasets](#official-datasets)
4. [Core Decision Engine & Safety Guardrails](#core-decision-engine--safety-guardrails)
5. [Gemini AI & Grounded Reply Layer](#gemini-ai--grounded-reply-layer)
6. [Real-Time Ticket Simulation & Persistence](#real-time-ticket-simulation--persistence)
7. [Two-Lane React Dashboard](#two-lane-react-dashboard)
8. [API Reference](#api-reference)
9. [Performance & Baseline Benchmark](#performance--benchmark)
10. [Test Suite & Verification](#test-suite--verification)
11. [Quick Demo Scenarios](#quick-demo-scenarios)
12. [Setup & Execution Instructions](#setup--execution-instructions)
13. [Deployment Readiness](#deployment-readiness)

---

## System Architecture & Workflow

The platform operates on a **safety-first deterministic authority model**:
- **Deterministic Engine**: Decides *WHAT* resolution action is safe, compliant, and authorized.
- **Gemini Generative Layer**: Crafts *HOW* the customer-facing response is articulated.

```
                  [ Incoming Support Ticket ]
                              │
                              ▼
                 [ Order Context Lookup ]
                 (orders_context.csv / 30 records)
                              │
                              ▼
            [ TF-IDF + Cosine Similarity Search ]
            (300 Historical Resolved Precedents)
                              │
                              ▼
                 [ Top-3 Precedent Retrieval ]
                              │
                              ▼
               [ Action Agreement Analysis ]
               (Exact vs Family vs Conflict)
                              │
                              ▼
             [ Deterministic Safety Guardrails ]
           ├── Similarity Gate (Threshold: 0.65)
           ├── Cancelled Order Redelivery Block
           ├── Order Value Refund Cap
           └── Escalation Precedent Handling
                              │
                              ▼
                 [ Confidence Score Formula ]
                (60% Sim + 30% Agree + 10% Valid)
                              │
              ┌───────────────┴───────────────┐
              ▼                               ▼
       [ AUTO_RESOLVE ]                [ HUMAN_REVIEW ]
       (Safe & High Confidence)        (Suggested Action + Guardrail Notes)
              │                               │
              ▼                               ▼
       [ Simulate Action ]             [ Block Direct Execution ]
       (Redelivery/Refund/Coupon)      (Human Agent Sign-off Required)
              │                               │
              └───────────────┬───────────────┘
                              ▼
               [ Customer Reply Generation ]
               (Gemini AI + Deterministic Fallback)
                              │
                              ▼
               [ Decision / Audit Logging ]
                              │
                              ▼
           [ Local JSON Persistence & Two-Lane Board ]
           (data/simulated_tickets.json)
```

---

## Hackathon Requirement Mapping

| Problem Statement Requirement | Implemented Component | Status |
| :--- | :--- | :---: |
| **Historical Precedent Matching** | TF-IDF Vectorizer + Cosine Similarity over 300 resolved tickets | ✅ Verified |
| **Top-K Precedent Retrieval** | Top-3 precedent ranking with similarity scores and resolution notes | ✅ Verified |
| **Action Agreement Logic** | Exact agreement, same-family agreement, and conflict detection | ✅ Verified |
| **Confidence Scoring** | Normalized formula: $0.60 \times \text{Sim} + 0.30 \times \text{Agree} + 0.10 \times \text{Valid}$ | ✅ Verified |
| **Two-Lane Routing** | Deterministic separation into `AUTO_RESOLVE` and `HUMAN_REVIEW` | ✅ Verified |
| **Cancelled-Order Protection** | Hard guardrail blocking redelivery on cancelled orders | ✅ Verified |
| **Refund Cap Protection** | Guardrail capping maximum simulated refund at order total | ✅ Verified |
| **Weak Similarity Safety** | Out-of-distribution tickets (<0.65 similarity) route to `HUMAN_REVIEW` | ✅ Verified |
| **Simulated Action Execution** | Automated action simulation (`redelivery`, `refund`, `coupon`) | ✅ Verified |
| **Suggested Action for Human** | Safe fallback suggestion provided when human review is required | ✅ Verified |
| **Audit & Explanation** | Structured "Why this action?" audit trail with precedent citations | ✅ Verified |
| **Customer Reply Drafting** | Context-grounded Gemini AI generation with instant template fallback | ✅ Verified |
| **Decision Audit Logging** | Endpoint `GET /api/decisions` tracking all evaluations | ✅ Verified |
| **Real-Time Ticket Simulation** | `POST /api/tickets/simulate` with verified order context selector | ✅ Verified |
| **Simulated Ticket Persistence** | Lightweight atomic JSON persistence (`data/simulated_tickets.json`) | ✅ Verified |
| **Two-Lane Web Dashboard** | Interactive React 18 + Vite UI with live state updates | ✅ Verified |

---

## Official Datasets

The system loads and caches three official baseline datasets from `data/sample_data/`:

| Dataset | Path | Size | Description |
| :--- | :--- | :---: | :--- |
| **Resolved Tickets** | `data/sample_data/resolved_tickets.csv` | 300 rows | Historical precedents with resolutions, notes, and CSAT scores |
| **Incoming Tickets** | `data/sample_data/new_tickets.csv` | 30 rows | Incoming customer tickets for evaluation |
| **Orders Context** | `data/sample_data/orders_context.csv` | 30 rows | Linked order metadata (`items`, `value_inr`, `delivery_status`) |

> **Note**: The original CSV files are strictly read-only and preserved in their original state.

---

## Core Decision Engine & Safety Guardrails

### 1. Similarity Engine
- Vectorizes customer issue descriptions against historical precedents using **TF-IDF + Cosine Similarity**.
- Retrieves the **Top 3** closest precedents.
- **Safety Gate**: Threshold is set to **`0.65`**. Queries scoring below 0.65 automatically route to `HUMAN_REVIEW`.

### 2. Action Agreement Analysis
Evaluates consistency across the top 3 precedents:
1. **Exact Action Agreement**: All precedents recommend the exact same action (e.g., `[redelivery, redelivery, redelivery]`).
2. **Same Action Family Agreement**: Precedents share an operational family (e.g., `[partial_refund, full_refund, full_refund]`).
3. **Conflicting Precedent Actions**: Precedents disagree on resolution family (e.g., `[redelivery, partial_refund, redelivery]`). The engine safely routes the ticket to `HUMAN_REVIEW` and computes a non-executing `suggested_action` for the human agent.

### 3. Business Safety Guardrails
Hard constraints enforced before any automated action is authorized:
- **`cancelled_redelivery_blocked`**: A customer requesting redelivery on a `cancelled` order is **blocked** from automated redelivery.
- **`refund_cap_exceeded_blocked`**: Refund amounts are capped at the actual order value (`value_inr`).
- **`similarity_threshold_passed`**: Weak matches are gated to human review.
- **`escalation_precedent_detected`**: Complex or escalated precedent patterns route to human specialists.

### 4. Confidence Calculation
$$\text{Confidence Score} = (0.60 \times \text{Top Similarity}) + (0.30 \times \text{Action Agreement Score}) + (0.10 \times \text{Order Context Validity})$$

*Business guardrails take absolute precedence over numerical confidence scores.*

---

## Gemini AI & Grounded Reply Layer

### Architectural Boundary
- **Deterministic Authority**: The backend decision engine strictly determines `decision`, `selected_action`, and `guardrails`.
- **Generative Assistant**: Google Gemini (`gemini-1.5-flash`) formats a professional, grounded customer-facing reply and agent reasoning summary.

### Context Grounding & Safety
The prompt receives:
- Exact customer issue description
- Linked order context (`order_id`, item count, delivery status, value)
- Authorized `decision` (`AUTO_RESOLVE` vs `HUMAN_REVIEW`)
- Selected or suggested resolution action
- Triggered guardrail notes

### Resilient Fallback System
If `GEMINI_API_KEY` is missing, or if a network timeout occurs (> 2.5s), the system instantly falls back to grounded deterministic response templates. **The core decision pipeline never fails.**

---

## Real-Time Ticket Simulation & Persistence

### Real-Time Simulation Flow
1. Open dashboard and click **"+ Simulate New Ticket"**.
2. Select a verified order from `orders_context.csv` (or use one-click preset test chips).
3. Enter the customer description.
4. Click **"Evaluate Ticket"** $\rightarrow$ full deterministic evaluation and reply generation execute in **< 1 second**.
5. Form resets on success, closes modal, and highlights the new ticket in the appropriate lane.

### Lightweight JSON Persistence (`data/simulated_tickets.json`)
- **Clean Separation**: Simulated tickets are stored in `data/simulated_tickets.json` without modifying source CSVs.
- **Survives Restarts**: Full evaluated payloads (decision, precedents, guardrails, draft reply) reload on startup in `< 2 ms`.
- **Sequential ID Generation**: IDs (`SIM-001`, `SIM-002`, `SIM-003`, ...) continue sequentially across server restarts.
- **Atomic File Writes**: Writes to `.tmp` file and replaces atomically (`os.replace`) to prevent corruption.
- **Corrupted File Resilience**: Corrupted or invalid JSON falls back gracefully to an empty state with a logged warning.

---

## Two-Lane React Dashboard

The frontend ([`frontend/`](file:///c:/Users/DELL/OneDrive/Desktop/DigiplusHack/digiplus_hack/frontend)) provides an operations dashboard:

- **AUTO-RESOLVED Lane**: Tickets passing all guardrails with simulated resolution execution.
- **NEEDS-HUMAN Lane**: Tickets requiring human oversight with highlighted guardrail flags and pre-computed suggested actions.
- **Detailed Inspection Pane**:
  - **Order Context**: Live metadata (`order_id`, items, INR value, delivery status).
  - **Top-3 Precedents**: Historical matches with individual similarity scores and resolution notes.
  - **Guardrail Checklist**: Visual validation badges for cancelled orders, refund caps, and similarity thresholds.
  - **Draft Customer Reply**: Context-grounded email body ready for transmission or human editing.
  - **"Why this action?" Audit Trail**: Clear explanation of precedent agreement and decision logic.
- **Live Search & Filtering**: Real-time ticket search and lane filtering.

---

## API Reference

Interactive Swagger documentation is available at `http://localhost:8000/docs`.

### Primary Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Service status and version |
| `GET` | `/api/health` | Health check for datasets and engine status |
| `GET` | `/api/tickets` | Evaluated ticket list (`?lane=auto_resolve` or `?lane=human_review`) |
| `GET` | `/api/tickets/{ticket_id}` | Full detail for a single ticket (order, precedents, evaluation, reply) |
| `POST` | `/api/tickets/{ticket_id}/evaluate` | Run or re-evaluate decision pipeline on a ticket |
| `POST` | `/api/tickets/{ticket_id}/resolve` | Execute simulated action (blocked if ticket is in `HUMAN_REVIEW`) |
| `POST` | `/api/tickets/simulate` | Ingest and evaluate a new real-time ticket with JSON persistence |
| `GET` | `/api/orders` | List verified order contexts for simulation selector |
| `GET` | `/api/decisions` | Audit history and decision logs |

---

## Performance & Benchmark

| Operation | Measured Latency | Optimization Applied |
| :--- | :---: | :--- |
| `POST /api/tickets/simulate` | **~715 ms** | End-to-end evaluation + Gemini draft + atomic disk write |
| `GET /api/tickets` (30 CSV + simulated) | **~20 ms** | Fast list-item evaluation without redundant LLM calls |
| Startup Persistence Loading | **< 2 ms** | In-memory JSON parsing at service initialization |

### Baseline 30-Ticket Distribution
- Total Incoming CSV Tickets: **30**
- `AUTO_RESOLVE`: **2** (`N-000`, `N-005`)
- `HUMAN_REVIEW`: **28**

> **Safety-First Posture**: The higher proportion of `HUMAN_REVIEW` reflects strict real-world business guardrails (preventing unverified refunds, blocking cancelled-order redeliveries, and flagging precedent conflicts).

---

## Test Suite & Verification

The test suite includes **42 automated unit and integration tests** passing with 100% success:

```text
============================= test session starts =============================
platform win32 -- Python 3.12.0, pytest-9.1.1
rootdir: C:\Users\DELL\OneDrive\Desktop\DigiplusHack\digiplus_hack
collected 42 items

backend/tests/test_api.py ...................                            [ 45%]
backend/tests/test_persistence.py .........                              [ 66%]
backend/tests/test_services.py ..............                            [100%]

======================== 42 passed, 1 warning in 9.36s ========================
```

### Coverage Highlights
- **API Contract**: All HTTP endpoints, lane filtering, error handling, and 404/400 validation.
- **Decision Engine**: TF-IDF similarity, exact/family agreement, tie-breaking, and confidence weighting.
- **Guardrails**: Cancelled order redelivery blocks, refund caps, and out-of-distribution queries.
- **AI & Fallback**: Gemini structured generation, missing API key handling, and network timeout fallback.
- **Persistence**: JSON file creation, restart reload, sequential ID continuity, and corrupted storage recovery.

---

## Quick Demo Scenarios

| Scenario | Input | Order Context | Decision | Selected / Suggested Action | Reason |
| :--- | :--- | :--- | :---: | :---: | :--- |
| **1. Missing Item (Delivered)** | *"milk packet missing from my order"* | `ORD-9905` (`delivered`) | `AUTO_RESOLVE` | `redelivery` (100% confidence) | Strong historical match with 3/3 precedent agreement on delivered order. |
| **2. Cancelled Order Protection** | *"milk packet missing from my order"* | `ORD-9902` (`cancelled`) | `HUMAN_REVIEW` | `human_review` (Redelivery blocked) | Cancelled-order guardrail prevents automated dispatch. Reply promises no redelivery. |
| **3. Novel Out-of-Distribution** | *"the delivery person was rude and shouted"* | `ORD-9908` (`delivered`) | `HUMAN_REVIEW` | `human_review` (Weak similarity) | Similarity < 0.65 threshold gates novel issue to human specialist. |
| **4. Conflicting Precedents** | *"got salted butter instead of unsalted"* | `ORD-9929` (`delivered`) | `HUMAN_REVIEW` | Suggested: `redelivery` | Precedents conflict between refund and replacement; routes to human with safe recommendation. |

---

## Setup & Execution Instructions

### Prerequisites
- **Python**: 3.10+ (tested on Python 3.12)
- **Node.js**: 18+ (tested with Vite 4)
- **PowerShell** (Windows) or **Bash** (macOS/Linux)

---

### 1. Backend Setup

From the repository root:

```powershell
# Create and activate Python virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install backend dependencies
pip install -r backend/requirements.txt

# (Optional) Set your Gemini API key
# Copy .env.example to .env and add:
# GEMINI_API_KEY="your_api_key_here"

# Start FastAPI backend server
.\.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --reload --port 8000
```

Backend will be accessible at:
- REST API: `http://localhost:8000`
- Swagger UI: `http://localhost:8000/docs`

---

### 2. Frontend Setup

In a separate terminal:

```powershell
cd frontend

# Install Node dependencies
npm install

# Start Vite development server
npm run dev
```

Frontend dashboard will be accessible at:
- Web Dashboard: `http://localhost:5173`

---

### 3. Run Automated Tests

```powershell
# Run full 42-test backend suite
.\.venv\Scripts\python.exe -m pytest backend/tests -v

# Run production frontend build verification
cd frontend
npm run build
```

---

## Deployment Readiness

- **Network Binding**: FastAPI binds to `0.0.0.0` with configurable `HOST` and `PORT` environment variables.
- **CORS Configured**: Dynamic origin support for local development and cloud URLs via `ALLOWED_ORIGINS`.
- **Stateless & Portable**: Uses lightweight local storage without requiring external Docker, PostgreSQL, or Redis dependencies.
- **Production UI**: Frontend builds cleanly with Vite (`dist/` production assets).
