import React from 'react';
import { ShieldCheck, CheckCircle2, AlertTriangle, FileCode } from 'lucide-react';

interface ReviewerScorecardProps {
  review?: any;
}

export const ReviewerScorecard: React.FC<ReviewerScorecardProps> = ({ review }) => {
  const isApproved = review?.approved ?? false;
  const confidencePercent = review?.confidence ? Math.round(review.confidence * 100) : 0;
  const severity = review?.severity || 'LOW';
  const testsStatus = review?.tests_status || 'UNKNOWN';

  const metrics = [
    { label: 'Review Decision', value: review ? (isApproved ? 'APPROVED' : 'CHANGES_REQUIRED') : 'PENDING', status: isApproved ? 'pass' : 'warn' },
    { label: 'Model Confidence', value: review ? `${confidencePercent}%` : '—', status: 'pass' },
    { label: 'Risk Severity', value: review ? severity : '—', status: 'pass' },
    { label: 'Tests Gate', value: review ? testsStatus : '—', status: 'pass' },
    { label: 'Human Gate', value: isApproved ? 'READY' : 'PENDING', status: 'pass' },
  ];

  const recommendations = review?.recommendations || [];

  return (
    <div className="panel p-5 space-y-4">
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div className="flex items-center gap-2">
          <ShieldCheck className="w-4 h-4 text-emerald-400" />
          <h3 className="font-bold text-sm text-slate-100 uppercase tracking-wider">
            Reviewer Agent Quality Scorecard
          </h3>
        </div>
        {review ? (
          <span className={`text-xs font-mono font-bold px-2.5 py-0.5 rounded border ${isApproved ? 'text-emerald-400 bg-emerald-950/40 border-emerald-500/30' : 'text-amber-400 bg-amber-950/40 border-amber-500/30'}`}>
            {isApproved ? `APPROVED (${confidencePercent}%)` : `CHANGES REQUIRED (${confidencePercent}%)`}
          </span>
        ) : (
          <span className="text-xs font-mono text-slate-400 bg-slate-900 px-2.5 py-0.5 rounded border border-slate-800">
            Awaiting Review Stage
          </span>
        )}
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
        {metrics.map((m, idx) => (
          <div key={idx} className="bg-slate-950 p-3 rounded border border-slate-800/80">
            <span className="text-[10px] uppercase font-bold text-slate-400">{m.label}</span>
            <p className="text-sm font-bold text-slate-100 font-mono mt-1">{m.value}</p>
          </div>
        ))}
      </div>

      {/* Reviewer Findings & Recommendations */}
      <div className="space-y-2 pt-2">
        <span className="text-[10px] uppercase font-bold text-slate-400">Reviewer Reasoning & Recommendations</span>
        {recommendations.length > 0 ? (
          <div className="space-y-1.5 font-mono text-xs">
            {recommendations.map((rec: string, idx: number) => (
              <div key={idx} className="flex items-start gap-2 bg-slate-950 p-2.5 rounded border border-slate-800 text-slate-300">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0 mt-0.5" />
                <span>{rec}</span>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-xs font-mono text-slate-400 p-2 bg-slate-950 rounded border border-slate-800">
            {review ? 'No additional recommendations. All quality checks satisfied.' : 'Reviewer agent will generate recommendations upon evaluating test results.'}
          </div>
        )}
      </div>
    </div>
  );
};
