import React from 'react';
import { ShieldAlert } from 'lucide-react';

export default function Footer() {
  return (
    <footer className="mt-12 border-t border-slate-800 bg-slate-950/80 py-8 text-xs text-slate-500">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-4">
        
        <div className="flex flex-col md:flex-row items-center justify-between gap-4">
          <div>
            <p className="font-semibold text-slate-300">
              AirWatch: Real-Time Air Quality Monitoring Dashboard
            </p>
            <p className="text-[11px] text-slate-400 mt-0.5">
              IoT and Analytics • Academic & Research Prototype
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-2 text-[11px] font-mono text-slate-400">
            <span className="px-2 py-0.5 rounded bg-slate-900 border border-slate-800">React 19</span>
            <span className="px-2 py-0.5 rounded bg-slate-900 border border-slate-800">Tailwind CSS</span>
            <span className="px-2 py-0.5 rounded bg-slate-900 border border-slate-800">Recharts</span>
            <span className="px-2 py-0.5 rounded bg-slate-900 border border-slate-800">FastAPI</span>
            <span className="px-2 py-0.5 rounded bg-slate-900 border border-slate-800">PostgreSQL 18</span>
            <span className="px-2 py-0.5 rounded bg-slate-900 border border-slate-800">SQLAlchemy</span>
          </div>
        </div>

        <div className="border-t border-slate-900 pt-4 flex flex-col sm:flex-row items-center justify-between gap-2 text-[11px]">
          <p className="flex items-center space-x-1.5 text-slate-400">
            <ShieldAlert className="w-3.5 h-3.5 text-amber-500 shrink-0" />
            <span>
              <strong>Notice:</strong> This dashboard is powered by a standalone mathematical data simulator. No physical hardware sensors or official regulatory AQI calculations are used.
            </span>
          </p>
          <p className="shrink-0 text-slate-500">
            © 2026 AirWatch Team
          </p>
        </div>

      </div>
    </footer>
  );
}
