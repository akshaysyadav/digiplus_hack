/**
 * Ticket board state — loads lanes from backend, no mock fallback.
 */

import { useState, useEffect, useMemo, useCallback } from 'react';
import {
  getAutoResolveTickets,
  getHumanReviewTickets,
} from '../services/api';

export function useTickets() {
  const [autoResolvedTickets, setAutoResolvedTickets] = useState([]);
  const [humanReviewTickets, setHumanReviewTickets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedTicket, setSelectedTicket] = useState(null);
  const [systemOnline, setSystemOnline] = useState(false);

  const loadTickets = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const [auto, human] = await Promise.all([
        getAutoResolveTickets(),
        getHumanReviewTickets(),
      ]);

      setSystemOnline(true);
      setAutoResolvedTickets(auto);
      setHumanReviewTickets(human);

      const all = [...auto, ...human];
      setSelectedTicket((prev) => {
        if (prev && all.some((t) => t.ticket_id === prev.ticket_id)) return prev;
        return all[0] || null;
      });
    } catch (err) {
      setSystemOnline(false);
      setError(err.message || 'Failed to load tickets from backend.');
      setAutoResolvedTickets([]);
      setHumanReviewTickets([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadTickets();
  }, [loadTickets]);

  const filterTickets = useCallback(
    (list) => {
      if (!searchQuery.trim()) return list;
      const q = searchQuery.toLowerCase();
      return list.filter((ticket) => {
        const haystack = `${ticket.ticket_id} ${ticket.order_id} ${ticket.description}`.toLowerCase();
        return haystack.includes(q);
      });
    },
    [searchQuery],
  );

  const filteredAuto = useMemo(
    () => filterTickets(autoResolvedTickets),
    [autoResolvedTickets, filterTickets],
  );

  const filteredHuman = useMemo(
    () => filterTickets(humanReviewTickets),
    [humanReviewTickets, filterTickets],
  );

  const stats = useMemo(() => {
    const total = autoResolvedTickets.length + humanReviewTickets.length;
    const autoCount = autoResolvedTickets.length;
    const humanCount = humanReviewTickets.length;
    const autoRate = total > 0 ? Math.round((autoCount / total) * 100) : 0;
    return { total, autoCount, humanCount, autoRate };
  }, [autoResolvedTickets, humanReviewTickets]);

  return {
    autoResolvedTickets: filteredAuto,
    humanReviewTickets: filteredHuman,
    loading,
    error,
    searchQuery,
    setSearchQuery,
    selectedTicket,
    setSelectedTicket,
    stats,
    systemOnline,
    refreshTickets: loadTickets,
  };
}
