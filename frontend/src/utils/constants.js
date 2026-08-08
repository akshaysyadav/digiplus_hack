/**
 * UI constants and label mapping
 */

export const DECISION_TYPES = {
  AUTO_RESOLVE: {
    label: 'AUTO-RESOLVED',
    shortLabel: 'AUTO-RESOLVED',
    badgeClass: 'badge-auto',
    lane: 'auto_resolve',
  },
  HUMAN_REVIEW: {
    label: 'NEEDS HUMAN',
    shortLabel: 'NEEDS HUMAN',
    badgeClass: 'badge-human',
    lane: 'human_review',
  },
};

export const ACTION_TYPES = {
  full_refund: { label: 'Full Refund', className: 'action-refund' },
  partial_refund: { label: 'Partial Refund', className: 'action-refund' },
  refund_reissue: { label: 'Refund Reissue', className: 'action-refund' },
  redelivery: { label: 'Redelivery', className: 'action-redelivery' },
  coupon: { label: 'Coupon Issued', className: 'action-coupon' },
  escalation: { label: 'Escalated', className: 'action-apology' },
  apology_no_action: { label: 'Apology Sent', className: 'action-apology' },
  human_review: { label: 'Human Review', className: 'action-apology' },
  blocked_redelivery: { label: 'Redelivery Blocked', className: 'action-blocked' },
  queued_for_review: { label: 'Queued for Review', className: 'action-apology' },
};

export const DELIVERY_STATUS = {
  delivered: { label: 'Delivered', className: 'status-delivered' },
  cancelled: { label: 'Cancelled', className: 'status-cancelled' },
  pending: { label: 'Pending', className: 'status-pending' },
};

export const GENERATION_SOURCE_LABELS = {
  gemini: 'AI Generated Draft',
  fallback: 'System Fallback Draft',
};
