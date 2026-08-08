import React from 'react';
import { TicketCard } from './TicketCard';

const LANE_CONFIG = {
  auto_resolve: {
    subtitle: 'Safe to automate',
    icon: '✓',
  },
  human_review: {
    subtitle: 'Human decision required',
    icon: '⚠',
  },
};

export function TicketLane({ title, type, tickets, selectedTicket, onSelectTicket }) {
  const isAuto = type === 'auto_resolve';
  const config = LANE_CONFIG[type] || LANE_CONFIG.human_review;

  return (
    <div className="lane-column">
      <div className={`lane-header ${isAuto ? 'auto-resolve' : 'human-review'}`}>
        <div className="lane-header-text">
          <div className={`lane-title ${isAuto ? 'auto-resolve' : 'human-review'}`}>
            <span aria-hidden="true">{config.icon}</span>
            <span>{title}</span>
          </div>
          <div className="lane-subtitle">{config.subtitle}</div>
        </div>
        <span className={`count-badge ${isAuto ? 'auto-resolve' : 'human-review'}`}>
          {tickets.length} {tickets.length === 1 ? 'ticket' : 'tickets'}
        </span>
      </div>

      <div className="lane-content">
        {tickets.length === 0 ? (
          <div className="lane-empty">No tickets in this lane.</div>
        ) : (
          tickets.map((ticket) => (
            <TicketCard
              key={ticket.ticket_id}
              ticket={ticket}
              isSelected={selectedTicket?.ticket_id === ticket.ticket_id}
              onClick={() => onSelectTicket(ticket)}
            />
          ))
        )}
      </div>
    </div>
  );
}
