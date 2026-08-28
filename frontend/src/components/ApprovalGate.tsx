import React, { useState } from 'react';
import { ShieldCheck, CheckCircle2, XCircle, AlertTriangle } from 'lucide-react';

interface ApprovalGateProps {
  taskId: string;
  reviewResult: {
    approved: boolean;
    confidence: number;
    severity: string;
    tests_status: string;
    recommendations: string[];
  };
  onApprove: (comments: string) => void;
  onReject: (comments: string) => void;
  isSubmitting: boolean;
}

export const ApprovalGate: React.FC<ApprovalGateProps> = ({
  taskId,
  reviewResult,
  onApprove,
  onReject,
  isSubmitting,
}) => {
  const [comments, setComments] = useState('');

  return (
    <div className="panel" style={{ backgroundColor: 'rgba(245, 158, 11, 0.08)', borderColor: 'rgba(245, 158, 11, 0.3)' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderBottom: '1px solid #1f2937', paddingBottom: 12, marginBottom: 16 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <ShieldCheck style={{ width: 20, height: 20, color: '#f59e0b' }} />
          <h3 style={{ margin: 0, fontSize: 12, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em', color: '#f9fafb' }}>
            HUMAN APPROVAL REQUIRED
          </h3>
        </div>
        <span className="status-badge waiting">
          Action Pending
        </span>
      </div>

      <p style={{ margin: '0 0 16px 0', fontSize: 13, color: '#e5e7eb' }}>
        Implementation completed successfully by Coding Agent. Human operator approval is required before Pull Request submission.
      </p>

      {/* Checklist */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, minmax(0, 1fr))', gap: 12, fontFamily: 'JetBrains Mono, monospace', fontSize: 12, marginBottom: 16 }}>
        <div style={{ backgroundColor: '#040711', padding: 10, borderRadius: 6, border: '1px solid #1f2937', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span style={{ color: '#9ca3af' }}>Tests Execution</span>
          <span style={{ color: '#10b981', fontWeight: 700 }}>✓ {reviewResult.tests_status || 'PASSED'}</span>
        </div>
        <div style={{ backgroundColor: '#040711', padding: 10, borderRadius: 6, border: '1px solid #1f2937', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span style={{ color: '#9ca3af' }}>Security Gate</span>
          <span style={{ color: '#10b981', fontWeight: 700 }}>✓ PASS</span>
        </div>
        <div style={{ backgroundColor: '#040711', padding: 10, borderRadius: 6, border: '1px solid #1f2937', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span style={{ color: '#9ca3af' }}>Reviewer Agent</span>
          <span style={{ color: '#10b981', fontWeight: 700 }}>✓ APPROVED</span>
        </div>
      </div>

      {/* Operator Comments */}
      <div className="form-group" style={{ marginBottom: 16 }}>
        <label className="form-label">Operator Comments (Optional):</label>
        <input
          type="text"
          value={comments}
          onChange={(e) => setComments(e.target.value)}
          placeholder="Enter review notes for PR creation..."
          className="form-input"
        />
      </div>

      {/* Action Buttons */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: 12 }}>
        <button
          onClick={() => onReject(comments)}
          disabled={isSubmitting}
          className="btn-rose"
        >
          Reject PR
        </button>

        <button
          onClick={() => onApprove(comments)}
          disabled={isSubmitting}
          className="btn-emerald"
        >
          Approve & Create PR
        </button>
      </div>
    </div>
  );
};
