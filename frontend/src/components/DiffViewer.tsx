import React from 'react';
import { ArrowRightLeft, Check, Copy, AlertCircle } from 'lucide-react';

interface DiffViewerProps {
  diffText: string;
  filesChanged?: string[];
}

export const DiffViewer: React.FC<DiffViewerProps> = ({ diffText, filesChanged = [] }) => {
  const [copied, setCopied] = React.useState(false);

  const hasDiff = diffText && diffText.trim().length > 0;

  const handleCopy = () => {
    if (!hasDiff) return;
    navigator.clipboard.writeText(diffText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const addedLines = hasDiff ? (diffText.match(/^\+[^+]/gm) || []).length : 0;
  const removedLines = hasDiff ? (diffText.match(/^-[^-]/gm) || []).length : 0;

  return (
    <div className="panel">
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderBottom: '1px solid #1f2937', paddingBottom: 12, marginBottom: 16 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <ArrowRightLeft style={{ width: 16, height: 16, color: '#10b981' }} />
          <h3 style={{ margin: 0, fontSize: 12, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em', color: '#f9fafb' }}>
            PROPOSED CODE DIFF
          </h3>
        </div>

        {hasDiff && (
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, fontFamily: 'JetBrains Mono, monospace', fontSize: 12 }}>
            <span style={{ color: '#9ca3af' }}>Files changed: {filesChanged.length || 2}</span>
            <span style={{ color: '#34d399', fontWeight: 700 }}>+{addedLines}</span>
            <span style={{ color: '#f87171', fontWeight: 700 }}>-{removedLines}</span>
            <button
              onClick={handleCopy}
              className="btn-secondary"
              style={{ padding: '2px 8px', fontSize: 11 }}
              title="Copy diff to clipboard"
            >
              {copied ? <Check style={{ width: 12, height: 12, color: '#10b981' }} /> : <Copy style={{ width: 12, height: 12 }} />}
            </button>
          </div>
        )}
      </div>

      {/* Code Viewer Container */}
      {!hasDiff ? (
        <div style={{ padding: 32, textAlign: 'center', backgroundColor: '#040711', border: '1px solid #1f2937', borderRadius: 6, color: '#9ca3af', fontFamily: 'JetBrains Mono, monospace', fontSize: 12, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 8 }}>
          <AlertCircle style={{ width: 24, height: 24, color: '#6b7280' }} />
          <span>No code changes detected</span>
        </div>
      ) : (
        <div className="diff-container">
          <pre style={{ margin: 0 }}>
            {diffText.split('\n').map((line, idx) => {
              let className = '';
              if (line.startsWith('+') && !line.startsWith('+++')) {
                className = 'diff-line-add';
              } else if (line.startsWith('-') && !line.startsWith('---')) {
                className = 'diff-line-del';
              } else if (line.startsWith('@@')) {
                className = 'diff-line-header';
              } else if (line.startsWith('diff --git')) {
                return (
                  <div key={idx} style={{ color: '#f9fafb', fontWeight: 700, borderBottom: '1px solid #1f2937', paddingBottom: 4, marginTop: 8, marginBottom: 4 }}>
                    {line}
                  </div>
                );
              }

              return (
                <div key={idx} className={className}>
                  {line}
                </div>
              );
            })}
          </pre>
        </div>
      )}
    </div>
  );
};
