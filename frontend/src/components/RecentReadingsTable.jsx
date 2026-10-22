import React from 'react';
import { Table, CheckCircle2, AlertTriangle, AlertOctagon } from 'lucide-react';

export default function RecentReadingsTable({ readings }) {
  const items = readings || [];

  const formatTimestamp = (isoStr) => {
    if (!isoStr) return '--';
    try {
      const d = new Date(isoStr);
      return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    } catch {
      return isoStr;
    }
  };

  const getStatusBadge = (r) => {
    const isCrit =
      r.temperature_c >= 40.0 ||
      r.humidity_percent >= 90.0 ||
      (r.gas_raw_value && r.gas_raw_value >= 500.0) ||
      (r.pm25_ug_m3 && r.pm25_ug_m3 >= 55.4) ||
      (r.pm10_ug_m3 && r.pm10_ug_m3 >= 254.0);

    const isWarn =
      r.temperature_c >= 35.0 ||
      r.humidity_percent >= 80.0 ||
      (r.gas_raw_value && r.gas_raw_value >= 300.0) ||
      (r.pm25_ug_m3 && r.pm25_ug_m3 >= 35.4) ||
      (r.pm10_ug_m3 && r.pm10_ug_m3 >= 154.0);

    if (isCrit) {
      return (
        <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded text-[10px] font-bold bg-rose-500/20 text-rose-300 border border-rose-500/30">
          <AlertOctagon className="w-2.5 h-2.5" />
          <span>Critical</span>
        </span>
      );
    }
    if (isWarn) {
      return (
        <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded text-[10px] font-bold bg-amber-500/20 text-amber-300 border border-amber-500/30">
          <AlertTriangle className="w-2.5 h-2.5" />
          <span>Warning</span>
        </span>
      );
    }
    return (
      <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded text-[10px] font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
        <CheckCircle2 className="w-2.5 h-2.5" />
        <span>Normal</span>
      </span>
    );
  };

  return (
    <div className="bg-slate-900/80 rounded-2xl p-5 border border-slate-800 shadow-xl">
      {/* Header */}
      <div className="flex items-center justify-between pb-4 border-b border-slate-800">
        <div className="flex items-center space-x-2.5">
          <div className="w-8 h-8 rounded-lg bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400">
            <Table className="w-4 h-4" />
          </div>
          <div>
            <h2 className="text-base font-bold text-white tracking-wide">Recent Ingested Readings</h2>
            <p className="text-xs text-slate-400">Latest sensor packets persisted to PostgreSQL</p>
          </div>
        </div>

        <span className="text-xs text-slate-400 font-mono">
          Showing last <strong className="text-cyan-400">{items.length}</strong> records
        </span>
      </div>

      {/* Table Content */}
      <div className="mt-4 overflow-x-auto">
        <table className="w-full text-left text-xs">
          <thead>
            <tr className="border-b border-slate-800 text-slate-400 uppercase tracking-wider text-[10px] font-semibold">
              <th className="py-2.5 px-3">#ID</th>
              <th className="py-2.5 px-3">Time</th>
              <th className="py-2.5 px-3">Temp (°C)</th>
              <th className="py-2.5 px-3">Humidity (%)</th>
              <th className="py-2.5 px-3">Gas Raw</th>
              <th className="py-2.5 px-3">PM2.5 (µg/m³)</th>
              <th className="py-2.5 px-3">PM10 (µg/m³)</th>
              <th className="py-2.5 px-3">Source</th>
              <th className="py-2.5 px-3 text-right">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60 font-mono">
            {items.length === 0 ? (
              <tr>
                <td colSpan={9} className="py-8 text-center text-slate-500 font-sans">
                  No readings recorded yet. Make sure the Python simulator is running.
                </td>
              </tr>
            ) : (
              items.map((r) => (
                <tr key={r.id} className="hover:bg-slate-800/40 transition-colors">
                  <td className="py-2.5 px-3 text-slate-400 font-bold">#{r.id}</td>
                  <td className="py-2.5 px-3 text-slate-300 font-medium">{formatTimestamp(r.timestamp)}</td>
                  <td className="py-2.5 px-3 text-white font-semibold">
                    {r.temperature_c !== undefined ? r.temperature_c.toFixed(1) : '--'}
                  </td>
                  <td className="py-2.5 px-3 text-white font-semibold">
                    {r.humidity_percent !== undefined ? r.humidity_percent.toFixed(1) : '--'}
                  </td>
                  <td className="py-2.5 px-3 text-slate-300">
                    {r.gas_raw_value !== undefined && r.gas_raw_value !== null ? r.gas_raw_value.toFixed(1) : '--'}
                  </td>
                  <td className="py-2.5 px-3 text-cyan-300">
                    {r.pm25_ug_m3 !== undefined && r.pm25_ug_m3 !== null ? r.pm25_ug_m3.toFixed(1) : '--'}
                  </td>
                  <td className="py-2.5 px-3 text-violet-300">
                    {r.pm10_ug_m3 !== undefined && r.pm10_ug_m3 !== null ? r.pm10_ug_m3.toFixed(1) : '--'}
                  </td>
                  <td className="py-2.5 px-3 font-sans">
                    <span className="text-[10px] px-2 py-0.5 rounded bg-slate-800 text-slate-300 font-medium">
                      {r.source}
                    </span>
                  </td>
                  <td className="py-2.5 px-3 text-right font-sans">{getStatusBadge(r)}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
