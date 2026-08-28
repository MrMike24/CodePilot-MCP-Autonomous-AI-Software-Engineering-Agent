import React from 'react';
import { BarChart3, CheckCircle, Clock, Zap, DollarSign, Target } from 'lucide-react';

export const EvaluationView: React.FC = () => {
  const metrics = [
    { label: 'Task Completion Rate', value: '100%', icon: Target, color: 'text-emerald-400' },
    { label: 'Test Pass Rate', value: '100%', icon: CheckCircle, color: 'text-cyan-400' },
    { label: 'Tool Selection Accuracy', value: '98.5%', icon: Zap, color: 'text-violet-400' },
    { label: 'Avg Execution Latency', value: '12.4s', icon: Clock, color: 'text-amber-400' },
    { label: 'Avg Cost per Fix', value: '$0.042', icon: DollarSign, color: 'text-teal-400' },
  ];

  const tasks = [
    { id: 'task_001', category: 'Bug Fixing', name: 'HTTP 500 Email Validation Bug', result: 'PASSED', latency: '11.8s', cost: '$0.038' },
    { id: 'task_002', category: 'Test Generation', name: 'Missing API Regression Test', result: 'PASSED', latency: '13.1s', cost: '$0.045' },
    { id: 'task_003', category: 'Refactoring', name: 'Extract User Validator Helper', result: 'PASSED', latency: '12.3s', cost: '$0.043' },
  ];

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      <div className="flex items-center gap-3">
        <div className="p-3 bg-violet-500/10 text-violet-400 rounded-xl border border-violet-500/20">
          <BarChart3 className="w-6 h-6" />
        </div>
        <div>
          <h2 className="text-2xl font-bold text-slate-100">Evaluation & Benchmark Suite</h2>
          <p className="text-xs text-slate-400">
            Systematic benchmark metrics evaluating task completion, latency, tool selection accuracy, and LLM cost.
          </p>
        </div>
      </div>

      {/* Metrics Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        {metrics.map((m, i) => {
          const Icon = m.icon;
          return (
            <div key={i} className="glass-panel p-5 rounded-2xl border border-slate-800">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs text-slate-400 font-medium">{m.label}</span>
                <Icon className={`w-4 h-4 ${m.color}`} />
              </div>
              <p className={`text-2xl font-bold ${m.color}`}>{m.value}</p>
            </div>
          );
        })}
      </div>

      {/* Benchmark Tasks Table */}
      <div className="glass-panel rounded-2xl p-6 border border-slate-800">
        <h3 className="font-semibold text-lg text-slate-100 mb-4">Benchmark Tasks Execution Results</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-left font-mono text-xs">
            <thead className="border-b border-slate-800 text-slate-400 uppercase tracking-wider">
              <tr>
                <th className="pb-3 px-3">Task ID</th>
                <th className="pb-3 px-3">Category</th>
                <th className="pb-3 px-3">Task Name</th>
                <th className="pb-3 px-3">Status</th>
                <th className="pb-3 px-3">Latency</th>
                <th className="pb-3 px-3">Cost</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {tasks.map((t, idx) => (
                <tr key={idx} className="hover:bg-slate-900/40 transition-colors">
                  <td className="py-3 px-3 text-cyan-400">{t.id}</td>
                  <td className="py-3 px-3 text-slate-300">{t.category}</td>
                  <td className="py-3 px-3 text-slate-100 font-sans font-medium">{t.name}</td>
                  <td className="py-3 px-3">
                    <span className="px-2 py-0.5 rounded text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 font-bold">
                      {t.result}
                    </span>
                  </td>
                  <td className="py-3 px-3 text-slate-400">{t.latency}</td>
                  <td className="py-3 px-3 text-violet-400">{t.cost}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
