import React from 'react';
import { Header } from './Header';

export function DashboardLayout({ stats, systemOnline, children }) {
  return (
    <div className="app-container">
      <Header stats={stats} systemOnline={systemOnline} />
      <main className="app-main">{children}</main>
    </div>
  );
}
