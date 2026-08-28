import React, { useState } from 'react';
import { Wrench, HardDrive, Terminal, GitBranch, Search } from 'lucide-react';
import { TraceStep } from './AgentTraceView';

interface MCPToolsViewProps {
  traces: TraceStep[];
}

export const MCPToolsView: React.FC<MCPToolsViewProps> = ({ traces }) => {
  const [filterServer, setFilterServer] = useState<'all' | 'filesystem' | 'execution' | 'github'>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCall, setSelectedCall] = useState<TraceStep | null>(null);

  const getServer = (toolName: string): 'filesystem' | 'execution' | 'github' => {
    if (['run_tests', 'run_linter', 'run_typecheck', 'run_security_scan'].includes(toolName)) {
      return 'execution';
    }
    if (['create_pull_request', 'get_repository', 'create_branch', 'get_issue', 'list_issues'].includes(toolName)) {
      return 'github';
    }
    return 'filesystem';
  };

  const filteredTraces = traces.filter((t) => {
    const server = getServer(t.tool);
    if (filterServer !== 'all' && server !== filterServer) return false;
    if (searchQuery && !t.tool.toLowerCase().includes(searchQuery.toLowerCase())) return false;
    return true;
  });

  return (
    <div className="content-container">
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 20 }}>
        <div>
          <h2 style={{ margin: 0, fontSize: 18, fontWeight: 700, color: '#f9fafb', display: 'flex', alignItems: 'center', gap: 8 }}>
            <Wrench style={{ width: 20, height: 20, color: '#3b82f6' }} />
            Model Context Protocol (MCP) Tool Inspector
          </h2>
          <p style={{ margin: '4px 0 0 0', fontSize: 12, color: '#9ca3af' }}>
            Real-time telemetry log of decoupled MCP server tool invocations
          </p>
        </div>

        {/* Filters */}
        <div style={{ display: 'flex', gap: 4, background: '#0b101d', padding: 4, borderRadius: 6, border: '1px solid #1f2937' }}>
          <button
            onClick={() => setFilterServer('all')}
            className="btn-secondary"
            style={{ padding: '4px 12px', fontSize: 12, backgroundColor: filterServer === 'all' ? '#1f2937' : 'transparent', borderColor: filterServer === 'all' ? '#374151' : 'transparent' }}
          >
            All Tools ({traces.length})
          </button>
          <button
            onClick={() => setFilterServer('filesystem')}
            className="btn-secondary"
            style={{ padding: '4px 12px', fontSize: 12, backgroundColor: filterServer === 'filesystem' ? '#1f2937' : 'transparent', borderColor: filterServer === 'filesystem' ? '#374151' : 'transparent' }}
          >
            Filesystem
          </button>
          <button
            onClick={() => setFilterServer('execution')}
            className="btn-secondary"
            style={{ padding: '4px 12px', fontSize: 12, backgroundColor: filterServer === 'execution' ? '#1f2937' : 'transparent', borderColor: filterServer === 'execution' ? '#374151' : 'transparent' }}
          >
            Execution
          </button>
          <button
            onClick={() => setFilterServer('github')}
            className="btn-secondary"
            style={{ padding: '4px 12px', fontSize: 12, backgroundColor: filterServer === 'github' ? '#1f2937' : 'transparent', borderColor: filterServer === 'github' ? '#374151' : 'transparent' }}
          >
            GitHub
          </button>
        </div>
      </div>

      {/* Tool Call Inspector Table */}
      <div className="panel" style={{ padding: 0, overflow: 'hidden' }}>
        <div style={{ padding: 16, borderBottom: '1px solid #1f2937', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, background: '#040711', border: '1px solid #1f2937', padding: '6px 12px', borderRadius: 6, width: 280 }}>
            <Search style={{ width: 14, height: 14, color: '#6b7280' }} />
            <input
              type="text"
              placeholder="Search tool name..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              style={{ background: 'transparent', border: 'none', color: '#f9fafb', fontSize: 12, outline: 'none', width: '100%', fontFamily: 'JetBrains Mono, monospace' }}
            />
          </div>
          <span style={{ fontSize: 12, color: '#9ca3af', fontFamily: 'JetBrains Mono, monospace' }}>
            Showing {filteredTraces.length} recorded calls
          </span>
        </div>

        <div className="table-wrapper">
          <table className="custom-table">
            <thead>
              <tr>
                <th>Timestamp</th>
                <th>MCP Server</th>
                <th>Tool Name</th>
                <th>Arguments Payload</th>
                <th>Duration</th>
                <th>Status</th>
                <th style={{ textAlign: 'right' }}>Action</th>
              </tr>
            </thead>
            <tbody>
              {filteredTraces.map((t, idx) => {
                const server = getServer(t.tool);
                return (
                  <tr key={idx}>
                    <td style={{ color: '#9ca3af' }}>{t.time}</td>
                    <td>
                      <span className="trace-agent-tag">{server}</span>
                    </td>
                    <td style={{ color: '#3b82f6', fontWeight: 700 }}>{t.tool}()</td>
                    <td style={{ color: '#d1d5db', maxWidth: 280, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      {t.args ? JSON.stringify(t.args) : '{}'}
                    </td>
                    <td style={{ color: '#9ca3af' }}>
                      {t.durationMs ? `${t.durationMs}ms` : '—'}
                    </td>
                    <td>
                      {t.status === 'success' ? (
                        <span className="status-badge completed">✓ Success</span>
                      ) : (
                        <span className="status-badge" style={{ backgroundColor: 'rgba(239, 68, 68, 0.1)', color: '#ef4444', borderColor: 'rgba(239, 68, 68, 0.3)' }}>✕ Failed</span>
                      )}
                    </td>
                    <td style={{ textAlign: 'right' }}>
                      <button
                        onClick={() => setSelectedCall(t)}
                        className="btn-secondary"
                        style={{ padding: '2px 8px', fontSize: 11, color: '#60a5fa' }}
                      >
                        Inspect
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Payload Modal */}
      {selectedCall && (
        <div className="modal-overlay">
          <div className="modal-card">
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderBottom: '1px solid #1f2937', paddingBottom: 12, marginBottom: 16 }}>
              <h3 style={{ margin: 0, fontSize: 14, fontWeight: 700, fontFamily: 'JetBrains Mono, monospace', color: '#f9fafb' }}>
                MCP Tool Call: {selectedCall.tool}()
              </h3>
              <button onClick={() => setSelectedCall(null)} style={{ background: 'none', border: 'none', color: '#9ca3af', cursor: 'pointer', fontSize: 14 }}>
                ✕
              </button>
            </div>

            <div style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: 12 }}>
              <div style={{ marginBottom: 12 }}>
                <span className="meta-label">MCP Server:</span>
                <div style={{ color: '#f9fafb', marginTop: 2 }}>{getServer(selectedCall.tool)}</div>
              </div>

              <div>
                <span className="meta-label">Arguments Payload:</span>
                <pre style={{ background: '#040711', padding: 12, borderRadius: 6, border: '1px solid #1f2937', color: '#60a5fa', overflowX: 'auto', marginTop: 4 }}>
                  {JSON.stringify(selectedCall.args || {}, null, 2)}
                </pre>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
