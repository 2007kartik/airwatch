/**
 * AirWatch — API Client
 * Centralized Axios client for interacting with the FastAPI backend.
 * Reads base URL from VITE_API_BASE_URL with fallback to http://127.0.0.1:8000.
 */

import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 5000,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Fetch health status of the API and PostgreSQL database
 */
export async function fetchHealth(signal) {
  const response = await apiClient.get('/api/health', { signal });
  return response.data;
}

/**
 * Fetch the single most recent sensor reading
 */
export async function fetchLatestReading(signal) {
  const response = await apiClient.get('/api/readings/latest', { signal });
  return response.data;
}

/**
 * Fetch historical readings with pagination
 */
export async function fetchReadings(limit = 10, offset = 0, signal) {
  const response = await apiClient.get('/api/readings', {
    params: { limit, offset },
    signal,
  });
  return response.data;
}

/**
 * Fetch triggered alerts with optional status/severity filters
 */
export async function fetchAlerts(status = null, severity = null, limit = 50, signal) {
  const params = { limit };
  if (status && status !== 'all') params.status = status;
  if (severity && severity !== 'all') params.severity = severity;

  const response = await apiClient.get('/api/alerts', { params, signal });
  return response.data;
}

/**
 * Acknowledge an active alert
 */
export async function acknowledgeAlert(alertId) {
  const response = await apiClient.patch(`/api/alerts/${alertId}`);
  return response.data;
}

/**
 * Fetch analytics summary statistics (avg, min, max, current)
 */
export async function fetchAnalyticsSummary(range = '24h', signal) {
  const response = await apiClient.get('/api/analytics/summary', {
    params: { range },
    signal,
  });
  return response.data;
}

/**
 * Fetch time-series trend points for charts
 */
export async function fetchAnalyticsTrends(range = '1h', limit = 150, signal) {
  const response = await apiClient.get('/api/analytics/trends', {
    params: { range, limit },
    signal,
  });
  return response.data;
}
