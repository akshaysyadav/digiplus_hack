# Frontend — Zepto Support Ticket Manager

* **Owner**: Developer 2 (Frontend)
* **Tech Stack**: React 18+ / Vite / Vanilla CSS (Modern aesthetic system)

---

## Directory Architecture

```
frontend/
├── README.md
├── package.json
├── public/
│   └── README.md
└── src/
    ├── components/         # Reusable UI elements (cards, badges, modals, detail panels)
    │   └── README.md
    ├── pages/              # Primary views (Dashboard, Two-Lane View, Ticket Details)
    │   └── README.md
    ├── layouts/            # Page shell, header, sidebar, dashboard frame
    │   └── README.md
    ├── services/           # Backend API integration client (Axios / Fetch wrappers)
    │   └── README.md
    ├── hooks/              # Custom React hooks (useTickets, useEvaluation)
    │   └── README.md
    ├── types/              # Type definitions & prop interfaces
    │   └── README.md
    ├── utils/              # Formatting utilities (confidence badges, currency format)
    │   └── README.md
    ├── data/               # Mock frontend state & sample UI constants
    │   └── README.md
    ├── App.jsx             # Top-level Application Shell & Routing
    └── main.jsx            # Application Entrypoint
```

---

## Planned Dashboard Features

The dashboard will present a modern **Two-Lane Interface**:

1. **Auto-Resolved Lane**:
   * Displays tickets automatically processed by the decision engine.
   * Shows precedent confidence match %, simulated action badge (e.g. `Full Refund`), and drafted response summary.

2. **Needs-Human Lane**:
   * Displays tickets flagged for human review due to low similarity, precedent action disagreement, or guardrail violation.
   * Highlights the specific reason for review escalation (e.g. `Precedent Disagreement`).

3. **Ticket Detail Drawer / View**:
   * **Ticket Summary**: Customer issue text and metadata.
   * **Order Context Panel**: Order status, item list, monetary values.
   * **Top 3 Precedents Cards**: Similarity scores, historical actions, precedent resolution text.
   * **Decision Indicator & Confidence Gauge**: Visual confidence score and decision tag.
   * **Simulated Action View**: Summary of action taken.
   * **Drafted Customer Reply**: Editable customer response draft.
   * **"Why this action?" Panel**: Clear audit log explaining the decision logic.

---

## Local Setup & Development

1. Install dependencies:
   ```bash
   cd frontend
   npm install
   ```

2. Start local development server:
   ```bash
   npm run dev
   ```

3. Build production bundle:
   ```bash
   npm run build
   ```
