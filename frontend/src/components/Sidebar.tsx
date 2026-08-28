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
} from 'lucide-react';
import { SystemHealth } from '../services/api';

interface SidebarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  health: SystemHealth;
}

export const Sidebar: React.FC<SidebarProps> = ({ activeTab, setActiveTab, health }) => {
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
    <aside className="sidebar">
      {/* Top Brand Branding Header */}
      <div>
        <div className="sidebar-brand">
          <div className="sidebar-logo">CP</div>
          <div>
            <h1 className="sidebar-brand-title">CodePilot-MCP</h1>
            <p className="sidebar-brand-subtitle">Autonomous AI Engineering</p>
          </div>
        </div>

        {/* Navigation Items List */}
        <nav className="nav-list">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`nav-item ${isActive ? 'active' : ''}`}
              >
                <Icon className="nav-icon" />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>
      </div>

      {/* Bottom System Status Section */}
      <div className="sidebar-status">
        <div className="sidebar-status-title">System Infrastructure Status</div>

        <div className="status-row">
          <span className="status-label">System Status</span>
          <span className="status-indicator">
            <span className="status-dot" />
            Operational
          </span>
        </div>

        <div className="status-row">
          <span className="status-label">MCP Protocol</span>
          <span className="status-indicator">
            <span className="status-dot" />
            Connected
          </span>
        </div>

        <div className="status-row">
          <span className="status-label">Code RAG</span>
          <span className="status-indicator">
            <span className="status-dot" />
            Connected
          </span>
        </div>

        <div className="status-row">
          <span className="status-label">Docker Sandbox</span>
          <span className="status-indicator">
            <span className="status-dot" />
            Ready
          </span>
        </div>
      </div>
    </aside>
  );
};
