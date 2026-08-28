import React, { useState } from 'react';
import { Terminal, ChevronDown, ChevronRight } from 'lucide-react';

export interface TraceStep {
  time: string;
  agent: string;
  tool: string;
  args?: Record<string, any>;
  status: 'success' | 'running' | 'failed';
  durationMs?: number;
}

interface AgentTraceViewProps {
  traces: TraceStep[];
}

export const AgentTraceView: React.FC<AgentTraceViewProps> = ({ traces }) => {
  const [expandedIndex, setExpandedIndex] = useState<number | null>(null);

  const activeTraces = traces || [];

  return (
    <div className="panel" style={{ margin: 0 }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderBottom: '1px solid #1f2937', paddingBottom: 12, marginBottom: 16 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <Terminal style={{ width: 16, height: 16, color: '#3b82f6' }} />
          <h3 style={{ margin: 0, fontSize: 12, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em', color: '#f9fafb' }}>
            AGENT EXECUTION TRACE
          </h3>
        </div>
        <span style={{ fontSize: 11, fontFamily: 'JetBrains Mono, monospace', color: '#9ca3af' }}>
          {activeTraces.length} recorded events
        </span>
      </div>

      {/* Trace Log List */}
      {activeTraces.length > 0 ? (
        <div className="trace-log-list">
          {activeTraces.map((trace, idx) => {
            const isExpanded = expandedIndex === idx;

            return (
              <div key={idx} className="trace-item" style={{ flexDirection: 'column', alignItems: 'stretch' }}>
                <div
                  onClick={() => setExpandedIndex(isExpanded ? null : idx)}
                  style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', cursor: 'pointer' }}
                >
                  <div className="trace-left">
                    <span className="trace-time">{trace.time}</span>
                    <span className="trace-agent-tag">{trace.agent}</span>
                    <span className="trace-tool">✓ {trace.tool}()</span>
                  </div>

                  <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    <span className="trace-duration">{trace.durationMs ? `${trace.durationMs}ms` : '—'}</span>
                    {trace.args && (
                      isExpanded ? <ChevronDown style={{ width: 14, height: 14, color: '#9ca3af' }} /> : <ChevronRight style={{ width: 14, height: 14, color: '#6b7280' }} />
                    )}
                  </div>
                </div>

                {/* Expandable JSON Arguments */}
                {isExpanded && trace.args && (
                  <div style={{ marginTop: 10, paddingTop: 8, borderTop: '1px solid #1f2937' }}>
                    <div style={{ fontSize: 10, color: '#6b7280', textTransform: 'uppercase', fontWeight: 700 }}>Tool Arguments:</div>
                    <pre style={{ margin: '4px 0 0 0', padding: 8, background: '#040711', borderRadius: 4, color: '#60a5fa', fontSize: 11 }}>
                      {JSON.stringify(trace.args, null, 2)}
                    </pre>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      ) : (
        <div style={{ padding: '32px 16px', textAlign: 'center', color: '#6b7280', fontSize: 12, fontFamily: 'monospace' }}>
          No agent execution trace events recorded yet for this task.
        </div>
      )}
    </div>
  );
};

