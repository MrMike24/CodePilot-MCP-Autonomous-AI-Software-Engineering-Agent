import React, { useState } from 'react';
import {
  CheckCircle2,
  AlertCircle,
  XCircle,
  Bot,
  Database,
  Wrench,
  Terminal,
  Bug,
  ShieldCheck,
  UserCheck,
  GitPullRequest,
} from 'lucide-react';

interface Stage {
  num: string;
  name: string;
  agent: string;
  desc: string;
  key: string;
  icon: any;
}

interface PipelineTimelineProps {
  currentStatus: string;
  runs?: any[];
  debugIterations?: number;
  onSelectStage?: (stageKey: string) => void;
}

export const PipelineTimeline: React.FC<PipelineTimelineProps> = ({
  currentStatus,
  runs = [],
  debugIterations = 0,
  onSelectStage,
}) => {
  const [selectedStage, setSelectedStage] = useState<string | null>(null);

  const stages: Stage[] = [
    { num: '01', name: 'Planning', agent: 'Planner Agent', desc: 'Code RAG & TaskPlan Generation', key: 'PLANNING', icon: Bot },
    { num: '02', name: 'Retrieval', agent: 'Code RAG', desc: 'Qdrant Hybrid Vector Search', key: 'RETRIEVING', icon: Database },
    { num: '03', name: 'Implementation', agent: 'Coding Agent', desc: 'MCP Workspace File Edits', key: 'IMPLEMENTING', icon: Wrench },
    { num: '04', name: 'Testing', agent: 'Execution MCP', desc: 'Docker Container Sandbox Pytest', key: 'TESTING', icon: Terminal },
    { num: '05', name: 'Debugging', agent: 'Debugger Agent', desc: 'Traceback Repair & Self-Correction', key: 'DEBUGGING', icon: Bug },
    { num: '06', name: 'Review', agent: 'Reviewer Agent', desc: 'Diff Quality Scorecard', key: 'REVIEWING', icon: ShieldCheck },
    { num: '07', name: 'Approval', agent: 'Human Operator', desc: 'Human-in-the-loop Gate', key: 'WAITING_APPROVAL', icon: UserCheck },
    { num: '08', name: 'Delivery', agent: 'GitHub MCP', desc: 'Git Commit / Pull Request', key: 'DELIVERED', icon: GitPullRequest },
  ];

  const hasDebuggerRan =
    debugIterations > 0 ||
    runs.some((r: any) =>
      r.steps &&
      r.steps.some(
        (s: any) =>
          s.agent_name?.toLowerCase().includes('debug') ||
          s.step_name?.toLowerCase().includes('debug')
      )
    );

  const getStageStatus = (key: string): 'completed' | 'running' | 'warning' | 'skipped' | 'failed' | 'pending' => {
    switch (key) {
      case 'PLANNING':
        if (currentStatus === 'PLANNING') return 'running';
        if (['RETRIEVING', 'IMPLEMENTING', 'TESTING', 'DEBUGGING', 'REVIEWING', 'WAITING_APPROVAL', 'APPROVED', 'DELIVERED', 'COMPLETED'].includes(currentStatus)) {
          return 'completed';
        }
        return 'pending';

      case 'RETRIEVING':
        if (currentStatus === 'RETRIEVING') return 'running';
        if (['IMPLEMENTING', 'TESTING', 'DEBUGGING', 'REVIEWING', 'WAITING_APPROVAL', 'APPROVED', 'DELIVERED', 'COMPLETED'].includes(currentStatus)) {
          return 'completed';
        }
        return 'pending';

      case 'IMPLEMENTING':
        if (currentStatus === 'IMPLEMENTING') return 'running';
        if (['TESTING', 'DEBUGGING', 'REVIEWING', 'WAITING_APPROVAL', 'APPROVED', 'DELIVERED', 'COMPLETED'].includes(currentStatus)) {
          return 'completed';
        }
        return 'pending';

      case 'TESTING':
        if (currentStatus === 'TESTING') return 'running';
        if (['DEBUGGING', 'REVIEWING', 'WAITING_APPROVAL', 'APPROVED', 'DELIVERED', 'COMPLETED'].includes(currentStatus)) {
          return 'completed';
        }
        return 'pending';

      case 'DEBUGGING':
        if (currentStatus === 'DEBUGGING') return 'running';
        if (['REVIEWING', 'WAITING_APPROVAL', 'APPROVED', 'DELIVERED', 'COMPLETED'].includes(currentStatus)) {
          return hasDebuggerRan ? 'completed' : 'skipped';
        }
        return 'pending';

      case 'REVIEWING':
        if (currentStatus === 'REVIEWING') return 'running';
        if (['WAITING_APPROVAL', 'APPROVED', 'DELIVERED', 'COMPLETED'].includes(currentStatus)) {
          return 'completed';
        }
        return 'pending';

      case 'WAITING_APPROVAL':
        if (['APPROVED', 'DELIVERED', 'COMPLETED'].includes(currentStatus)) return 'completed';
        if (currentStatus === 'WAITING_APPROVAL') return 'warning';
        if (currentStatus === 'REJECTED') return 'failed';
        return 'pending';

      case 'DELIVERED':
        if (['DELIVERED', 'COMPLETED'].includes(currentStatus)) return 'completed';
        if (currentStatus === 'APPROVED') return 'running';
        return 'pending';

      default:
        return 'pending';
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'completed':
        return <span style={{ color: '#10b981', fontSize: 10, fontWeight: 600 }}>✓ Done</span>;
      case 'running':
        return <span style={{ color: '#60a5fa', fontSize: 10, fontWeight: 600 }}>● Active</span>;
      case 'warning':
        return <span style={{ color: '#fbbf24', fontSize: 10, fontWeight: 600 }}>⚠ Awaiting</span>;
      case 'skipped':
        return <span style={{ color: '#9ca3af', fontSize: 10, fontWeight: 500 }}>✓ Skipped</span>;
      case 'failed':
        return <span style={{ color: '#f87171', fontSize: 10, fontWeight: 600 }}>✕ Rejected</span>;
      default:
        return <span style={{ color: '#4b5563', fontSize: 10 }}>○ Standby</span>;
    }
  };

  return (
    <div className="pipeline-container">
      <div className="pipeline-title">
        Autonomous Pipeline Execution Timeline
      </div>

      {/* Horizontal Pipeline Steps Grid */}
      <div className="pipeline-grid">
        {stages.map((st) => {
          const status = getStageStatus(st.key);
          const isSelected = selectedStage === st.key;

          return (
            <div
              key={st.key}
              onClick={() => {
                setSelectedStage(st.key);
                if (onSelectStage) onSelectStage(st.key);
              }}
              className={`pipeline-node ${status}`}
              style={{ cursor: 'pointer', border: isSelected ? '1px solid #3b82f6' : undefined }}
            >
              <div className="node-header">
                <span className="node-num">{st.num}</span>
                {status === 'completed' && <CheckCircle2 style={{ width: 14, height: 14, color: '#10b981' }} />}
                {status === 'running' && <span className="status-dot" style={{ backgroundColor: '#3b82f6', width: 8, height: 8, borderRadius: '50%', display: 'inline-block' }} />}
                {status === 'warning' && <AlertCircle style={{ width: 14, height: 14, color: '#f59e0b' }} />}
                {status === 'skipped' && <span style={{ fontSize: 9, color: '#9ca3af', fontFamily: 'monospace', fontWeight: 600 }}>PASS</span>}
                {status === 'failed' && <XCircle style={{ width: 14, height: 14, color: '#ef4444' }} />}
                {status === 'pending' && <span style={{ fontSize: 10, color: '#6b7280' }}>○</span>}
              </div>

              <div>
                <div className="node-name">{st.name}</div>
                <div className="node-agent" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: 3 }}>
                  <span>{st.agent}</span>
                </div>
                <div style={{ marginTop: 2 }}>{getStatusLabel(status)}</div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
