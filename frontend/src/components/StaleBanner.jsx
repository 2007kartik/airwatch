import React from 'react';
import { AlertCircle, RefreshCw } from 'lucide-react';

export default function StaleBanner({ isStale, error, lastUpdated, onRetry }) {
  if (!isStale) return null;

  return (
    <div className="bg-rose-950/80 border-b border-rose-800 text-rose-200 px-4 py-2.5 shadow-md">
      <div className="max-w-7xl mx-auto flex items-center justify-between text-xs sm:text-sm">
        <div className="flex items-center space-x-2">
          <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
          <span>
            <strong className="font-semibold text-rose-100">Connection Warning:</strong>{' '}
            {error || 'Cannot reach the FastAPI backend at http://127.0.0.1:8000.'}{' '}
            <span className="text-rose-300">
              Displaying last cached reading ({lastUpdated ? lastUpdated.toLocaleTimeString() : 'N/A'}). Auto-retrying every 5s...
            </span>
          </span>
        </div>
        <button
          onClick={onRetry}
          className="ml-4 px-2.5 py-1 rounded bg-rose-900 hover:bg-rose-800 text-rose-100 font-medium text-xs flex items-center space-x-1 shrink-0 transition-colors border border-rose-700"
        >
          <RefreshCw className="w-3 h-3" />
          <span>Retry Now</span>
        </button>
      </div>
    </div>
  );
}
