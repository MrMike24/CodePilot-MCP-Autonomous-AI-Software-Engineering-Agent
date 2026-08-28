import React from 'react';
import { ShieldCheck, Lock, HardDrive, Terminal, UserCheck, KeyRound, CheckCircle2 } from 'lucide-react';

export const SecurityView: React.FC = () => {
  const securityItems = [
    {
      title: 'Path Traversal Protection',
      status: 'Protected',
      desc: 'Strict path canonicalization prevents workspace escaping (../).',
      icon: HardDrive,
    },
    {
      title: 'Secret File Exclusion',
      status: 'Protected',
      desc: 'Access to .env, .git, and credentials files is blocked at MCP layer.',
      icon: Lock,
    },
    {
      title: 'Role-Based Access Control (RBAC)',
      status: 'Enforced',
      desc: 'Tool authorization gating by role (developer, reviewer, admin).',
      icon: UserCheck,
    },
    {
      title: 'Docker Execution Sandbox',
      status: 'Verified',
      desc: 'Code execution isolated in containers with CPU/memory/timeout limits.',
      icon: Terminal,
    },
    {
      title: 'Host System Access',
      status: 'Restricted',
      desc: 'Arbitrary host command execution and root container access disabled.',
      icon: ShieldCheck,
    },
  ];

  return (
    <div className="p-6 max-w-[1600px] mx-auto space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-xl font-bold text-slate-100 flex items-center gap-2">
          <ShieldCheck className="w-5 h-5 text-emerald-400" />
          Security Architecture & Compliance Status
        </h2>
        <p className="text-xs text-slate-400">
          First-class security controls protecting host infrastructure and sensitive credentials
        </p>
      </div>

      {/* Security Status Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {securityItems.map((item, idx) => {
          const Icon = item.icon;
          return (
            <div key={idx} className="panel p-5 space-y-3">
              <div className="flex items-center justify-between">
                <div className="p-2 bg-slate-900 rounded-lg text-emerald-400 border border-slate-800">
                  <Icon className="w-5 h-5" />
                </div>
                <span className="px-2.5 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-emerald-950/40 text-emerald-400 border border-emerald-500/30">
                  ✓ {item.status}
                </span>
              </div>

              <div>
                <h3 className="font-bold text-sm text-slate-100">{item.title}</h3>
                <p className="text-xs text-slate-400 mt-1 leading-relaxed">{item.desc}</p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
