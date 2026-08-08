/**
 * UI helpers derived from backend ticket data — display only, no decision logic.
 */

import { formatAction } from './formatters';

export function isAutoResolve(ticket) {
  return ticket?.decision === 'AUTO_RESOLVE';
}

export function analyzePrecedentAgreement(precedents = []) {
  if (!precedents.length) {
    return { type: 'none', counts: {}, total: 0, breakdown: [], dominantAction: null };
  }

  const counts = {};
  precedents.forEach((p) => {
    const action = p.resolution_action || p.action || 'unknown';
    counts[action] = (counts[action] || 0) + 1;
  });

  const total = precedents.length;
  const entries = Object.entries(counts);
  const dominant = entries.sort((a, b) => b[1] - a[1])[0];

  if (entries.length === 1) {
    return {
      type: 'unanimous',
      counts,
      total,
      dominantAction: dominant[0],
      breakdown: [`${total}/${total} precedents agree`],
    };
  }

  return {
    type: 'conflict',
    counts,
    total,
    dominantAction: dominant?.[0] || null,
    breakdown: entries.map(([action, count]) => `${count} × ${formatAction(action)}`),
  };
}

export function getCardStatusHint(ticket) {
  if (!ticket) return '';

  if (isAutoResolve(ticket)) {
    const agreement = ticket.exact_action_agreement;
    if (agreement === true) return '3/3 precedents agree';
    if (ticket.delivery_status === 'delivered') return 'Delivered';
    return formatAction(ticket.selected_action);
  }

  if (ticket.suggested_action) {
    return `Suggested: ${formatAction(ticket.suggested_action)}`;
  }

  if (ticket.delivery_status === 'cancelled') {
    return '⚠ Cancelled order — review required';
  }

  return 'Human approval required';
}

export function buildWhyDecisionItems(ticket) {
  if (!ticket) return { heading: '', items: [], conclusion: '' };

  const isAuto = isAutoResolve(ticket);
  const agreement = analyzePrecedentAgreement(ticket.precedents);
  const guardrails = ticket.guardrails || ticket.evaluation?.guardrails || {};
  const similarity = ticket.similarity_score ?? ticket.evaluation?.similarity_score ?? 0;
  const deliveryStatus = ticket.order?.delivery_status || ticket.delivery_status || '';
  const items = [];

  if (similarity >= 0.75) {
    items.push({ type: 'pass', text: `Strong historical match — ${Math.round(similarity * 100)}%` });
  } else if (similarity > 0) {
    items.push({ type: 'warn', text: `Moderate historical match — ${Math.round(similarity * 100)}%` });
  }

  if (agreement.type === 'unanimous') {
    items.push({
      type: 'pass',
      text: `${agreement.total}/${agreement.total} precedents suggest ${formatAction(agreement.dominantAction)}`,
    });
  } else if (agreement.type === 'conflict') {
    items.push({ type: 'warn', text: 'Historical actions conflict' });
    agreement.breakdown.forEach((line) => {
      items.push({ type: 'warn', text: line, indent: true });
    });
  }

  if (deliveryStatus === 'delivered') {
    items.push({ type: 'pass', text: 'Order is delivered' });
  } else if (deliveryStatus === 'cancelled') {
    items.push({ type: 'warn', text: 'Order is cancelled' });
  }

  if (guardrails.cancelled_redelivery_blocked) {
    items.push({ type: 'fail', text: 'Redelivery is blocked on cancelled orders' });
  }

  if (guardrails.refund_cap_enforced) {
    items.push({ type: 'warn', text: 'Refund cap enforced — exceeds safe limit' });
  }

  if (guardrails.escalation_precedent_detected) {
    items.push({ type: 'warn', text: 'Escalation precedent detected' });
  }

  if (guardrails.similarity_threshold_passed === false) {
    items.push({ type: 'fail', text: 'Similarity threshold not met' });
  }

  const allGuardrailsPassed = Object.values(guardrails).every(Boolean);
  if (isAuto && allGuardrailsPassed && agreement.type === 'unanimous') {
    items.push({ type: 'pass', text: 'No guardrail triggered' });
  }

  let conclusion = '';
  if (isAuto) {
    conclusion = `AUTO-RESOLVE → ${formatAction(ticket.selected_action).toUpperCase()}`;
  } else if (ticket.suggested_action) {
    conclusion = `HUMAN REVIEW — AI suggests ${formatAction(ticket.suggested_action).toUpperCase()}, not executed`;
  } else if (guardrails.cancelled_redelivery_blocked) {
    conclusion = 'HUMAN REVIEW REQUIRED — redelivery blocked';
  } else if (agreement.type === 'conflict') {
    conclusion = 'SYSTEM DOES NOT GUESS — human review required';
  } else {
    conclusion = 'HUMAN REVIEW REQUIRED';
  }

  return {
    heading: isAuto ? 'WHY AUTO-RESOLVED?' : 'WHY HUMAN REVIEW?',
    items,
    conclusion,
    reasoning: ticket.reasoning || ticket.evaluation?.reasoning || '',
  };
}

export function buildGuardrailChecks(guardrails = {}) {
  const labels = {
    similarity_threshold_passed: 'Similarity threshold passed',
    cancelled_redelivery_blocked: 'Cancelled-order redelivery check',
    refund_cap_enforced: 'Refund cap check',
    escalation_precedent_detected: 'Escalation precedent check',
  };

  return Object.entries(labels).map(([key, label]) => {
    const value = guardrails[key];
    let status = 'unknown';
    if (value === true) {
      // For "blocked" flags, true means the guardrail TRIGGERED (failed safety)
      status = key === 'cancelled_redelivery_blocked'
        || key === 'refund_cap_enforced'
        || key === 'escalation_precedent_detected'
        ? 'failed'
        : 'passed';
    } else if (value === false) {
      status = key === 'cancelled_redelivery_blocked'
        || key === 'refund_cap_enforced'
        || key === 'escalation_precedent_detected'
        ? 'passed'
        : 'failed';
    }
    return { key, label, status, raw: value };
  });
}
