# Backend — Zepto Support Ticket Manager

* **Owner**: Developer 1 (Backend)
* **Framework**: Python 3.10+ / FastAPI

---

## Directory Architecture

```
backend/
├── README.md
├── requirements.txt
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI application entrypoint
│   ├── api/                       # API routes & endpoint definitions
│   │   ├── __init__.py
│   │   └── routes/
│   │       └── __init__.py
│   ├── core/                      # Application config & constants
│   │   ├── __init__.py
│   │   └── config.py
│   ├── models/                    # Pydantic schemas & data models
│   │   ├── __init__.py
│   │   └── schemas.py
│   ├── services/                  # Modular domain services
│   │   ├── __init__.py
│   │   ├── data_service.py        # Loads raw CSV files from data/
│   │   ├── similarity_service.py  # TF-IDF + Cosine Similarity search
│   │   ├── decision_service.py    # Auto-resolve vs Human-review logic
│   │   ├── order_context_service.py # Validates order context & rules
│   │   ├── action_service.py      # Action simulation (refund, redelivery, etc.)
│   │   └── reply_service.py       # Customer draft reply & explanation generator
│   └── utils/                     # Shared helpers & formatting utilities
│       ├── __init__.py
│       └── helpers.py
└── tests/                         # Pytest automated test suite
    └── __init__.py
```

---

## Service Responsibilities

* **`data_service.py`**: Responsible for loading and caching `resolved_tickets.csv`, `new_tickets.csv`, and `orders_context.csv` directly from `data/sample_data/`.

* **`similarity_service.py`**: Computes TF-IDF vectors for resolved tickets and finds top-3 precedent matches for incoming tickets.
* **`order_context_service.py`**: Cross-references tickets with `orders_context.csv` and checks order rules (cancelled order check, max refund cap).
* **`decision_service.py`**: Evaluates similarity threshold, precedent action agreement, and order rules to return `AUTO_RESOLVE` or `HUMAN_REVIEW`.
* **`action_service.py`**: Simulates specific resolution actions (`full_refund`, `partial_refund`, `redelivery`, `coupon`, `escalation`, `apology_no_action`).
* **`reply_service.py`**: Generates customer-facing draft responses and structured audit explanations ("Why this action?").

---

## Setup & Running Locally

1. Create and activate a Python virtual environment:
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # macOS/Linux:
   source venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run FastAPI development server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

4. Run tests:
   ```bash
   pytest
   ```
