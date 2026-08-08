/**
 * Centralized API service — reads backend as sole source of truth.
 */

const API_BASE = (
  typeof import.meta !== 'undefined'
  && import.meta.env
  && import.meta.env.VITE_API_BASE_URL
)
  ? import.meta.env.VITE_API_BASE_URL.replace(/\/$/, '')
  : 'http://localhost:8000';

const API_PREFIX = `${API_BASE}/api`;

class ApiError extends Error {
  constructor(message, status = null) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
  }
}

async function request(path, options = {}) {
  const url = `${API_PREFIX}${path}`;
  let response;

  try {
    response = await fetch(url, {
      headers: { 'Content-Type': 'application/json', ...options.headers },
      ...options,
    });
  } catch {
    throw new ApiError(
      'Backend connection unavailable. Make sure FastAPI is running on localhost:8000.',
    );
  }

  if (!response.ok) {
    let detail = `Request failed (${response.status})`;
    try {
      const body = await response.json();
      detail = body.detail || body.message || detail;
    } catch {
      // ignore parse errors
    }
    throw new ApiError(detail, response.status);
  }

  return response.json();
}

/** Normalize list-item shape from GET /api/tickets */
function normalizeListItem(item = {}) {
  return {
    ticket_id: item.ticket_id || '',
    created_at: item.created_at || '',
    order_id: item.order_id || '',
    description: item.description || '',
    decision: (item.decision || 'HUMAN_REVIEW').toUpperCase(),
    confidence_score: Number(item.confidence_score ?? 0),
    selected_action: item.selected_action || 'human_review',
    suggested_action: item.suggested_action ?? null,
    delivery_status: item.delivery_status || 'unknown',
  };
}

/** Preserve backend detail envelope; flatten evaluation for convenience */
function normalizeDetail(data = {}) {
  const evaluation = data.evaluation || {};
  const order = data.order || {};
  const guardrails = evaluation.guardrails || {};

  return {
    ticket_id: data.ticket_id || '',
    created_at: data.created_at || '',
    description: data.description || '',
    order,
    precedents: Array.isArray(data.precedents) ? data.precedents : [],
    evaluation,
    simulated_action: data.simulated_action || null,
    draft_reply: data.draft_reply || null,
    // Flattened convenience fields for list-style access in detail view
    decision: (evaluation.decision || 'HUMAN_REVIEW').toUpperCase(),
    confidence_score: Number(evaluation.confidence_score ?? 0),
    selected_action: evaluation.selected_action || 'human_review',
    suggested_action: evaluation.suggested_action ?? null,
    reasoning: evaluation.reasoning || '',
    guardrails,
    similarity_score: Number(evaluation.similarity_score ?? 0),
    exact_action_agreement: evaluation.exact_action_agreement ?? null,
    action_family_agreement: evaluation.action_family_agreement ?? null,
  };
}

export async function healthCheck() {
  return request('/health');
}

export async function getTickets(lane = 'all') {
  const query = lane && lane !== 'all' ? `?lane=${lane}` : '';
  const data = await request(`/tickets${query}`);
  const items = Array.isArray(data) ? data : data.tickets || [];
  return items.map(normalizeListItem);
}

export async function getAutoResolveTickets() {
  return getTickets('auto_resolve');
}

export async function getHumanReviewTickets() {
  return getTickets('human_review');
}

export async function getTicket(ticketId) {
  const data = await request(`/tickets/${ticketId}`);
  return normalizeDetail(data);
}

export async function evaluateTicket(ticketId) {
  const data = await request(`/tickets/${ticketId}/evaluate`, { method: 'POST' });
  return normalizeDetail(data);
}

export async function resolveTicket(ticketId) {
  return request(`/tickets/${ticketId}/resolve`, { method: 'POST' });
}

export async function getDecisions() {
  const data = await request('/decisions');
  return Array.isArray(data) ? data : data.decisions || [];
}

export { ApiError, API_BASE };
