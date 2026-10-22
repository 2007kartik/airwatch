import React from 'react';
import { AlertTriangle, AlertOctagon, CheckCircle2 } from 'lucide-react';

export default function MetricCard({
  title,
  subtitle,
  value,
  unit,
  warningThreshold,
  criticalThreshold,
  icon: Icon,
  colorScheme = 'cyan',
  summaryStats = null,
  disclaimer = null,
}) {
  const isAvailable = value !== undefined && value !== null;
  const numValue = isAvailable ? parseFloat(value) : 0;

  // Determine threshold status
  let statusLabel = 'Normal';
  let statusColor = 'text-emerald-400 bg-emerald-950/40 border-emerald-800';
  let StatusIcon = CheckCircle2;

  if (isAvailable) {
    if (criticalThreshold !== undefined && numValue >= criticalThreshold) {
      statusLabel = 'Critical';
      statusColor = 'text-rose-400 bg-rose-950/60 border-rose-800 animate-pulse';
      StatusIcon = AlertOctagon;
    } else if (warningThreshold !== undefined && numValue >= warningThreshold) {
      statusLabel = 'Warning';
      statusColor = 'text-amber-400 bg-amber-950/60 border-amber-800';
      StatusIcon = AlertTriangle;
    }
  }

  // Pre-configured accent gradients
  const colorStyles = {
    cyan: {
      border: 'border-slate-800 hover:border-cyan-500/40',
      iconBg: 'bg-cyan-500/10 text-cyan-400 border-cyan-500/20',
      glow: 'shadow-cyan-900/10',
    },
    teal: {
      border: 'border-slate-800 hover:border-teal-500/40',
      iconBg: 'bg-teal-500/10 text-teal-400 border-teal-500/20',
      glow: 'shadow-teal-900/10',
    },
    amber: {
      border: 'border-slate-800 hover:border-amber-500/40',
      iconBg: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
      glow: 'shadow-amber-900/10',
    },
    violet: {
      border: 'border-slate-800 hover:border-violet-500/40',
      iconBg: 'bg-violet-500/10 text-violet-400 border-violet-500/20',
      glow: 'shadow-violet-900/10',
    },
    indigo: {
      border: 'border-slate-800 hover:border-indigo-500/40',
      iconBg: 'bg-indigo-500/10 text-indigo-400 border-indigo-500/20',
      glow: 'shadow-indigo-900/10',
    },
  }[colorScheme] || {
    border: 'border-slate-800 hover:border-cyan-500/40',
    iconBg: 'bg-cyan-500/10 text-cyan-400 border-cyan-500/20',
    glow: 'shadow-cyan-900/10',
  };

  return (
    <div
      className={`relative bg-slate-900/80 rounded-2xl p-5 border ${colorStyles.border} shadow-lg ${colorStyles.glow} transition-all duration-300 hover:-translate-y-0.5`}
    >
      {/* Top Row: Icon, Title & Status */}
      <div className="flex items-start justify-between">
        <div className="flex items-center space-x-3">
          <div className={`w-10 h-10 rounded-xl flex items-center justify-center border ${colorStyles.iconBg}`}>
            <Icon className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-slate-200 tracking-wide">{title}</h3>
            {subtitle && <p className="text-[11px] text-slate-400">{subtitle}</p>}
          </div>
        </div>

        {/* Status Badge */}
        <span
          className={`inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-[11px] font-semibold border ${statusColor}`}
        >
          <StatusIcon className="w-3 h-3" />
          <span>{statusLabel}</span>
        </span>
      </div>

      {/* Main Metric Value */}
      <div className="mt-4 flex items-baseline space-x-2">
        <span className="text-3xl sm:text-4xl font-extrabold tracking-tight text-white font-mono">
          {isAvailable ? numValue.toFixed(1) : '--'}
        </span>
        <span className="text-sm font-medium text-slate-400">{unit}</span>
      </div>

      {/* Threshold Information Footnote */}
      <div className="mt-2 flex items-center justify-between text-[11px] text-slate-400 border-t border-slate-800/80 pt-2">
        <span>
          Warn: <strong className="text-slate-300">{warningThreshold !== undefined ? warningThreshold : 'N/A'}{unit}</strong>
        </span>
        <span>
          Crit: <strong className="text-slate-300">{criticalThreshold !== undefined ? criticalThreshold : 'N/A'}{unit}</strong>
        </span>
      </div>

      {/* 24h Summary Aggregates */}
      {summaryStats && (
        <div className="mt-2.5 pt-2 border-t border-slate-800/60 grid grid-cols-3 gap-1 text-[11px] text-center bg-slate-950/40 rounded-lg py-1.5 px-2">
          <div>
            <p className="text-slate-500 text-[10px] uppercase font-semibold">24h Avg</p>
            <p className="font-mono font-medium text-slate-300">
              {summaryStats.avg !== null && summaryStats.avg !== undefined ? summaryStats.avg.toFixed(1) : '--'}
            </p>
          </div>
          <div>
            <p className="text-slate-500 text-[10px] uppercase font-semibold">24h Min</p>
            <p className="font-mono font-medium text-slate-300">
              {summaryStats.min !== null && summaryStats.min !== undefined ? summaryStats.min.toFixed(1) : '--'}
            </p>
          </div>
          <div>
            <p className="text-slate-500 text-[10px] uppercase font-semibold">24h Max</p>
            <p className="font-mono font-medium text-slate-300">
              {summaryStats.max !== null && summaryStats.max !== undefined ? summaryStats.max.toFixed(1) : '--'}
            </p>
          </div>
        </div>
      )}

      {/* Optional Disclaimer badge */}
      {disclaimer && (
        <p className="mt-2 text-[10px] text-slate-500 italic">
          * {disclaimer}
        </p>
      )}
    </div>
  );
}
