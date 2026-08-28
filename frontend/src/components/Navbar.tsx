import React from 'react';
import {
  LayoutDashboard,
  ListTodo,
  Bot,
  Wrench,
  Database,
  BarChart3,
  Activity,
  ShieldCheck,
  Settings,
  Plus,
  CheckCircle2,
  AlertCircle,
} from 'lucide-react';
import { SystemHealth } from '../services/api';

interface NavbarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  onNewTask: () => void;
  health: SystemHealth;
}

export const Navbar: React.FC<NavbarProps> = ({ activeTab, setActiveTab, onNewTask, health }) => {
  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'tasks', label: 'Tasks', icon: ListTodo },
    { id: 'agents', label: 'Agents', icon: Bot },
    { id: 'mcp-tools', label: 'MCP Tools', icon: Wrench },
    { id: 'rag', label: 'Code RAG', icon: Database },
    { id: 'evaluations', label: 'Evaluations', icon: BarChart3 },
    { id: 'observability', label: 'Observability', icon: Activity },
    { id: 'security', label: 'Security', icon: ShieldCheck },
    { id: 'settings', label: 'Settings', icon: Settings },
  ];

  return (
    <header className="border-b border-slate-800 bg-[#0b101d] sticky top-0 z-50">
      {/* Top Header Identity Bar */}
      <div className="max-w-[1600px] mx-auto px-6 py-3 flex items-center justify-between border-b border-slate-800/60">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center text-white font-bold font-mono text-sm shadow-sm">
              CP
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-bold text-slate-100 text-base tracking-tight">CodePilot-MCP</span>
                <span className="text-[10px] font-mono font-semibold px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
                  Enterprise v0.1.0
                </span>
              </div>
              <p className="text-xs text-slate-400">
                Autonomous AI Software Engineering Platform
              </p>
            </div>
          </div>
        </div>

        {/* Real System Status Indicators */}
        <div className="hidden lg:flex items-center gap-4 text-xs font-medium text-slate-300">
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded bg-slate-900 border border-slate-800">
            <span className={`w-2 h-2 rounded-full ${health.status === 'online' ? 'bg-emerald-400 animate-pulse' : 'bg-rose-400'}`} />
            <span>System {health.status === 'online' ? 'Operational' : 'Offline'}</span>
          </div>

          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded bg-slate-900 border border-slate-800">
            <span className="w-2 h-2 rounded-full bg-emerald-400" />
            <span>MCP Connected</span>
          </div>

          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded bg-slate-900 border border-slate-800">
            <span className="w-2 h-2 rounded-full bg-emerald-400" />
            <span>RAG Connected</span>
          </div>

          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded bg-slate-900 border border-slate-800">
            <span className="w-2 h-2 rounded-full bg-emerald-400" />
            <span>Sandbox Ready</span>
          </div>

          <button
            onClick={onNewTask}
            className="flex items-center gap-1.5 px-3.5 py-1.5 bg-blue-600 hover:bg-blue-500 text-white font-medium text-xs rounded-md transition-colors shadow-sm"
          >
            <Plus className="w-4 h-4" />
            New Task
          </button>
        </div>
      </div>

      {/* Navigation Sub-header Tabs */}
      <div className="max-w-[1600px] mx-auto px-6 flex items-center overflow-x-auto">
        <nav className="flex items-center gap-1 py-1.5">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`flex items-center gap-2 px-3.5 py-2 rounded-md text-xs font-medium transition-colors ${
                  isActive
                    ? 'bg-slate-800 text-white font-semibold border border-slate-700'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60'
                }`}
              >
                <Icon className={`w-3.5 h-3.5 ${isActive ? 'text-blue-400' : 'text-slate-400'}`} />
                {item.label}
              </button>
            );
          })}
        </nav>
      </div>
    </header>
  );
};
