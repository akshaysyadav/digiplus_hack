# Data Directory — Zepto Support Ticket Manager

The source-of-truth hackathon CSV datasets are stored in `data/sample_data/`:

## Datasets & Exact Schemas

1. **`resolved_tickets.csv`** (`RESOLV~1.CSV`) — 300 historical resolved tickets
   * **Location**: `data/sample_data/`
   * **Exact Schema**: `ticket_id`, `category`, `description`, `resolution_action`, `resolution_note`, `time_to_resolve_min`, `csat`
   * **Usage**: Text/vector similarity search, category mapping, historical precedent resolution lookup.

2. **`new_tickets.csv`** (`NEW_TI~1.CSV`) — 30 incoming customer tickets
   * **Location**: `data/sample_data/`
   * **Exact Schema**: `ticket_id`, `created_at`, `order_id`, `description`
   * **Usage**: Evaluation queue ingested by the backend engine.

3. **`orders_context.csv`** (`ORDERS~1.CSV`) — 30 order records
   * **Location**: `data/sample_data/`
   * **Exact Schema**: `order_id`, `items`, `value_inr`, `delivery_time_min`, `delivery_status`
   * **Usage**: Order context validation (guardrails: `delivery_status == 'cancelled'`, refund cap vs `value_inr`).

---

## Data Handling Rules

* **Do NOT move, rename, or modify files**: Keep source files inside `data/sample_data/` intact.
* **Do NOT create duplicate or fake data**: Ground truth CSV files must be preserved as provided.
* **Backend Ingestion**: `backend/app/services/data_service.py` reads data directly from `data/sample_data/`.

