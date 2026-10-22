import React, { useState } from 'react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import { TrendingUp, Layers, ThermometerSun } from 'lucide-react';

// Custom Dark Tooltip defined outside component to avoid recreation during render
function CustomTooltip({ active, payload, label }) {
  if (!active || !payload || !payload.length) return null;

  let formattedTime = label;
  try {
    formattedTime = new Date(label).toLocaleString();
  } catch {}

  return (
    <div className="bg-slate-900/95 border border-slate-700/80 rounded-xl p-3 shadow-2xl backdrop-blur-md text-xs">
      <p className="font-semibold text-slate-300 mb-2 border-b border-slate-800 pb-1 font-mono">
        {formattedTime}
      </p>
      <div className="space-y-1">
        {payload.map((entry, index) => (
          <div key={`tooltip-${index}`} className="flex items-center justify-between space-x-4">
            <span className="flex items-center space-x-1.5" style={{ color: entry.color }}>
              <span className="w-2 h-2 rounded-full" style={{ backgroundColor: entry.color }}></span>
              <span className="font-medium text-slate-300">{entry.name}:</span>
            </span>
            <span className="font-mono font-bold text-white">
              {entry.value !== null && entry.value !== undefined ? entry.value.toFixed(1) : '--'}{' '}
              {entry.unit || ''}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

export default function TrendCharts({ trends, activeRange, onRangeChange }) {
  const [activeTab, setActiveTab] = useState('pollutants'); // 'pollutants' | 'climate'

  const ranges = [
    { id: '1h', label: 'Last 1 Hour' },
    { id: '6h', label: 'Last 6 Hours' },
    { id: '24h', label: 'Last 24 Hours' },
    { id: '7d', label: 'Last 7 Days' },
  ];

  // Format timestamps nicely depending on range
  const formatXAxis = (isoStr) => {
    if (!isoStr) return '';
    try {
      const d = new Date(isoStr);
      if (activeRange === '1h' || activeRange === '6h') {
        return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
      }
      return `${d.getMonth() + 1}/${d.getDate()} ${d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`;
    } catch {
      return isoStr;
    }
  };

  const points = trends?.points || [];

  return (
    <div className="bg-slate-900/80 rounded-2xl p-5 border border-slate-800 shadow-xl">
      {/* Header with Title, Tabs, and Range Selectors */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-slate-800">
        
        {/* Title & Tabs */}
        <div className="flex flex-wrap items-center gap-3">
          <div className="flex items-center space-x-2">
            <TrendingUp className="w-5 h-5 text-cyan-400" />
            <h2 className="text-base font-bold text-white tracking-wide">Historical Trends</h2>
          </div>

          <div className="flex items-center bg-slate-950 p-1 rounded-xl border border-slate-800 text-xs font-medium">
            <button
              onClick={() => setActiveTab('pollutants')}
              className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg transition-all ${
                activeTab === 'pollutants'
                  ? 'bg-cyan-600 text-white shadow-sm'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <Layers className="w-3.5 h-3.5" />
              <span>Simulated Pollutants (PM & Gas)</span>
            </button>
            <button
              onClick={() => setActiveTab('climate')}
              className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg transition-all ${
                activeTab === 'climate'
                  ? 'bg-cyan-600 text-white shadow-sm'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <ThermometerSun className="w-3.5 h-3.5" />
              <span>Climate (Temp & Humidity)</span>
            </button>
          </div>
        </div>

        {/* Time Range Pills */}
        <div className="flex items-center bg-slate-950 p-1 rounded-xl border border-slate-800 text-xs font-semibold self-start md:self-auto">
          {ranges.map((r) => (
            <button
              key={r.id}
              onClick={() => onRangeChange(r.id)}
              className={`px-2.5 py-1 rounded-lg transition-all ${
                activeRange === r.id
                  ? 'bg-slate-800 text-cyan-400 shadow-sm border border-slate-700'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              {r.id.toUpperCase()}
            </button>
          ))}
        </div>

      </div>

      {/* Chart Area */}
      <div className="mt-4 h-72 sm:h-80 w-full">
        {points.length === 0 ? (
          <div className="h-full flex items-center justify-center text-slate-500 text-sm">
            Waiting for trend points from simulator...
          </div>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            {activeTab === 'pollutants' ? (
              <AreaChart data={points} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorPm25" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#06b6d4" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="colorPm10" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="colorGas" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#f59e0b" stopOpacity={0.2} />
                    <stop offset="95%" stopColor="#f59e0b" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis
                  dataKey="timestamp"
                  tickFormatter={formatXAxis}
                  stroke="#64748b"
                  tick={{ fill: '#64748b', fontSize: 11 }}
                  tickLine={false}
                />
                <YAxis
                  stroke="#64748b"
                  tick={{ fill: '#64748b', fontSize: 11 }}
                  tickLine={false}
                />
                <Tooltip content={<CustomTooltip />} />
                <Legend
                  wrapperStyle={{ paddingTop: '10px', fontSize: '12px' }}
                  formatter={(value) => <span className="text-slate-300 font-medium">{value}</span>}
                />
                <Area
                  type="monotone"
                  dataKey="pm25_ug_m3"
                  name="Simulated PM2.5"
                  unit="µg/m³"
                  stroke="#06b6d4"
                  strokeWidth={2}
                  fillOpacity={1}
                  fill="url(#colorPm25)"
                />
                <Area
                  type="monotone"
                  dataKey="pm10_ug_m3"
                  name="Simulated PM10"
                  unit="µg/m³"
                  stroke="#8b5cf6"
                  strokeWidth={2}
                  fillOpacity={1}
                  fill="url(#colorPm10)"
                />
                <Area
                  type="monotone"
                  dataKey="gas_raw_value"
                  name="Raw Gas Indicator"
                  unit=""
                  stroke="#f59e0b"
                  strokeWidth={1.5}
                  strokeDasharray="4 4"
                  fillOpacity={1}
                  fill="url(#colorGas)"
                />
              </AreaChart>
            ) : (
              <AreaChart data={points} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorTemp" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#f43f5e" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#f43f5e" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="colorHum" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#14b8a6" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#14b8a6" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis
                  dataKey="timestamp"
                  tickFormatter={formatXAxis}
                  stroke="#64748b"
                  tick={{ fill: '#64748b', fontSize: 11 }}
                  tickLine={false}
                />
                <YAxis
                  stroke="#64748b"
                  tick={{ fill: '#64748b', fontSize: 11 }}
                  tickLine={false}
                />
                <Tooltip content={<CustomTooltip />} />
                <Legend
                  wrapperStyle={{ paddingTop: '10px', fontSize: '12px' }}
                  formatter={(value) => <span className="text-slate-300 font-medium">{value}</span>}
                />
                <Area
                  type="monotone"
                  dataKey="temperature_c"
                  name="Temperature"
                  unit="°C"
                  stroke="#f43f5e"
                  strokeWidth={2}
                  fillOpacity={1}
                  fill="url(#colorTemp)"
                />
                <Area
                  type="monotone"
                  dataKey="humidity_percent"
                  name="Relative Humidity"
                  unit="%"
                  stroke="#14b8a6"
                  strokeWidth={2}
                  fillOpacity={1}
                  fill="url(#colorHum)"
                />
              </AreaChart>
            )}
          </ResponsiveContainer>
        )}
      </div>

      {/* Footnote */}
      <div className="mt-2 text-right">
        <span className="text-[11px] text-slate-500 font-mono">
          Showing {points.length} readings recorded in PostgreSQL • Source: SIMULATED
        </span>
      </div>
    </div>
  );
}
