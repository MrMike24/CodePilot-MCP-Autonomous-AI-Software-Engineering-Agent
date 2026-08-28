import React, { useState, useEffect } from 'react';
import { Sidebar } from './components/Sidebar';
import { Header } from './components/Header';
import { TaskDashboard } from './components/TaskDashboard';
import { TasksView } from './components/TasksView';
import { MCPToolsView } from './components/MCPToolsView';
import { CodeRAGView } from './components/CodeRAGView';
import { EvaluationView } from './components/EvaluationView';
import { ObservabilityView } from './components/ObservabilityView';
import { SecurityView } from './components/SecurityView';
import { SettingsView } from './components/SettingsView';
import { NewTaskModal } from './components/NewTaskModal';
import {
  fetchHealth,
  fetchStats,
  fetchTasks,
  fetchTaskDetail,
  createTask as apiCreateTask,
  approveTask as apiApproveTask,
  TaskItem,
  SystemHealth,
  DashboardStats,
} from './services/api';

function extractTraces(detail: any) {
  let backendTraces: any[] = [];
  if (detail?.runs && detail.runs.length > 0) {
    detail.runs.forEach((run: any) => {
      if (run.steps) {
        run.steps.forEach((step: any) => {
          if (step.tool_calls && step.tool_calls.length > 0) {
            step.tool_calls.forEach((tc: any) => {
              let timeStr = '';
              if (tc.timestamp) {
                timeStr = typeof tc.timestamp === 'string' && tc.timestamp.includes('T')
                  ? tc.timestamp.split('T')[1].slice(0, 8)
                  : String(tc.timestamp).slice(11, 19);
              }
              backendTraces.push({
                time: timeStr || new Date().toTimeString().slice(0, 8),
                agent: step.agent_name,
                tool: tc.tool_name,
                args: tc.arguments,
                status: tc.status === 'SUCCESS' ? 'success' : 'failed',
                durationMs: tc.duration_ms,
              });
            });
          } else {
            let timeStr = '';
            if (step.timestamp) {
              timeStr = typeof step.timestamp === 'string' && step.timestamp.includes('T')
                ? step.timestamp.split('T')[1].slice(0, 8)
                : String(step.timestamp).slice(11, 19);
            }
            backendTraces.push({
              time: timeStr || new Date().toTimeString().slice(0, 8),
              agent: step.agent_name,
              tool: step.step_name,
              status: 'success',
              durationMs: 120,
            });
          }
        });
      }
    });
  }
  return backendTraces;
}

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [health, setHealth] = useState<SystemHealth>({
    status: 'online',
    project: 'CodePilot-MCP',
    version: '0.1.0',
    demo_mode: true,
    database: 'healthy',
  });
  const [tasks, setTasks] = useState<TaskItem[]>([]);
  const [selectedTask, setSelectedTask] = useState<TaskItem | null>(null);

  // Poll real health, task list & statistics from FastAPI backend
  useEffect(() => {
    async function loadBackendData() {
      try {
        const h = await fetchHealth();
        setHealth(h);

        const s = await fetchStats();
        if (s) setStats(s);

        const backendTasks = await fetchTasks();
        if (backendTasks && backendTasks.length > 0) {
          setTasks((prevTasks) => {
            return backendTasks.map((bt) => {
              const existing = prevTasks.find((p) => p.id === bt.id);
              return {
                ...bt,
                traces: existing?.traces || [],
                diff_summary: existing?.diff_summary || '',
                execution_result: existing?.execution_result,
                review: existing?.review,
                pull_request: existing?.pull_request,
              };
            });
          });

          setSelectedTask((prev) => {
            if (!prev) return backendTasks[0];
            const exists = backendTasks.some((bt) => bt.id === prev.id);
            if (!exists) return backendTasks[0];
            // Keep full detailed state of prev, never overwrite traces with empty list
            return prev;
          });
        } else {
          setTasks([]);
          setSelectedTask(null);
        }
      } catch (err: any) {
        console.warn('Backend load error', err);
      }
    }
    loadBackendData();
    const interval = setInterval(loadBackendData, 3000);
    return () => clearInterval(interval);
  }, []);

  // Dedicated real-time polling for selected active task
  useEffect(() => {
    if (!selectedTask || !selectedTask.id) return;

    let isMounted = true;
    async function pollSelectedTask() {
      if (!selectedTask?.id) return;
      try {
        const detail = await fetchTaskDetail(selectedTask.id);
        if (detail && isMounted) {
          setErrorMessage(null);
          const backendTraces = extractTraces(detail);

          const updatedTask: TaskItem = {
            ...detail,
            traces: backendTraces,
            diff_summary: detail.diff_summary || '',
          };

          setSelectedTask(updatedTask);
          setTasks((prev) => prev.map((t) => (t.id === updatedTask.id ? updatedTask : t)));

          // Refresh stats if terminal state reached
          if (['WAITING_APPROVAL', 'COMPLETED', 'APPROVED', 'DELIVERED', 'FAILED', 'REJECTED'].includes(detail.status)) {
            fetchStats().then((s) => s && setStats(s)).catch(() => {});
          }
        }
      } catch (err: any) {
        if (isMounted) {
          // If task not found (404), reset selectedTask so UI doesn't remain stuck
          if (err.message && err.message.includes('404')) {
            const allTasks = await fetchTasks().catch(() => []);
            if (allTasks.length > 0) {
              setSelectedTask(allTasks[0]);
              setTasks(allTasks);
            } else {
              setSelectedTask(null);
              setTasks([]);
            }
          } else {
            setErrorMessage(`Live polling error: ${err.message || 'Failed to reach task endpoint'}`);
          }
        }
      }
    }

    pollSelectedTask();
    const interval = setInterval(pollSelectedTask, 1500);
    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, [selectedTask?.id]);

  const handleCreateTask = async (newTask: { title: string; description: string; branch: string }) => {
    setErrorMessage(null);
    try {
      const created = await apiCreateTask({
        title: newTask.title,
        description: newTask.description,
        target_branch: newTask.branch,
      });
      const initialTask: TaskItem = {
        ...created,
        status: created.status || 'CREATED',
        traces: [],
        diff_summary: '',
      };
      setTasks((prev) => [initialTask, ...prev.filter((t) => t.id !== initialTask.id)]);
      setSelectedTask(initialTask);
    } catch (err: any) {
      setErrorMessage(`Task creation failed: ${err.message}`);
    }
  };

  const handleApprove = async (taskId: string, comments: string) => {
    if (!taskId) return;
    setErrorMessage(null);
    try {
      await apiApproveTask(taskId, true, comments);
      const detail = await fetchTaskDetail(taskId);
      const updatedTask: TaskItem = {
        ...detail,
        traces: extractTraces(detail),
      };
      setSelectedTask(updatedTask);
      setTasks((prev) => prev.map((t) => (t.id === taskId ? updatedTask : t)));
      fetchStats().then((s) => s && setStats(s)).catch(() => {});
    } catch (err: any) {
      setErrorMessage(`Approval action failed: ${err.message}`);
    }
  };

  const handleReject = async (taskId: string, comments: string) => {
    if (!taskId) return;
    setErrorMessage(null);
    try {
      await apiApproveTask(taskId, false, comments);
      const detail = await fetchTaskDetail(taskId);
      const updatedTask: TaskItem = {
        ...detail,
        traces: extractTraces(detail),
      };
      setSelectedTask(updatedTask);
      setTasks((prev) => prev.map((t) => (t.id === taskId ? updatedTask : t)));
      fetchStats().then((s) => s && setStats(s)).catch(() => {});
    } catch (err: any) {
      setErrorMessage(`Rejection action failed: ${err.message}`);
    }
  };

  const handleSelectTask = (t: TaskItem) => {
    setSelectedTask({
      ...t,
      traces: t.traces || [],
      diff_summary: t.diff_summary || '',
      execution_result: t.execution_result,
      review: t.review,
    });
  };

  return (
    <div className="app-shell">
      {/* 1. Fixed Sidebar Navigation */}
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} health={health} />

      {/* 2. Main Right Container Shell */}
      <div className="main-wrapper">
        {/* Top Header */}
        <Header activeTab={activeTab} onNewTask={() => setIsModalOpen(true)} health={health} />

        {/* Global Error Banner if API error occurs */}
        {errorMessage && (
          <div style={{ backgroundColor: 'rgba(239, 68, 68, 0.15)', borderBottom: '1px solid #ef4444', padding: '8px 24px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', color: '#fca5a5', fontSize: 13 }}>
            <span>⚠️ {errorMessage}</span>
            <button onClick={() => setErrorMessage(null)} style={{ background: 'none', border: 'none', color: '#fca5a5', cursor: 'pointer', fontWeight: 'bold' }}>✕</button>
          </div>
        )}

        {/* Main Content Scrollable Area */}
        <main className="main-content">
          {activeTab === 'dashboard' && (
            <TaskDashboard
              tasks={tasks}
              selectedTask={selectedTask}
              stats={stats}
              onSelectTask={handleSelectTask}
              onApproveTask={handleApprove}
              onRejectTask={handleReject}
            />
          )}
          {activeTab === 'tasks' && (
            <TasksView
              tasks={tasks}
              onSelectTask={(t) => {
                handleSelectTask(t);
                setActiveTab('dashboard');
              }}
              onNewTask={() => setIsModalOpen(true)}
            />
          )}
          {activeTab === 'agents' && (
            <div className="dashboard-content">
              <div className="panel">
                <h2 style={{ margin: '0 0 16px 0', fontSize: 18, fontWeight: 700, color: '#f9fafb' }}>
                  Multi-Agent System Orchestration Graph
                </h2>
                <div style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: 12, color: '#60a5fa' }}>
                  <pre style={{ margin: 0 }}>
{`START
  │
  ▼
Planner Agent ───► Code RAG Retrieval (Qdrant)
  │
  ▼
Coding Agent  ───► MCP Filesystem & Execution Tools
  │
  ▼
Execution MCP ───► Pytest Sandbox Container
  │
  ├───────► Tests Failed & Iterations < 5 ───► Debugger Agent
  │                                                  │
  │                                                  ▼
  │                                           Execution MCP
  │
  ├───────► Tests Passed ───► Reviewer Agent
  │                                │
  ▼                                ▼
Tests Failed & Iterations >= 5   Human Approval Gate
  │                                │
  ▼                                ├─► Approved ──► GitHub MCP Create PR ──► END
  END (Report Failure)             └─► Rejected ──► END`}
                  </pre>
                </div>
              </div>
            </div>
          )}
          {activeTab === 'mcp-tools' && <MCPToolsView traces={selectedTask?.traces || []} />}
          {activeTab === 'rag' && <CodeRAGView />}
          {activeTab === 'evaluations' && <EvaluationView />}
          {activeTab === 'observability' && <ObservabilityView />}
          {activeTab === 'security' && <SecurityView />}
          {activeTab === 'settings' && <SettingsView />}
        </main>
      </div>

      {/* Task Creation Modal */}
      <NewTaskModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSubmit={handleCreateTask}
      />
    </div>
  );
};

export default App;
