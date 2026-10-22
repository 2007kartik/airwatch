import React from 'react';
import { Activity, Database, Server, RefreshCw } from 'lucide-react';

export default function Navbar({ health, _isStale, lastUpdated, isRefreshing, onRefresh }) {
  const isApiOnline = health?.status === 'ok';
  const isDbConnected = health?.database === 'connected';

  const formatTime = (date) => {
    if (!date) return '--:--:--';
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
  };

  return (
    <header className="sticky top-0 z-50 bg-slate-900/90 backdrop-blur-md border-b border-slate-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          
          {/* Brand Logo & Name */}
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-600 to-teal-400 p-0.5 shadow-lg shadow-cyan-500/20 flex items-center justify-center">
              <div className="w-full h-full bg-slate-900 rounded-[10px] flex items-center justify-center">
                <Activity className="w-5 h-5 text-cyan-400 animate-pulse" />
              </div>
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="text-xl font-bold tracking-tight bg-gradient-to-r from-white via-slate-100 to-slate-400 bg-clip-text text-transparent">
                  AirWatch
                </span>
                <span className="text-xs px-2 py-0.5 rounded-full font-semibold bg-cyan-950/80 text-cyan-400 border border-cyan-800/60">
                  v0.1.0
                </span>
              </div>
              <p className="text-xs text-slate-400 hidden sm:block">
                Real-Time Environmental Analytics Dashboard
              </p>
            </div>
          </div>

          {/* SIMULATED DATA Prominent Badge */}
          <div className="flex items-center">
            <div className="flex items-center space-x-2 px-3 py-1.5 rounded-full bg-amber-950/40 border border-amber-600/50 text-amber-300 shadow-sm shadow-amber-900/20">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-amber-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-amber-500"></span>
              </span>
              <span className="text-xs font-bold tracking-wider uppercase">
                Simulated Data
              </span>
              <span className="text-[10px] text-amber-400/80 hidden md:inline font-medium">
                (Software Model • 5s Interval)
              </span>
            </div>
          </div>

          {/* Status Badges & Refresh */}
          <div className="flex items-center space-x-3">
            
            {/* API Health */}
            <div
              className={`hidden sm:flex items-center space-x-1.5 px-2.5 py-1 rounded-lg text-xs font-medium border ${
                isApiOnline
                  ? 'bg-emerald-950/40 border-emerald-800 text-emerald-400'
                  : 'bg-rose-950/40 border-rose-800 text-rose-400'
              }`}
              title={isApiOnline ? 'FastAPI Backend Online' : 'FastAPI Backend Unreachable'}
            >
              <Server className="w-3.5 h-3.5" />
              <span>{isApiOnline ? 'API Online' : 'API Offline'}</span>
            </div>

            {/* PostgreSQL Health */}
            <div
              className={`hidden md:flex items-center space-x-1.5 px-2.5 py-1 rounded-lg text-xs font-medium border ${
                isDbConnected
                  ? 'bg-emerald-950/40 border-emerald-800 text-emerald-400'
                  : 'bg-rose-950/40 border-rose-800 text-rose-400'
              }`}
              title={isDbConnected ? 'PostgreSQL 18 Connected' : 'PostgreSQL Disconnected'}
            >
              <Database className="w-3.5 h-3.5" />
              <span>{isDbConnected ? 'PG 18 Connected' : 'PG Disconnected'}</span>
            </div>

            {/* Last Polled Time & Refresh Action */}
            <div className="flex items-center space-x-2 pl-2 border-l border-slate-800">
              <div className="text-right hidden lg:block">
                <p className="text-[10px] uppercase tracking-wider text-slate-500 font-semibold">Last Polled</p>
                <p className="text-xs text-slate-300 font-mono">{formatTime(lastUpdated)}</p>
              </div>

              <button
                onClick={onRefresh}
                disabled={isRefreshing}
                className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white transition-colors border border-slate-700 disabled:opacity-50"
                title="Refresh Data Now"
                id="btn-refresh-dashboard"
              >
                <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin text-cyan-400' : ''}`} />
              </button>
            </div>

          </div>

        </div>
      </div>
    </header>
  );
}
