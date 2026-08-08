import React from 'react';
import { Header } from './Header';

export function DashboardLayout({ stats, systemOnline, onOpenSimulate, children }) {
  return (
    <div className="app-container">
      <Header stats={stats} systemOnline={systemOnline} onOpenSimulate={onOpenSimulate} />
      <main className="app-main">{children}</main>
    </div>
  );
}

