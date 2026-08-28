import React from 'react';
import { Plus } from 'lucide-react';
import { SystemHealth } from '../services/api';

interface HeaderProps {
  activeTab: string;
  onNewTask: () => void;
  health: SystemHealth;
}

export const Header: React.FC<HeaderProps> = ({ activeTab, onNewTask, health }) => {
  const getTitle = () => {
    switch (activeTab) {
      case 'dashboard':
        return 'Dashboard';
      case 'tasks':
        return 'Tasks';
      case 'agents':
        return 'Multi-Agent Orchestration Graph';
      case 'mcp-tools':
        return 'Model Context Protocol (MCP) Tools';
      case 'rag':
        return 'Code-Aware RAG Engine';
      case 'evaluations':
        return 'Evaluation Benchmark';
      case 'observability':
        return 'Observability & Telemetry';
      case 'security':
        return 'Security Architecture';
      case 'settings':
        return 'Platform Settings';
      default:
        return 'Dashboard';
    }
  };

  return (
    <header className="header">
      {/* Active Tab Page Title */}
      <h1 className="header-title">{getTitle()}</h1>

      {/* Right System Indicators & CTA Button */}
      <div className="header-right">
        <div className="header-badges">
          <div className="badge-item">
            <span className="status-dot" />
            <span>System Operational</span>
          </div>
          <div className="badge-item">
            <span className="status-dot" />
            <span>MCP Connected</span>
          </div>
          <div className="badge-item">
            <span className="status-dot" />
            <span>RAG Connected</span>
          </div>
          <div className="badge-item">
            <span className="status-dot" />
            <span>Sandbox Ready</span>
          </div>
        </div>

        <button onClick={onNewTask} className="btn-primary">
          <Plus style={{ width: 16, height: 16 }} />
          <span>New Task</span>
        </button>
      </div>
    </header>
  );
};
