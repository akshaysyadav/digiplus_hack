/**
 * Formatting utilities for dashboard UI
 */

export function formatCurrency(amount) {
  if (amount === undefined || amount === null) return '₹0';
  return `₹${Number(amount).toLocaleString('en-IN')}`;
}

export function formatPercent(score) {
  if (score === undefined || score === null) return '0%';
  const val = score <= 1 ? Math.round(score * 100) : Math.round(score);
  return `${val}%`;
}

export function formatDateTime(isoString) {
  if (!isoString) return '—';
  try {
    const date = new Date(isoString);
    return date.toLocaleString([], {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  } catch {
    return isoString;
  }
}

export function truncateText(text, maxLength = 65) {
  if (!text) return '';
  if (text.length <= maxLength) return text;
  return `${text.substring(0, maxLength)}…`;
}

export function formatAction(action) {
  if (!action) return '—';
  return String(action)
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

export function formatDeliveryStatus(status) {
  if (!status) return 'Unknown';
  return String(status).replace(/_/g, ' ').toUpperCase();
}
