import React from 'react';
import {
  Thermometer,
  Droplets,
  Wind,
  CloudFog,
  Layers,
  Activity,
  Loader2,
} from 'lucide-react';

import { useAirWatchData } from './hooks/useAirWatchData';
import Navbar from './components/Navbar';
import StaleBanner from './components/StaleBanner';
import MetricCard from './components/MetricCard';
import TrendCharts from './components/TrendCharts';
import AlertsPanel from './components/AlertsPanel';
import AnalyticsSummary from './components/AnalyticsSummary';
import RecentReadingsTable from './components/RecentReadingsTable';
import Footer from './components/Footer';

export default function App() {
  const {
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
    refreshNow,
  } = useAirWatchData(5000); // 5-second polling

  if (isInitialLoading) {
    return (
      <div className="min-h-screen bg-slate-950 flex flex-col items-center justify-center space-y-4 text-slate-300">
        <div className="relative">
          <div className="w-16 h-16 rounded-2xl bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-400">
            <Activity className="w-8 h-8 animate-pulse" />
          </div>
          <Loader2 className="w-6 h-6 animate-spin text-cyan-400 absolute -top-1 -right-1" />
        </div>
        <div className="text-center">
          <h1 className="text-lg font-bold text-white tracking-wide">Connecting to AirWatch...</h1>
          <p className="text-xs text-slate-500 mt-1">Connecting to FastAPI backend & PostgreSQL 18</p>
        </div>
      </div>
    );
  }

  const tempSummary = analyticsSummary?.temperature;
  const humSummary = analyticsSummary?.humidity;
  const gasSummary = analyticsSummary?.gas_raw;
  const pm25Summary = analyticsSummary?.pm25;
  const pm10Summary = analyticsSummary?.pm10;

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans selection:bg-cyan-500 selection:text-white">
      {/* Top Navbar */}
      <Navbar
        health={health}
        isStale={isStale}
        lastUpdated={lastUpdated}
        isRefreshing={isRefreshing}
        onRefresh={refreshNow}
      />

      {/* Stale Data / Connection Lost Warning Banner */}
      <StaleBanner
        isStale={isStale}
        error={error}
        lastUpdated={lastUpdated}
        onRetry={refreshNow}
      />

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
        
        {/* Section 1: KPI Metric Cards Grid */}
        <section aria-label="Current Environmental Metrics">
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-xs uppercase font-bold tracking-wider text-slate-400">
              Live Environmental Indicators (Updated ~5s)
            </h2>
            {latestReading && (
              <span className="text-[11px] font-mono text-slate-500">
                Latest Packet ID #{latestReading.id} •{' '}
                {new Date(latestReading.timestamp).toLocaleTimeString()}
              </span>
            )}
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
            
            {/* 1. Temperature */}
            <MetricCard
              title="Temperature"
              subtitle="Ambient Thermal Sensor"
              value={latestReading?.temperature_c}
              unit="°C"
              warningThreshold={35.0}
              criticalThreshold={40.0}
              icon={Thermometer}
              colorScheme="cyan"
              summaryStats={tempSummary}
            />

            {/* 2. Relative Humidity */}
            <MetricCard
              title="Humidity"
              subtitle="Relative Air Moisture"
              value={latestReading?.humidity_percent}
              unit="%"
              warningThreshold={80.0}
              criticalThreshold={90.0}
              icon={Droplets}
              colorScheme="teal"
              summaryStats={humSummary}
            />

            {/* 3. Gas Sensor Level */}
            <MetricCard
              title="Gas Level"
              subtitle="Raw MQ Sensor Indicator"
              value={latestReading?.gas_raw_value}
              unit=""
              warningThreshold={300.0}
              criticalThreshold={500.0}
              icon={Wind}
              colorScheme="amber"
              summaryStats={gasSummary}
              disclaimer="Raw MQ indicator"
            />

            {/* 4. Simulated PM2.5 */}
            <MetricCard
              title="Simulated PM2.5"
              subtitle="Fine Particulate Indicator"
              value={latestReading?.pm25_ug_m3}
              unit="µg/m³"
              warningThreshold={35.4}
              criticalThreshold={55.4}
              icon={CloudFog}
              colorScheme="violet"
              summaryStats={pm25Summary}
              disclaimer="Simulated, not official AQI"
            />

            {/* 5. Simulated PM10 */}
            <MetricCard
              title="Simulated PM10"
              subtitle="Coarse Particulate Indicator"
              value={latestReading?.pm10_ug_m3}
              unit="µg/m³"
              warningThreshold={154.0}
              criticalThreshold={254.0}
              icon={Layers}
              colorScheme="indigo"
              summaryStats={pm10Summary}
              disclaimer="Simulated, not official AQI"
            />

          </div>
        </section>

        {/* Section 2: Trends Charts (2 cols) & Alerts Panel (1 col) */}
        <section aria-label="Trends and Alerts" className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <TrendCharts
              trends={trends}
              activeRange={activeRange}
              onRangeChange={setActiveRange}
            />
          </div>
          <div className="lg:col-span-1">
            <AlertsPanel
              alerts={alerts}
              onAcknowledgeAlert={handleAcknowledgeAlert}
            />
          </div>
        </section>

        {/* Section 3: Analytics Aggregates Summary */}
        <section aria-label="Statistical Aggregates">
          <AnalyticsSummary summary={analyticsSummary} />
        </section>

        {/* Section 4: Recent Sensor Readings Table */}
        <section aria-label="Recent Sensor Readings">
          <RecentReadingsTable readings={readingsList} />
        </section>

      </main>

      {/* Footer */}
      <Footer />
    </div>
  );
}
