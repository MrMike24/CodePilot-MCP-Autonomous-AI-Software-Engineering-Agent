import React from 'react';
import { Settings as SettingsIcon, Sliders, Database, Key, Shield } from 'lucide-react';

export const SettingsView: React.FC = () => {
  return (
    <div className="p-6 max-w-[1600px] mx-auto space-y-6">
      <div>
        <h2 className="text-xl font-bold text-slate-100 flex items-center gap-2">
          <SettingsIcon className="w-5 h-5 text-blue-400" />
          Platform System Configuration
        </h2>
        <p className="text-xs text-slate-400">
          Environment parameters, LLM providers, and system defaults
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Settings Panel 1 */}
        <div className="panel p-5 space-y-4">
          <h3 className="font-bold text-sm text-slate-100 uppercase tracking-wider border-b border-slate-800 pb-2">
            Execution Mode & Provider Settings
          </h3>
          <div className="space-y-3 font-mono text-xs">
            <div className="flex justify-between py-1 border-b border-slate-800/60">
              <span className="text-slate-400">DEMO_MODE:</span>
              <span className="text-emerald-400 font-bold">true (Zero-Credential Simulation)</span>
            </div>
            <div className="flex justify-between py-1 border-b border-slate-800/60">
              <span className="text-slate-400">LLM_PROVIDER:</span>
              <span className="text-blue-400 font-bold">openai (gpt-4o)</span>
            </div>
            <div className="flex justify-between py-1 border-b border-slate-800/60">
              <span className="text-slate-400">DOCKER_SANDBOX_IMAGE:</span>
              <span className="text-slate-200">python:3.12-slim</span>
            </div>
            <div className="flex justify-between py-1">
              <span className="text-slate-400">MAX_DEBUG_ITERATIONS:</span>
              <span className="text-amber-400 font-bold">5</span>
            </div>
          </div>
        </div>

        {/* Settings Panel 2 */}
        <div className="panel p-5 space-y-4">
          <h3 className="font-bold text-sm text-slate-100 uppercase tracking-wider border-b border-slate-800 pb-2">
            Database & Vector Store Connection
          </h3>
          <div className="space-y-3 font-mono text-xs">
            <div className="flex justify-between py-1 border-b border-slate-800/60">
              <span className="text-slate-400">POSTGRES_DB:</span>
              <span className="text-slate-200">codepilot_db</span>
            </div>
            <div className="flex justify-between py-1 border-b border-slate-800/60">
              <span className="text-slate-400">QDRANT_COLLECTION:</span>
              <span className="text-purple-400 font-bold">codepilot_codebase</span>
            </div>
            <div className="flex justify-between py-1 border-b border-slate-800/60">
              <span className="text-slate-400">PROMETHEUS_METRICS_PATH:</span>
              <span className="text-cyan-400">/api/v1/metrics</span>
            </div>
            <div className="flex justify-between py-1">
              <span className="text-slate-400">WORKSPACE_ROOT:</span>
              <span className="text-slate-300 truncate max-w-xs">demo_repository</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
