import React from 'react';

export function Header({ stats, systemOnline }) {
  return (
    <header className="app-header">
      <div className="header-inner">
        <div className="brand-badge">
          <div className="brand-logo">Z</div>
          <div>
            <h1 className="brand-title">Zepto Support AI</h1>
            <div className="brand-subtitle">AI-powered ticket triage &amp; resolution</div>
          </div>
        </div>

        <div className="header-right">
          <div className={`system-status ${systemOnline ? 'online' : 'offline'}`}>
            <span className="status-dot" />
            {systemOnline ? 'System Online' : 'System Offline'}
          </div>

          <div className="header-stats">
            <div className="stat-pill">
              <span className="stat-label">Tickets</span>
              <span className="stat-value">{stats.total}</span>
            </div>

            <div className="stat-pill auto">
              <span className="stat-label">Auto-Resolved</span>
              <span className="stat-value">{stats.autoCount}</span>
            </div>

            <div className="stat-pill human">
              <span className="stat-label">Needs Human</span>
              <span className="stat-value">{stats.humanCount}</span>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}
