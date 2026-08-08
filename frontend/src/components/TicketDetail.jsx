import React from 'react';
import {
  ACTION_TYPES,
  DELIVERY_STATUS,
  GENERATION_SOURCE_LABELS,
} from '../utils/constants';
import {
  formatCurrency,
  formatPercent,
  formatDateTime,
  formatAction,
  formatDeliveryStatus,
} from '../utils/formatters';
import {
  analyzePrecedentAgreement,
  buildWhyDecisionItems,
  buildGuardrailChecks,
  isAutoResolve,
} from '../utils/ticketHelpers';

function getActionMeta(action) {
  const key = String(action || '').toLowerCase();
  return ACTION_TYPES[key] || {
    label: formatAction(action),
    className: 'action-apology',
  };
}

function StatusIcon({ type }) {
  const icons = { pass: '✓', warn: '⚠', fail: '✕', unknown: '·' };
  return <span className={`status-icon status-${type}`}>{icons[type] || '·'}</span>;
}

function DetailSkeleton() {
  return (
    <div className="detail-container">
      <div className="skeleton-block skeleton-header" />
      <div className="skeleton-block skeleton-section" />
      <div className="skeleton-block skeleton-section" />
      <div className="skeleton-block skeleton-section tall" />
    </div>
  );
}

export function TicketDetail({ ticket, loading, error, onRetry }) {
  if (loading) return <DetailSkeleton />;

  if (error) {
    return (
      <div className="detail-container">
        <div className="state-card error-state">
          <strong>Ticket detail unavailable.</strong>
          <p>{error}</p>
          {onRetry && (
            <button type="button" className="retry-button" onClick={onRetry}>
              Retry
            </button>
          )}
        </div>
      </div>
    );
  }

  if (!ticket) {
    return (
      <div className="detail-container">
        <div className="state-card empty-state">
          <strong>Select a ticket.</strong>
          <p>Choose a ticket from either lane to inspect the full decision record.</p>
        </div>
      </div>
    );
  }

  const isAuto = isAutoResolve(ticket);
  const order = ticket.order || {};
  const deliveryKey = String(order.delivery_status || '').toLowerCase();
  const deliveryMeta = DELIVERY_STATUS[deliveryKey] || {
    label: formatDeliveryStatus(order.delivery_status),
    className: 'status-pending',
  };
  const agreement = analyzePrecedentAgreement(ticket.precedents);
  const whyDecision = buildWhyDecisionItems(ticket);
  const guardrailChecks = buildGuardrailChecks(ticket.guardrails);
  const selectedMeta = getActionMeta(ticket.selected_action);
  const suggestedMeta = ticket.suggested_action
    ? getActionMeta(ticket.suggested_action)
    : null;
  const simulated = ticket.simulated_action;
  const draft = ticket.draft_reply;
  const generationLabel = draft?.generation_source
    ? GENERATION_SOURCE_LABELS[draft.generation_source] || draft.generation_source
    : null;

  return (
    <aside className="detail-container" aria-live="polite">
      {/* Header */}
      <div className="detail-header">
        <div>
          <div className={`badge ${isAuto ? 'badge-auto' : 'badge-human'}`}>
            {isAuto ? '✓ AUTO-RESOLVED' : '⚠ NEEDS HUMAN'}
          </div>
          <h2 className="detail-title">{ticket.ticket_id}</h2>
        </div>
        <div className="detail-meta">
          <div className="metric-pill">
            <span>Confidence</span>
            <strong>{formatPercent(ticket.confidence_score)}</strong>
          </div>
          <span className="order-chip">Order #{order.order_id || 'N/A'}</span>
        </div>
      </div>

      <div className="detail-body">
        {/* Customer Issue */}
        <section className="detail-section">
          <div className="section-title">Customer Issue</div>
          <p className="customer-issue">{ticket.description || '—'}</p>
          <p className="created-at">Created {formatDateTime(ticket.created_at)}</p>
        </section>

        {/* Order Context */}
        <section className="detail-section">
          <div className="section-title">Order Context</div>
          <div className="order-grid">
            <div className="order-item-stat">
              <div className="stat-label">Order ID</div>
              <div className="stat-val">{order.order_id || '—'}</div>
            </div>
            <div className="order-item-stat">
              <div className="stat-label">Items</div>
              <div className="stat-val">{order.items ?? '—'}</div>
            </div>
            <div className="order-item-stat">
              <div className="stat-label">Order Value</div>
              <div className="stat-val">{formatCurrency(order.value_inr)}</div>
            </div>
            <div className="order-item-stat">
              <div className="stat-label">Delivery Time</div>
              <div className="stat-val">{order.delivery_time_min ?? '—'} min</div>
            </div>
            <div className="order-item-stat span-2">
              <div className="stat-label">Delivery Status</div>
              <div className={`stat-val delivery-badge ${deliveryMeta.className}`}>
                {deliveryMeta.label}
              </div>
            </div>
          </div>
        </section>

        {/* Decision */}
        <section className="detail-section decision-section">
          <div className="section-title">Decision</div>
          {isAuto ? (
            <div className="decision-block auto">
              <div className="decision-headline">✓ AUTO-RESOLVED</div>
              <div className="decision-detail">
                <span>Action executed:</span>
                <span className={`action-pill ${selectedMeta.className}`}>{selectedMeta.label}</span>
              </div>
            </div>
          ) : (
            <div className="decision-block human">
              <div className="decision-headline">⚠ NEEDS HUMAN</div>
              <p className="decision-note">Human decision required — no action has been executed.</p>
              {suggestedMeta ? (
                <div className="suggestion-box">
                  <div className="suggestion-label">AI / System Suggestion</div>
                  <span className={`action-pill ${suggestedMeta.className}`}>{suggestedMeta.label}</span>
                  <p className="suggestion-note">Advisory only — human approval required before execution.</p>
                </div>
              ) : (
                <div className="suggestion-box muted">
                  <div className="suggestion-label">No Safe Suggestion</div>
                  <p className="suggestion-note">
                    {ticket.guardrails?.cancelled_redelivery_blocked
                      ? 'Historical precedents suggest redelivery, but the order is cancelled and redelivery is blocked.'
                      : agreement.type === 'conflict'
                        ? 'Historical precedents conflict — the system cannot recommend a single safe action.'
                        : 'No automated suggestion available for this ticket.'}
                  </p>
                </div>
              )}
            </div>
          )}
        </section>

        {/* Top 3 Precedents */}
        <section className="detail-section">
          <div className="section-title">Top 3 Historical Precedents</div>
          <div className="precedent-list">
            {(ticket.precedents || []).map((p) => {
              const actionMeta = getActionMeta(p.resolution_action);
              return (
                <div key={p.precedent_id} className="precedent-card">
                  <div className="precedent-top">
                    <strong>{p.precedent_id}</strong>
                    <span className="sim-score">{formatPercent(p.similarity_score)} similar</span>
                  </div>
                  <div className="precedent-text">{p.description}</div>
                  <div className="precedent-meta-line">
                    <span>Action:</span>
                    <span className={`action-pill ${actionMeta.className}`}>{actionMeta.label}</span>
                  </div>
                  {p.resolution_note && (
                    <div className="precedent-note">
                      <span>Note:</span>
                      <p>{p.resolution_note}</p>
                    </div>
                  )}
                  {p.csat != null && (
                    <div className="precedent-csat">CSAT: {p.csat}/5</div>
                  )}
                </div>
              );
            })}
          </div>
        </section>

        {/* Action Agreement */}
        <section className="detail-section">
          <div className="section-title">Action Agreement</div>
          <div className={`agreement-visual ${agreement.type}`}>
            {agreement.type === 'unanimous' && (
              <>
                <div className="agreement-headline pass">
                  {agreement.total}/{agreement.total} PRECEDENTS AGREE
                </div>
                <div className="agreement-action">
                  ✓ {formatAction(agreement.dominantAction).toUpperCase()}
                </div>
              </>
            )}
            {agreement.type === 'conflict' && (
              <>
                <div className="agreement-headline warn">ACTION CONFLICT</div>
                <div className="agreement-breakdown">
                  {agreement.breakdown.map((line) => (
                    <div key={line} className="agreement-line">{line}</div>
                  ))}
                </div>
              </>
            )}
            {ticket.guardrails?.cancelled_redelivery_blocked && agreement.type === 'unanimous' && (
              <div className="agreement-blocked">
                <div className="agreement-headline warn">
                  {agreement.total}/{agreement.total} historical precedents suggest {formatAction(agreement.dominantAction)}
                </div>
                <div className="agreement-headline fail">BUT: CANCELLED ORDER — REDELIVERY BLOCKED</div>
              </div>
            )}
          </div>
        </section>

        {/* Confidence / Evidence */}
        <section className="detail-section">
          <div className="section-title">Confidence / Evidence</div>
          <div className="evidence-grid">
            <div className="evidence-item">
              <span className="evidence-label">Similarity</span>
              <strong>{formatPercent(ticket.similarity_score)}</strong>
            </div>
            <div className="evidence-item">
              <span className="evidence-label">Exact Agreement</span>
              <strong>{ticket.exact_action_agreement === true ? 'Yes' : ticket.exact_action_agreement === false ? 'No' : '—'}</strong>
            </div>
            <div className="evidence-item">
              <span className="evidence-label">Family Agreement</span>
              <strong>{ticket.action_family_agreement === true ? 'Yes' : ticket.action_family_agreement === false ? 'No' : '—'}</strong>
            </div>
            <div className="evidence-item highlight">
              <span className="evidence-label">Final Confidence</span>
              <strong>{formatPercent(ticket.confidence_score)}</strong>
            </div>
          </div>
        </section>

        {/* Why This Decision */}
        <section className="detail-section why-section">
          <div className="section-title">{whyDecision.heading}</div>
          <ul className="why-list">
            {whyDecision.items.map((item, i) => (
              <li key={i} className={`why-item ${item.indent ? 'indent' : ''}`}>
                <StatusIcon type={item.type} />
                <span>{item.text}</span>
              </li>
            ))}
          </ul>
          <div className="why-conclusion">{whyDecision.conclusion}</div>
          {whyDecision.reasoning && (
            <p className="why-reasoning">{whyDecision.reasoning}</p>
          )}
        </section>

        {/* Guardrails */}
        <section className="detail-section">
          <div className="section-title">Safety Checks</div>
          <ul className="guardrail-list">
            {guardrailChecks.map((check) => (
              <li key={check.key} className={`guardrail-item ${check.status}`}>
                <StatusIcon type={check.status === 'passed' ? 'pass' : check.status === 'failed' ? 'fail' : 'unknown'} />
                <span>{check.label}</span>
              </li>
            ))}
          </ul>
        </section>

        {/* Simulated Action */}
        {simulated && (
          <section className="detail-section">
            <div className="section-title">{isAuto ? 'Simulated Action' : 'Action Status'}</div>
            <div className={`simulated-box ${simulated.status?.toLowerCase() || ''}`}>
              {isAuto ? (
                <>
                  <div className="simulated-action">
                    ✓ {formatAction(simulated.action).toUpperCase()}
                    {simulated.amount_inr != null && (
                      <span className="simulated-amount">{formatCurrency(simulated.amount_inr)}</span>
                    )}
                  </div>
                  <div className="simulated-status">{simulated.status || '—'}</div>
                  {simulated.note && <p className="simulated-note">{simulated.note}</p>}
                  {simulated.is_simulated && (
                    <span className="simulated-tag">Simulated — no real systems accessed</span>
                  )}
                </>
              ) : (
                <>
                  <div className="simulated-action queued">QUEUED FOR HUMAN REVIEW</div>
                  {simulated.note && <p className="simulated-note">{simulated.note}</p>}
                </>
              )}
            </div>
          </section>
        )}

        {/* Draft Reply */}
        {draft && (draft.subject || draft.body) && (
          <section className="detail-section">
            <div className="section-title">
              Draft Customer Reply
              {generationLabel && (
                <span className={`generation-badge ${draft.generation_source}`}>
                  {generationLabel}
                </span>
              )}
            </div>
            <div className="reply-card">
              {draft.subject && (
                <div className="reply-subject">
                  <span className="reply-label">Subject:</span>
                  {draft.subject}
                </div>
              )}
              {draft.body && (
                <div className="reply-body">
                  <span className="reply-label">Body:</span>
                  <p>{draft.body}</p>
                </div>
              )}
              <p className="reply-disclaimer">Draft only — not sent to customer.</p>
            </div>
            {draft.explanation && (
              <div className="reply-explanation">
                <div className="explanation-label">Why this reply?</div>
                <p>{draft.explanation}</p>
              </div>
            )}
          </section>
        )}
      </div>
    </aside>
  );
}
