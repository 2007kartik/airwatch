import React from 'react';
import { BarChart3, Info } from 'lucide-react';

export default function AnalyticsSummary({ summary }) {
  if (!summary) {
    return (
      <div className="bg-slate-900/80 rounded-2xl p-5 border border-slate-800 shadow-xl text-center text-slate-500 py-8">
        Loading analytics summary...
      </div>
    );
  }

  const metrics = [
    {
      name: 'Temperature',
      unit: '°C',
      data: summary.temperature,
      warn: 35.0,
      crit: 40.0,
    },
    {
      name: 'Relative Humidity',
      unit: '%',
      data: summary.humidity,
      warn: 80.0,
      crit: 90.0,
    },
    {
      name: 'Gas Sensor Level (Raw)',
      unit: '',
      data: summary.gas_raw,
      warn: 300.0,
      crit: 500.0,
    },
    {
      name: 'Simulated PM2.5',
      unit: 'µg/m³',
      data: summary.pm25,
      warn: 35.4,
      crit: 55.4,
    },
    {
      name: 'Simulated PM10',
      unit: 'µg/m³',
      data: summary.pm10,
      warn: 154.0,
      crit: 254.0,
    },
  ];

  return (
    <div className="bg-slate-900/80 rounded-2xl p-5 border border-slate-800 shadow-xl">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-slate-800 gap-2">
        <div className="flex items-center space-x-2.5">
          <div className="w-8 h-8 rounded-lg bg-teal-500/10 border border-teal-500/20 flex items-center justify-center text-teal-400">
            <BarChart3 className="w-4 h-4" />
          </div>
          <div>
            <h2 className="text-base font-bold text-white tracking-wide">24-Hour Analytics & Aggregates</h2>
            <p className="text-xs text-slate-400">SQL aggregations computed from PostgreSQL database</p>
          </div>
        </div>

        {/* Counter Pills */}
        <div className="flex items-center space-x-3 text-xs font-mono">
          <span className="px-2.5 py-1 rounded-lg bg-slate-950 border border-slate-800 text-slate-300">
            Readings: <strong className="text-cyan-400">{summary.total_readings}</strong>
          </span>
          <span className="px-2.5 py-1 rounded-lg bg-slate-950 border border-slate-800 text-slate-300">
            Alerts: <strong className="text-rose-400">{summary.total_alerts}</strong>
          </span>
        </div>
      </div>

      {/* Aggregate Metrics Table */}
      <div className="mt-4 overflow-x-auto">
        <table className="w-full text-left text-xs">
          <thead>
            <tr className="border-b border-slate-800 text-slate-400 uppercase tracking-wider text-[10px] font-semibold">
              <th className="py-2.5 px-3">Environmental Indicator</th>
              <th className="py-2.5 px-3">Current</th>
              <th className="py-2.5 px-3">24h Average</th>
              <th className="py-2.5 px-3">24h Min</th>
              <th className="py-2.5 px-3">24h Max</th>
              <th className="py-2.5 px-3 text-right">Threshold Bounds</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60 font-mono">
            {metrics.map((m, idx) => {
              const cur = m.data?.current;
              const isOverCrit = cur !== null && cur !== undefined && cur >= m.crit;
              const isOverWarn = cur !== null && cur !== undefined && cur >= m.warn;

              return (
                <tr key={idx} className="hover:bg-slate-800/30 transition-colors">
                  <td className="py-2.5 px-3 font-sans font-medium text-slate-200">
                    {m.name}
                  </td>
                  <td className="py-2.5 px-3 font-bold">
                    <span
                      className={
                        isOverCrit
                          ? 'text-rose-400'
                          : isOverWarn
                          ? 'text-amber-400'
                          : 'text-emerald-400'
                      }
                    >
                      {cur !== null && cur !== undefined ? cur.toFixed(1) : '--'} {m.unit}
                    </span>
                  </td>
                  <td className="py-2.5 px-3 text-slate-300">
                    {m.data?.avg !== null && m.data?.avg !== undefined ? m.data.avg.toFixed(1) : '--'}{' '}
                    {m.unit}
                  </td>
                  <td className="py-2.5 px-3 text-slate-400">
                    {m.data?.min !== null && m.data?.min !== undefined ? m.data.min.toFixed(1) : '--'}{' '}
                    {m.unit}
                  </td>
                  <td className="py-2.5 px-3 text-slate-400">
                    {m.data?.max !== null && m.data?.max !== undefined ? m.data.max.toFixed(1) : '--'}{' '}
                    {m.unit}
                  </td>
                  <td className="py-2.5 px-3 text-right text-slate-400 font-sans text-[11px]">
                    <span className="text-amber-400/90 font-mono font-medium">{m.warn}</span> /{' '}
                    <span className="text-rose-400/90 font-mono font-medium">{m.crit}</span> {m.unit}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Educational & Prototype Disclosure Box */}
      <div className="mt-4 p-3.5 rounded-xl bg-slate-950/60 border border-slate-800 flex items-start space-x-2.5 text-xs text-slate-400">
        <Info className="w-4 h-4 text-cyan-400 shrink-0 mt-0.5" />
        <div className="space-y-1">
          <p className="font-semibold text-slate-200">
            Prototype Simulation Disclosure & Technical Limitations
          </p>
          <p className="leading-relaxed">
            All environmental indicators in AirWatch are generated by a standalone Python simulator via continuous random drift and configurable threshold spikes. This prototype does not use physical sensors or official regulatory AQI calculations.
          </p>
        </div>
      </div>
    </div>
  );
}
