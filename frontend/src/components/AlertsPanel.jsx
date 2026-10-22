import React, { useState } from 'react';
import {
  Bell,
  AlertTriangle,
  AlertOctagon,
  CheckCircle,
  Clock,
  ShieldAlert,
  Loader2,
} from 'lucide-react';

export default function AlertsPanel({ alerts, onAcknowledgeAlert }) {
  const [filter, setFilter] = useState('all'); // 'all' | 'active' | 'acknowledged'
  const [acknowledgingId, setAcknowledgingId] = useState(null);

  const items = alerts?.items || [];
  const activeCount = alerts?.active_count || 0;
  const acknowledgedCount = alerts?.acknowledged_count || 0;

  const filteredItems = items.filter((a) => {
    if (filter === 'active') return a.status === 'active';
    if (filter === 'acknowledged') return a.status === 'acknowledged';
    return true;
  });

  const handleAcknowledge = async (id) => {
    setAcknowledgingId(id);
    await onAcknowledgeAlert(id);
    setAcknowledgingId(null);
  };

  const formatTimestamp = (isoStr) => {
    if (!isoStr) return '--';
    try {
      const d = new Date(isoStr);
      return `${d.toLocaleDateString()} ${d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}`;
    } catch {
      return isoStr;
    }
  };

  return (
    <div className="bg-slate-900/80 rounded-2xl p-5 border border-slate-800 shadow-xl flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center justify-between pb-4 border-b border-slate-800">
        <div className="flex items-center space-x-2.5">
          <div className="w-8 h-8 rounded-lg bg-rose-500/10 border border-rose-500/20 flex items-center justify-center text-rose-400">
            <Bell className="w-4 h-4" />
          </div>
          <div>
            <h2 className="text-base font-bold text-white tracking-wide">Threshold Alerts</h2>
            <p className="text-xs text-slate-400">Rule-based environmental threshold violations</p>
          </div>
        </div>

        {/* Active Badge */}
        <div className="flex items-center space-x-2">
          {activeCount > 0 ? (
            <span className="inline-flex items-center space-x-1.5 px-2.5 py-1 rounded-full text-xs font-bold bg-rose-950/80 text-rose-300 border border-rose-800 shadow-sm animate-pulse">
              <span className="w-2 h-2 rounded-full bg-rose-500"></span>
              <span>{activeCount} Active</span>
            </span>
          ) : (
            <span className="inline-flex items-center space-x-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-emerald-950/60 text-emerald-400 border border-emerald-800">
              <CheckCircle className="w-3.5 h-3.5" />
              <span>0 Active</span>
            </span>
          )}
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="flex items-center space-x-1.5 py-3 border-b border-slate-800 text-xs font-semibold">
        <button
          onClick={() => setFilter('all')}
          className={`px-3 py-1 rounded-lg transition-all ${
            filter === 'all'
              ? 'bg-slate-800 text-cyan-400 border border-slate-700'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          All ({items.length})
        </button>
        <button
          onClick={() => setFilter('active')}
          className={`px-3 py-1 rounded-lg transition-all ${
            filter === 'active'
              ? 'bg-rose-950/80 text-rose-300 border border-rose-800'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          Active ({activeCount})
        </button>
        <button
          onClick={() => setFilter('acknowledged')}
          className={`px-3 py-1 rounded-lg transition-all ${
            filter === 'acknowledged'
              ? 'bg-slate-800 text-emerald-400 border border-slate-700'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          Acknowledged ({acknowledgedCount})
        </button>
      </div>

      {/* Alert List */}
      <div className="mt-3 flex-1 overflow-y-auto space-y-2.5 max-h-[380px] pr-1">
        {filteredItems.length === 0 ? (
          <div className="py-12 text-center text-slate-500 text-xs flex flex-col items-center justify-center space-y-2">
            <ShieldAlert className="w-8 h-8 text-slate-600" />
            <p className="font-medium text-slate-400">No alerts match the selected filter.</p>
            <p className="text-[11px] text-slate-500">
              When the Python simulator triggers a threshold spike, alerts will appear here.
            </p>
          </div>
        ) : (
          filteredItems.map((alert) => {
            const isCrit = alert.severity === 'critical';
            const isActive = alert.status === 'active';

            return (
              <div
                key={alert.id}
                className={`p-3.5 rounded-xl border transition-all text-xs ${
                  isActive
                    ? isCrit
                      ? 'bg-rose-950/30 border-rose-800/80 hover:border-rose-700'
                      : 'bg-amber-950/30 border-amber-800/80 hover:border-amber-700'
                    : 'bg-slate-950/40 border-slate-800/60 opacity-75'
                }`}
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="flex items-start space-x-2">
                    {isCrit ? (
                      <AlertOctagon className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
                    ) : (
                      <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
                    )}
                    <div>
                      <div className="flex items-center space-x-2">
                        <span
                          className={`uppercase text-[10px] font-extrabold px-1.5 py-0.5 rounded ${
                            isCrit
                              ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
                              : 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                          }`}
                        >
                          {alert.severity}
                        </span>
                        <span className="font-semibold text-slate-200">
                          {alert.alert_type.replace('_', ' ').toUpperCase()}
                        </span>
                      </div>
                      <p className="text-slate-300 mt-1 leading-relaxed">{alert.message}</p>
                    </div>
                  </div>

                  {/* Acknowledge Button or Status */}
                  <div className="shrink-0">
                    {isActive ? (
                      <button
                        onClick={() => handleAcknowledge(alert.id)}
                        disabled={acknowledgingId === alert.id}
                        className="px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-cyan-300 hover:text-white border border-cyan-800/50 hover:border-cyan-600 font-medium text-[11px] flex items-center space-x-1 transition-all disabled:opacity-50"
                        title="Mark alert as acknowledged"
                      >
                        {acknowledgingId === alert.id ? (
                          <Loader2 className="w-3 h-3 animate-spin" />
                        ) : (
                          <CheckCircle className="w-3 h-3" />
                        )}
                        <span>Acknowledge</span>
                      </button>
                    ) : (
                      <span className="inline-flex items-center space-x-1 text-[11px] text-emerald-400 font-medium bg-emerald-950/40 px-2 py-0.5 rounded border border-emerald-800">
                        <CheckCircle className="w-3 h-3" />
                        <span>Acknowledged</span>
                      </span>
                    )}
                  </div>
                </div>

                {/* Footer Metadata */}
                <div className="mt-2.5 pt-2 border-t border-slate-800/60 flex items-center justify-between text-[11px] text-slate-400 font-mono">
                  <div className="flex items-center space-x-1">
                    <Clock className="w-3 h-3 text-slate-500" />
                    <span>{formatTimestamp(alert.created_at)}</span>
                  </div>
                  <div>
                    Observed: <strong className="text-slate-300">{alert.observed_value}</strong> | Threshold:{' '}
                    <strong className="text-slate-300">{alert.threshold_value}</strong>
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
