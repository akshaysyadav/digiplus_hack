# Backend — Zepto Support Ticket Manager

* **Framework**: Python 3.10+ / FastAPI / Uvicorn
* **Similarity Engine**: scikit-learn TF-IDF + Cosine Similarity
* **Decision Engine**: Deterministic guardrail pipeline

---

## 1. Local Development

### Prerequisites
- Python 3.10+ (tested on Python 3.12)
- Virtual environment (recommended)

### Setup & Run
```bash
cd backend

# 1. Install dependencies
pip install -r requirements.txt

# 2. Start local FastAPI server (binds on 0.0.0.0:8000)
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Access Endpoints & Docs
- **Base URL**: `http://localhost:8000`
- **Interactive Swagger Docs**: `http://localhost:8000/docs`
- **Alternative ReDoc**: `http://localhost:8000/redoc`
- **Health Check**: `http://localhost:8000/api/health`

### Run Automated Tests
```bash
pytest -v
```

---

## 2. Production Cloud Deployment

The backend is fully configured for deployment on any cloud hosting platform (Render, Railway, Fly.io, AWS, Heroku, HuggingFace Spaces).

### Environment Variables
| Variable | Required | Default | Description |
| :--- | :--- | :--- | :--- |
| `PORT` | Optional | `8000` | Port provided automatically by cloud platforms (e.g. Render/Railway) |
| `HOST` | Optional | `0.0.0.0` | Host binding interface (defaults to `0.0.0.0` for container/cloud environments) |
| `ALLOWED_ORIGINS` | Optional | `*` | Comma-separated list of allowed frontend origins (e.g., `https://my-zepto-frontend.vercel.app,http://localhost:5173`) |

### Production Start Command
```bash
uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
```
*(Or if running directly with Python: `python -m app.main`)*

---

## 3. Core API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Service status check |
| `GET` | `/api/health` | System health check and dataset readiness |
| `GET` | `/api/tickets` | List all 30 incoming tickets with decision statuses |
| `GET` | `/api/tickets?lane=auto_resolve` | Filter tickets for the Auto-Resolved lane |
| `GET` | `/api/tickets?lane=human_review` | Filter tickets for the Needs-Human lane |
| `GET` | `/api/tickets/{ticket_id}` | Full ticket detail with order context, precedents, evaluation, and draft reply |
| `POST` | `/api/tickets/{ticket_id}/evaluate` | Run evaluation pipeline and record audit log |
| `POST` | `/api/tickets/{ticket_id}/resolve` | Execute simulated resolution action (guards against resolving `HUMAN_REVIEW` tickets) |
| `GET` | `/api/decisions` | Retrieve full decision audit history |

---

## 4. Key Demo Scenarios

1. **`N-005` (AUTO_RESOLVE)**:
   - Issue: `"milk packet missing from my order"`
   - Order: `ORD-9905` (Delivered)
   - Precedents: Unanimous 3/3 agreement on `redelivery`
   - Confidence: `1.00`
   - Result: `AUTO_RESOLVE` $\to$ Simulated `redelivery`

2. **`N-002` (CANCELLED ORDER SAFETY GUARDRAIL)**:
   - Issue: `"milk packet missing from my order"`
   - Order: `ORD-9902` (Cancelled)
   - Precedents: 3/3 agreement on `redelivery`
   - Guardrail: Cancelled order blocks redelivery
   - Result: `HUMAN_REVIEW` $\to$ Action `blocked_redelivery`

3. **`N-029` (CONFLICTING PRECEDENT ACTIONS)**:
   - Issue: `"got salted butter instead of unsalted"`
   - Order: `ORD-9929` (Delivered)
   - Precedents: Disagreement (`redelivery` vs `partial_refund`)
   - Guardrail: Precedent conflict (system does not guess)
   - Result: `HUMAN_REVIEW` $\to$ Queued for human agent
