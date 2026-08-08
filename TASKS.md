# Zepto Support Ticket Manager — Task Tracker

> **Project Status**: Backend Implementation & Testing Completed  
> Backend REST API ready and verified against all 30 test tickets and unit test suites.

---

## 1. Backend (`backend/`)

- [x] Inspect CSV datasets (`resolved_tickets.csv`, `new_tickets.csv`, `orders_context.csv`) and define Pydantic models.
- [x] Implement `data_service.py` to load and parse CSV datasets safely.
- [x] Implement `similarity_service.py` using TF-IDF + cosine similarity to search top-3 past precedents.
- [x] Implement `order_context_service.py` to fetch order details and validate order status / amounts.
- [x] Implement `decision_service.py` to evaluate confidence threshold, precedent action agreement, and business rules.
- [x] Implement `action_service.py` to simulate resolution actions (refund, redelivery, coupon, etc.).
- [x] Implement `reply_service.py` to draft customer response and generate decision explanations.
- [x] Create FastAPI routes in `app/api/routes/` for:
  - [x] `GET /api/tickets` (list incoming tickets with lane filter)
  - [x] `GET /api/tickets/{ticket_id}` (ticket details & context)
  - [x] `POST /api/tickets/{ticket_id}/evaluate` (run similarity, business rules, decision, and draft reply)
  - [x] `POST /api/tickets/{ticket_id}/resolve` (execute / approve simulated action)
  - [x] `GET /api/decisions` (retrieve logged decisions)
- [x] Implement decision logging to persist decisions and explanations.

---

## 2. Frontend (`frontend/`)

- [ ] Initialize React application setup (Vite + React) with modern dashboard styling.
- [ ] Create API service wrapper in `src/services/api.js` matching `API_CONTRACT.md`.
- [ ] Build Main Layout & Navigation (`src/layouts/`).
- [ ] Build Two-Lane Dashboard (`src/pages/Dashboard.jsx`):
  - [ ] Auto-Resolved Lane (tickets passing decision engine)
  - [ ] Needs-Human Lane (tickets flagged for manual review)
- [ ] Build Ticket Detail View (`src/components/TicketDetail.jsx`):
  - [ ] Ticket summary & customer problem statement
  - [ ] Order context panel (order status, items, value)
  - [ ] Top-3 Precedents cards with similarity scores
  - [ ] Confidence badge & decision indicator
  - [ ] Simulated Action display
  - [ ] Drafted customer reply preview
  - [ ] "Why this action?" explanation panel
- [ ] Add filter / search controls for ticket lanes.

---

## 3. Integration (`Integration`)

- [x] Finalize request/response schemas between Frontend and Backend in `API_CONTRACT.md`.
- [ ] Connect Frontend services to FastAPI endpoints.
- [ ] Verify end-to-end flow from receiving a ticket to rendering decision lanes.
- [ ] Verify error handling and fallback display when API is offline or returning errors.

---

## 4. Testing (`Testing`)

- [x] Write unit tests for `similarity_service.py` top-3 precedent matching.
- [x] Write unit tests for `decision_service.py` business rules:
  - [x] Test weak similarity -> Human Review
  - [x] Test precedent action disagreement -> Human Review
  - [x] Test cancelled order -> No Redelivery
  - [x] Test refund capped by order value
- [x] Run backend automated tests via `pytest` (13 passed).
- [ ] Perform manual frontend walkthrough for demo scenarios.

---

## 5. Deployment (`Deployment`)

- [ ] Prepare production build configurations (`Dockerfile` or web host deployment specs).
- [ ] Deploy backend API to public cloud host (e.g. Render / Railway / HuggingFace Spaces).
- [ ] Deploy frontend application to public host (e.g. Vercel / Netlify).
- [ ] Verify public deployment URLs and document in `README.md`.
- [ ] Push clean code to public GitHub repository.
