import React from 'react';
import { formatPercent, truncateText, formatAction } from '../utils/formatters';
import { ACTION_TYPES } from '../utils/constants';
import { getCardStatusHint, isAutoResolve } from '../utils/ticketHelpers';

function getActionMeta(action) {
  const key = String(action || 'human_review').toLowerCase();
  return ACTION_TYPES[key] || {
    label: formatAction(action),
    className: 'action-apology',
  };
}

export function TicketCard({ ticket, isSelected, onClick }) {
  const isAuto = isAutoResolve(ticket);
  const confidence = Number(ticket.confidence_score ?? 0);
  const statusHint = getCardStatusHint(ticket);

  const primaryAction = isAuto
    ? ticket.selected_action
    : ticket.suggested_action;

  const actionMeta = primaryAction
    ? getActionMeta(primaryAction)
    : null;

  const confidenceColor = confidence >= 0.9 ? '#059669' : confidence >= 0.7 ? '#D97706' : '#DC2626';

  return (
    <button
      type="button"
      className={`ticket-card ${isSelected ? 'selected' : ''}`}
      onClick={onClick}
    >
      <div className="card-top">
        <span className="ticket-id">{ticket.ticket_id}</span>
        <span className="order-id">Order #{ticket.order_id || 'N/A'}</span>
      </div>

      <div className="ticket-desc">{truncateText(ticket.description, 90)}</div>

      <div className="card-bottom">
        <span className={`badge ${isAuto ? 'badge-auto' : 'badge-human'}`}>
          {isAuto ? 'AUTO-RESOLVED' : 'NEEDS HUMAN'}
        </span>

        {actionMeta && (
          <span className={`action-pill ${actionMeta.className}`}>
            {!isAuto && <span className="suggested-prefix">Suggested: </span>}
            {actionMeta.label}
          </span>
        )}
      </div>

      <div className="card-meta">
        <span className="confidence-label" style={{ color: confidenceColor }}>
          {formatPercent(confidence)} confidence
        </span>
        <span className="card-hint">{statusHint}</span>
      </div>

      <div className="confidence-bar-outer">
        <div
          className="confidence-bar-inner"
          style={{
            width: `${Math.min(confidence * 100, 100)}%`,
            backgroundColor: confidenceColor,
          }}
        />
      </div>
    </button>
  );
}
