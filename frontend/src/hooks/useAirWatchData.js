/**
 * AirWatch — Custom Data Polling Hook
 * Manages 5-second interval polling, handles network errors gracefully,
 * preserves stale data during transient outages, and cleans up on unmount.
 */

import { useState, useEffect, useRef, useCallback } from 'react';
import {
  fetchHealth,
  fetchLatestReading,
  fetchReadings,
  fetchAlerts,
  acknowledgeAlert,
  fetchAnalyticsSummary,
  fetchAnalyticsTrends,
} from '../api/client';

export function useAirWatchData(pollInterval = 5000) {
  const [health, setHealth] = useState(null);
  const [latestReading, setLatestReading] = useState(null);
  const [readingsList, setReadingsList] = useState([]);
  const [alerts, setAlerts] = useState({ items: [], total: 0, active_count: 0, acknowledged_count: 0 });
  const [analyticsSummary, setAnalyticsSummary] = useState(null);
  const [trends, setTrends] = useState({ points: [], time_range: '1h', count: 0 });
  const [activeRange, setActiveRange] = useState('1h');

  const [isInitialLoading, setIsInitialLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [isStale, setIsStale] = useState(false);
  const [lastUpdated, setLastUpdated] = useState(null);
  const [error, setError] = useState(null);

  // Guards against overlapping requests
  const isFetchingRef = useRef(false);
  const abortControllerRef = useRef(null);

  const loadData = useCallback(async (isManual = false) => {
    if (isFetchingRef.current) return;
    isFetchingRef.current = true;

    if (isManual) setIsRefreshing(true);

    // Abort previous in-flight requests if any
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    abortControllerRef.current = new AbortController();
    const signal = abortControllerRef.current.signal;

    try {
      // Execute all fetches in parallel
      const [
        healthData,
        latestData,
        readingsData,
        alertsData,
        summaryData,
        trendsData,
      ] = await Promise.all([
        fetchHealth(signal).catch((err) => {
          console.warn('Health check failed:', err.message);
          return null;
        }),
        fetchLatestReading(signal).catch((err) => {
          if (err.response?.status !== 404) console.warn('Latest reading failed:', err.message);
          return null;
        }),
        fetchReadings(12, 0, signal).catch((err) => {
          console.warn('Readings list failed:', err.message);
          return { items: [], total: 0 };
        }),
        fetchAlerts(null, null, 50, signal).catch((err) => {
          console.warn('Alerts failed:', err.message);
          return { items: [], total: 0, active_count: 0, acknowledged_count: 0 };
        }),
        fetchAnalyticsSummary('24h', signal).catch((err) => {
          console.warn('Analytics summary failed:', err.message);
          return null;
        }),
        fetchAnalyticsTrends(activeRange, 150, signal).catch((err) => {
          console.warn('Trends failed:', err.message);
          return { points: [], time_range: activeRange, count: 0 };
        }),
      ]);

      // If health succeeded or we got valid data, update state
      if (healthData || latestData || readingsData.items.length > 0) {
        if (healthData) setHealth(healthData);
        if (latestData) setLatestReading(latestData);
        if (readingsData?.items) setReadingsList(readingsData.items);
        if (alertsData) setAlerts(alertsData);
        if (summaryData) setAnalyticsSummary(summaryData);
        if (trendsData) setTrends(trendsData);

        setIsStale(false);
        setError(null);
        setLastUpdated(new Date());
      } else {
        // Backend seems completely unreachable
        setIsStale(true);
        setError('Backend service is currently unreachable.');
      }
    } catch (err) {
      if (err.name !== 'CanceledError' && err.name !== 'AbortError') {
        console.error('Error during AirWatch poll:', err);
        setIsStale(true);
        setError(err.message || 'Failed to fetch sensor data.');
      }
    } finally {
      isFetchingRef.current = false;
      setIsInitialLoading(false);
      setIsRefreshing(false);
    }
  }, [activeRange]);

  // Initial load and timer loop
  useEffect(() => {
    loadData();

    const intervalId = setInterval(() => {
      loadData();
    }, pollInterval);

    return () => {
      clearInterval(intervalId);
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, [loadData, pollInterval]);

  // Handle alert acknowledgement with optimistic UI update
  const handleAcknowledgeAlert = async (alertId) => {
    try {
      await acknowledgeAlert(alertId);
      // Optimistically update status in local state
      setAlerts((prev) => {
        const updatedItems = prev.items.map((item) =>
          item.id === alertId
            ? { ...item, status: 'acknowledged', acknowledged_at: new Date().toISOString() }
            : item
        );
        const newActiveCount = Math.max(0, prev.active_count - 1);
        return {
          ...prev,
          items: updatedItems,
          active_count: newActiveCount,
          acknowledged_count: prev.acknowledged_count + 1,
        };
      });
      return true;
    } catch (err) {
      console.error('Failed to acknowledge alert:', err);
      return false;
    }
  };

  return {
    health,
    latestReading,
    readingsList,
    alerts,
    analyticsSummary,
    trends,
    activeRange,
    setActiveRange,
    isInitialLoading,
    isRefreshing,
    isStale,
    lastUpdated,
    error,
    handleAcknowledgeAlert,
    refreshNow: () => loadData(true),
  };
}
