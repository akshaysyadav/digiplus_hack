import React, { useState, useEffect } from 'react';
import { getOrders, simulateTicket } from '../services/api';

const QUICK_PRESETS = [
  {
    label: '🥛 Milk Missing (Delivered)',
    description: 'milk packet missing from my order',
    orderId: 'ORD-9905',
  },
  {
    label: '🚫 Milk Missing (Cancelled)',
    description: 'milk packet missing from my order',
    orderId: 'ORD-9902',
  },
  {
    label: '🧈 Wrong Butter (Conflict)',
    description: 'got salted butter instead of unsalted',
    orderId: 'ORD-9929',
  },
  {
    label: '⚠️ Novel Issue (Weak Sim)',
    description: 'the delivery person was rude and shouted at me',
    orderId: 'ORD-9908',
  },
];

export function SimulateTicketModal({ isOpen, onClose, onTicketCreated }) {
  const [description, setDescription] = useState('');
  const [orderId, setOrderId] = useState('');
  const [orders, setOrders] = useState([]);
  const [loadingOrders, setLoadingOrders] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!isOpen) {
      setError('');
      return;
    }

    async function fetchOrders() {
      setLoadingOrders(true);
      try {
        const data = await getOrders();
        setOrders(data);
        if (data.length > 0 && !orderId) {
          setOrderId(data[0].order_id);
        }
      } catch (err) {
        console.error('Failed to load orders:', err);
      } finally {
        setLoadingOrders(false);
      }
    }

    fetchOrders();
  }, [isOpen]);

  if (!isOpen) return null;

  const handleApplyPreset = (preset) => {
    if (submitting) return;
    setDescription(preset.description);
    setOrderId(preset.orderId);
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (submitting) return;

    if (!description.trim()) {
      setError('Please enter a customer issue description.');
      return;
    }
    if (!orderId) {
      setError('Please select an order ID.');
      return;
    }

    setSubmitting(true);
    setError('');

    try {
      const createdTicket = await simulateTicket({
        description: description.trim(),
        order_id: orderId,
      });

      // Reset form state ONLY after successful API response
      setDescription('');
      setError('');

      if (onTicketCreated) {
        onTicketCreated(createdTicket);
      }
      onClose();
    } catch (err) {
      // Preserve description on error so user can retry without retyping
      setError(err.message || 'Failed to simulate and evaluate ticket.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="modal-backdrop" onClick={!submitting ? onClose : undefined} role="dialog" aria-modal="true">
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div className="modal-title-group">
            <span className="modal-badge">Real-Time Simulation</span>
            <h2 className="modal-title">Simulate New Customer Ticket</h2>
          </div>
          <button
            type="button"
            className="modal-close-btn"
            onClick={onClose}
            disabled={submitting}
            aria-label="Close modal"
          >
            ✕
          </button>
        </div>

        <div className="preset-chips-container">
          <span className="preset-label">Quick Demo Scenarios:</span>
          <div className="preset-chips">
            {QUICK_PRESETS.map((p, idx) => (
              <button
                key={idx}
                type="button"
                className="preset-chip"
                onClick={() => handleApplyPreset(p)}
                disabled={submitting}
                title={`Order: ${p.orderId}`}
              >
                {p.label}
              </button>
            ))}
          </div>
        </div>

        <form onSubmit={handleSubmit} className="simulate-form">
          {error && (
            <div className="form-error-banner">
              <strong>Error:</strong> {error}
            </div>
          )}

          <div className="form-group">
            <label htmlFor="sim-description" className="form-label">
              Customer Issue / Description <span className="required-star">*</span>
            </label>
            <textarea
              id="sim-description"
              className="form-textarea"
              rows={3}
              placeholder="e.g. milk packet missing from my order, wrong brand delivered, payment charged twice..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              disabled={submitting}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="sim-order-id" className="form-label">
              Select Verified Order ID <span className="required-star">*</span>
            </label>
            {loadingOrders ? (
              <div className="form-loading-hint">Loading verified orders dataset…</div>
            ) : (
              <select
                id="sim-order-id"
                className="form-select"
                value={orderId}
                onChange={(e) => setOrderId(e.target.value)}
                disabled={submitting}
                required
              >
                {orders.map((o) => (
                  <option key={o.order_id} value={o.order_id}>
                    {o.order_id} — ₹{o.value_inr} ({o.items} items, {o.delivery_status})
                  </option>
                ))}
              </select>
            )}
            <span className="form-help-text">
              Order status &amp; values are loaded live from <code>orders_context.csv</code> to enforce guardrails.
            </span>
          </div>

          <div className="modal-actions">
            <button
              type="button"
              className="btn-secondary"
              onClick={onClose}
              disabled={submitting}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="btn-primary"
              disabled={submitting || loadingOrders}
            >
              {submitting ? 'Evaluating Pipeline…' : '⚡ Evaluate Ticket'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
