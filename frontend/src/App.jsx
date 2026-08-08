import React, { useEffect, useState, useCallback } from 'react';
import { DashboardLayout } from './layouts/DashboardLayout';
import { TicketLane } from './components/TicketLane';
import { TicketDetail } from './components/TicketDetail';
import { useTickets } from './hooks/useTickets';
import { getTicket } from './services/api';

function App() {
  const {
    autoResolvedTickets,
    humanReviewTickets,
    loading,
    error,
    searchQuery,
    setSearchQuery,
    selectedTicket,
    setSelectedTicket,
    stats,
    systemOnline,
    refreshTickets,
  } = useTickets();

  const [detailTicket, setDetailTicket] = useState(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [detailError, setDetailError] = useState('');

  const loadDetail = useCallback(async (ticketId) => {
    if (!ticketId) {
      setDetailTicket(null);
      return;
    }
    setDetailLoading(true);
    setDetailError('');
    try {
      const ticket = await getTicket(ticketId);
      setDetailTicket(ticket);
    } catch (err) {
      setDetailError(err.message || 'Unable to load ticket details.');
      setDetailTicket(null);
    } finally {
      setDetailLoading(false);
    }
  }, []);

  useEffect(() => {
    if (selectedTicket?.ticket_id) {
      loadDetail(selectedTicket.ticket_id);
    } else {
      setDetailTicket(null);
    }
  }, [selectedTicket, loadDetail]);

  return (
    <DashboardLayout stats={stats} systemOnline={systemOnline}>
      <div className="controls-bar">
        <label className="search-box" aria-label="Search tickets">
          <span className="search-icon" aria-hidden="true">⌕</span>
          <input
            className="search-input"
            type="search"
            placeholder="Search ticket, order, or issue…"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </label>
      </div>

      {loading ? (
        <div className="state-panel">
          <div className="loading-grid">
            <div className="skeleton-block skeleton-lane" />
            <div className="skeleton-block skeleton-lane" />
          </div>
        </div>
      ) : error ? (
        <div className="state-panel">
          <div className="state-card error-state">
            <strong>Unable to load tickets.</strong>
            <p>{error}</p>
            <p className="error-hint">
              Backend connection unavailable. Make sure FastAPI is running on localhost:8000.
            </p>
            <button type="button" className="retry-button" onClick={refreshTickets}>
              Retry
            </button>
          </div>
        </div>
      ) : (
        <>
          <section className="dashboard-grid" aria-label="Ticket board">
            <TicketLane
              title="AUTO-RESOLVED"
              type="auto_resolve"
              tickets={autoResolvedTickets}
              selectedTicket={selectedTicket}
              onSelectTicket={setSelectedTicket}
            />
            <TicketLane
              title="NEEDS HUMAN"
              type="human_review"
              tickets={humanReviewTickets}
              selectedTicket={selectedTicket}
              onSelectTicket={setSelectedTicket}
            />
          </section>

          <TicketDetail
            ticket={detailTicket}
            loading={detailLoading}
            error={detailError}
            onRetry={() => selectedTicket && loadDetail(selectedTicket.ticket_id)}
          />
        </>
      )}
    </DashboardLayout>
  );
}

export default App;
