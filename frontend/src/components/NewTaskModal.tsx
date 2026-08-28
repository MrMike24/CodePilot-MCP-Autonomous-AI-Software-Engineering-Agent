import React, { useState } from 'react';
import { Play, Bug, FileCode, Zap } from 'lucide-react';

interface NewTaskModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (task: { title: string; description: string; branch: string }) => void;
}

export const NewTaskModal: React.FC<NewTaskModalProps> = ({ isOpen, onClose, onSubmit }) => {
  const [title, setTitle] = useState('Fix HTTP 500 when email is empty in FastAPI user route');
  const [description, setDescription] = useState(
    'Fix the bug where the API returns HTTP 500 when the user submits an empty email address. Add regression tests.'
  );
  const [branch, setBranch] = useState('main');

  const presets = [
    {
      label: 'Fix Email Bug',
      title: 'Fix HTTP 500 when email is empty in FastAPI user route',
      desc: 'Fix the bug where the API returns HTTP 500 when the user submits an empty email address. Add regression tests.',
      icon: Bug,
    },
    {
      label: 'Generate Test Suite',
      title: 'Generate test suite for user creation duplicate username validation',
      desc: 'Add unit tests verifying unique username constraint behavior. Duplicate usernames return HTTP 400 Bad Request.',
      icon: FileCode,
    },
    {
      label: 'Refactor Validator',
      title: 'Extract user payload validator into helper module',
      desc: 'Extract validation logic from route handler into app/validators.py.',
      icon: Zap,
    },
  ];

  if (!isOpen) return null;

  return (
    <div className="modal-overlay">
      <div className="modal-card">
        {/* Header */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderBottom: '1px solid #1f2937', paddingBottom: 12, marginBottom: 16 }}>
          <h3 style={{ margin: 0, fontSize: 15, fontWeight: 700, color: '#f9fafb' }}>Create Autonomous Engineering Task</h3>
          <button
            onClick={onClose}
            style={{ background: 'none', border: 'none', color: '#9ca3af', cursor: 'pointer', fontSize: 16 }}
            aria-label="Close modal"
          >
            ✕
          </button>
        </div>

        {/* Responsive Quick 1-Click Task Presets */}
        <div style={{ marginBottom: 16 }}>
          <label className="form-label" style={{ fontSize: 10, textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 8 }}>
            Quick 1-Click Task Presets
          </label>
          <div className="preset-grid">
            {presets.map((p, idx) => {
              const Icon = p.icon;
              return (
                <button
                  key={idx}
                  type="button"
                  onClick={() => {
                    setTitle(p.title);
                    setDescription(p.desc);
                  }}
                  className="preset-card"
                >
                  <div className="preset-header">
                    <span className="preset-title">{p.label}</span>
                    <Icon style={{ width: 14, height: 14, color: '#3b82f6', flexShrink: 0 }} />
                  </div>
                  <div className="preset-desc">{p.desc}</div>
                </button>
              );
            })}
          </div>
        </div>

        {/* Task Form */}
        <form
          onSubmit={(e) => {
            e.preventDefault();
            onSubmit({ title, description, branch });
            onClose();
          }}
        >
          <div className="form-group">
            <label className="form-label">Task Title</label>
            <input
              type="text"
              required
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="form-input"
            />
          </div>

          <div className="form-group">
            <label className="form-label">Issue Description & Requirements</label>
            <textarea
              required
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={3}
              className="form-textarea"
            />
          </div>

          <div className="form-group">
            <label className="form-label font-mono">Target Git Branch</label>
            <input
              type="text"
              value={branch}
              onChange={(e) => setBranch(e.target.value)}
              className="form-input font-mono"
            />
          </div>

          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: 12, borderTop: '1px solid #1f2937', paddingTop: 16, marginTop: 16 }}>
            <button type="button" onClick={onClose} className="btn-secondary">
              Cancel
            </button>
            <button type="submit" className="btn-primary">
              <Play style={{ width: 14, height: 14 }} />
              <span>Launch Agent</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
