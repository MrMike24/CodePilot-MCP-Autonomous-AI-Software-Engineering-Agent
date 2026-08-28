export interface SystemHealth {
  status: string;
  project: string;
  version: string;
  demo_mode: boolean;
  database: string;
}

export interface TaskItem {
  id: string;
  title: string;
  description: string;
  repository_id: string;
  status: string;
  target_branch: string;
  feature_branch?: string;
  featureBranch?: string;
  created_at: string;
  createdAt?: string;
  updated_at: string;
  repository?: any;
  runs?: any[];
  review?: any;
  diff_summary?: string;
  diffSummary?: string;
  execution_result?: any;
  pull_request?: any;
  prResult?: any;
  traces: any[];
}

export interface BenchmarkReport {
  summary: {
    total_tasks: number;
    completed_tasks: number;
    task_completion_rate: number;
    test_pass_rate: number;
    tool_selection_accuracy: number;
    avg_iterations: number;
    avg_latency_sec: number;
    avg_cost_usd: number;
  };
  results: Array<{
    task_id: string;
    category: string;
    name: string;
    status: string;
    latency_sec: number;
    iterations: number;
    cost_usd: number;
  }>;
}

export interface DashboardStats {
  total_tasks: number;
  active_tasks: number;
  waiting_approval: number;
  completed_tasks: number;
  failed_tasks: number;
  test_pass_rate: string;
  avg_latency: string;
  docker_sandbox: string;
}

const API_BASE = '/api/v1';

export async function fetchHealth(): Promise<SystemHealth> {
  try {
    const res = await fetch(`${API_BASE}/health`);
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    return await res.json();
  } catch (err) {
    return {
      status: 'offline',
      project: 'CodePilot-MCP',
      version: '0.1.0',
      demo_mode: true,
      database: 'unhealthy',
    };
  }
}

export async function fetchStats(): Promise<DashboardStats | null> {
  try {
    const res = await fetch(`${API_BASE}/tasks/stats/summary`);
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    return await res.json();
  } catch (err) {
    console.warn('Backend API fetchStats failed.', err);
    return null;
  }
}

export async function fetchTasks(): Promise<TaskItem[]> {
  try {
    const res = await fetch(`${API_BASE}/tasks`);
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    return await res.json();
  } catch (err) {
    console.warn('Backend API fetchTasks failed. Using fallback state.', err);
    return [];
  }
}

export async function fetchTaskDetail(taskId: string): Promise<TaskItem> {
  const res = await fetch(`${API_BASE}/tasks/${taskId}`);
  if (!res.ok) {
    const errText = await res.text().catch(() => '');
    throw new Error(`HTTP error ${res.status}: ${errText || res.statusText}`);
  }
  return await res.json();
}

export async function createTask(data: { title: string; description: string; target_branch?: string }): Promise<TaskItem> {
  const res = await fetch(`${API_BASE}/tasks`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const errText = await res.text().catch(() => '');
    throw new Error(`Failed to create task (${res.status}): ${errText || res.statusText}`);
  }
  return await res.json();
}

export async function approveTask(taskId: string, approved: boolean, comments?: string): Promise<any> {
  const res = await fetch(`${API_BASE}/tasks/${taskId}/approve`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ approved, comments, approved_by: 'human_operator' }),
  });
  if (!res.ok) {
    const errText = await res.text().catch(() => '');
    throw new Error(`Failed to submit approval (${res.status}): ${errText || res.statusText}`);
  }
  return await res.json();
}
