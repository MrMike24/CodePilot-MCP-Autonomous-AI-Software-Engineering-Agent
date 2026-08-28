import React from 'react';
import { ListTodo, Plus, CheckCircle2, Clock, XCircle, ChevronRight } from 'lucide-react';
import { TaskItem } from '../services/api';

interface TasksViewProps {
  tasks: TaskItem[];
  onSelectTask: (task: TaskItem) => void;
  onNewTask: () => void;
}

export const TasksView: React.FC<TasksViewProps> = ({ tasks, onSelectTask, onNewTask }) => {
  return (
    <div className="p-6 max-w-[1600px] mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-slate-100 flex items-center gap-2">
            <ListTodo className="w-5 h-5 text-blue-400" />
            Engineering Tasks History
          </h2>
          <p className="text-xs text-slate-400">
            Repository-level task history and execution status
          </p>
        </div>

        <button
          onClick={onNewTask}
          className="flex items-center gap-1.5 px-3.5 py-1.5 bg-blue-600 hover:bg-blue-500 text-white font-medium text-xs rounded-md transition-colors shadow-sm"
        >
          <Plus className="w-4 h-4" />
          Create Task
        </button>
      </div>

      {/* Task List Table */}
      <div className="panel overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left font-mono text-xs">
            <thead className="bg-slate-900/80 text-slate-400 uppercase tracking-wider border-b border-slate-800">
              <tr>
                <th className="py-3 px-4">Task ID</th>
                <th className="py-3 px-4">Title & Issue Description</th>
                <th className="py-3 px-4">Feature Branch</th>
                <th className="py-3 px-4">Created Date</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/80">
              {tasks.map((t) => (
                <tr key={t.id} className="hover:bg-slate-900/40 transition-colors">
                  <td className="py-3 px-4 text-blue-400 font-bold">{t.id.slice(0, 12)}</td>
                  <td className="py-3 px-4 font-sans font-medium text-slate-100 max-w-md">
                    <div>{t.title}</div>
                    <div className="text-xs text-slate-400 font-normal line-clamp-1 mt-0.5">{t.description}</div>
                  </td>
                  <td className="py-3 px-4 text-emerald-400">{t.feature_branch || t.featureBranch || 'codepilot/fix'}</td>
                  <td className="py-3 px-4 text-slate-400">{t.created_at || t.createdAt || 'N/A'}</td>
                  <td className="py-3 px-4">
                    {t.status === 'COMPLETED' || t.status === 'APPROVED' ? (
                      <span className="px-2 py-0.5 rounded text-emerald-400 bg-emerald-950/40 border border-emerald-500/30 font-bold text-[10px]">
                        ✓ {t.status}
                      </span>
                    ) : t.status === 'WAITING_APPROVAL' ? (
                      <span className="px-2 py-0.5 rounded text-amber-400 bg-amber-950/40 border border-amber-500/30 font-bold text-[10px]">
                        ⚠ WAITING
                      </span>
                    ) : (
                      <span className="px-2 py-0.5 rounded text-blue-400 bg-blue-950/40 border border-blue-500/30 font-bold text-[10px]">
                        ● {t.status}
                      </span>
                    )}
                  </td>
                  <td className="py-3 px-4 text-right">
                    <button
                      onClick={() => onSelectTask(t)}
                      className="text-blue-400 hover:text-blue-300 font-semibold text-xs inline-flex items-center gap-1"
                    >
                      View Detail <ChevronRight className="w-3.5 h-3.5" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
