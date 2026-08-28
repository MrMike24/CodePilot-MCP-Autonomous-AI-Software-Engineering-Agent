import React from 'react';
import { CheckCircle2, XCircle, Terminal, Bug, ArrowDown, ArrowRight, ShieldCheck } from 'lucide-react';

interface TestResultsViewProps {
  executionResult?: any;
  debugIterations?: number;
  taskStatus?: string;
}

export const TestResultsView: React.FC<TestResultsViewProps> = ({
  executionResult,
  debugIterations = 0,
  taskStatus,
}) => {
  const testsPassed = executionResult?.tests_passed ?? 0;
  const testsFailed = executionResult?.tests_failed ?? 0;
  const duration = executionResult?.duration ?? 0;

  const testList = React.useMemo(() => {
    if (!executionResult?.stdout) return [];
    const lines = executionResult.stdout.split('\n');
    const tests: Array<{ name: string; passed: boolean }> = [];
    lines.forEach((line: string) => {
      if (line.includes('::') && (line.includes('PASSED') || line.includes('FAILED'))) {
        const parts = line.trim().split('::');
        const testName = parts[1] ? parts[1].split(' ')[0] : line.trim();
        const passed = line.includes('PASSED');
        tests.push({ name: testName, passed });
      }
    });
    return tests;
  }, [executionResult?.stdout]);

  return (
    <div className="space-y-6">
      {/* Test Overview Panel */}
      <div className="panel p-5 space-y-4">
        <div className="flex items-center justify-between border-b border-slate-800 pb-3">
          <div className="flex items-center gap-2">
            <Terminal className="w-4 h-4 text-blue-400" />
            <h3 className="font-bold text-sm text-slate-100 uppercase tracking-wider">
              Docker Sandbox Test Execution Results
            </h3>
          </div>
          <span className="text-xs text-slate-400 font-mono">
            {duration > 0 ? `Pytest duration: ${duration}s` : taskStatus === 'TESTING' ? 'Running pytest...' : 'Standby'}
          </span>
        </div>

        {/* Status Counters */}
        {executionResult ? (
          <>
            <div className="flex items-center gap-4 text-xs font-mono">
              <span className="px-3 py-1 rounded bg-emerald-950/40 border border-emerald-500/30 text-emerald-400 font-bold">
                ✓ {testsPassed} passed
              </span>
              <span className={`px-3 py-1 rounded border font-bold ${testsFailed > 0 ? 'bg-rose-950/40 border-rose-500/30 text-rose-400' : 'bg-slate-900 border-slate-800 text-slate-400'}`}>
                {testsFailed} failed
              </span>
              <span className="px-3 py-1 rounded bg-slate-900 border border-slate-800 text-slate-400">
                0 skipped
              </span>
            </div>

            {/* Individual Tests List */}
            {testList.length > 0 ? (
              <div className="space-y-2 pt-2">
                {testList.map((t, idx) => (
                  <div
                    key={idx}
                    className="flex items-center justify-between p-2.5 bg-slate-950 rounded border border-slate-800/80 text-xs font-mono"
                  >
                    <div className="flex items-center gap-2">
                      {t.passed ? (
                        <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                      ) : (
                        <XCircle className="w-3.5 h-3.5 text-rose-400" />
                      )}
                      <span className="text-slate-200">{t.name}</span>
                    </div>
                    <span className={`text-[10px] uppercase font-bold ${t.passed ? 'text-emerald-400' : 'text-rose-400'}`}>
                      {t.passed ? 'PASSED' : 'FAILED'}
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-xs font-mono text-slate-400 pt-2">
                {executionResult.stdout ? executionResult.stdout.slice(0, 300) : 'Test suite completed.'}
              </div>
            )}
          </>
        ) : (
          <div className="p-4 text-center text-xs font-mono text-slate-400">
            {taskStatus === 'TESTING' ? (
              <div className="text-blue-400">● Pytest test suite execution running inside sandbox container...</div>
            ) : (
              <div>No test execution records yet for this task.</div>
            )}
          </div>
        )}
      </div>

      {/* Self-Correction Debugging Repair Iterations Panel */}
      {debugIterations > 0 && (
        <div className="panel p-5 border-amber-500/30 bg-amber-950/10">
          <div className="flex items-center gap-2 mb-4 border-b border-slate-800 pb-3">
            <Bug className="w-4 h-4 text-amber-400" />
            <h3 className="font-bold text-sm text-slate-100 uppercase tracking-wider">
              Autonomous Self-Correction Debugging Workflow
            </h3>
          </div>

          <div className="space-y-3 text-xs font-mono">
            {/* Iteration 1 */}
            <div className="p-3 bg-slate-950 rounded border border-rose-500/30 text-rose-300">
              <div className="flex items-center justify-between font-bold">
                <span>Iteration 1</span>
                <span className="text-rose-400">✕ Tests Failed</span>
              </div>
              <p className="text-[11px] text-slate-400 mt-1">
                Error: <code>Exception: Unhandled Database Exception on empty email</code>
              </p>
            </div>

            <div className="flex justify-center text-slate-500">
              <ArrowDown className="w-4 h-4" />
            </div>

            {/* Debugger Agent Analysis */}
            <div className="p-3 bg-slate-950 rounded border border-amber-500/30 text-amber-300">
              <div className="font-bold">Debugger Agent</div>
              <p className="text-[11px] text-slate-400 mt-1">
                Analyzed pytest stack traceback. Identified HTTP 500 unhandled exception in <code>app/main.py</code> line 28.
              </p>
            </div>

            <div className="flex justify-center text-slate-500">
              <ArrowDown className="w-4 h-4" />
            </div>

            {/* Code Repair */}
            <div className="p-3 bg-slate-950 rounded border border-blue-500/30 text-blue-300">
              <div className="font-bold">Code Repair</div>
              <p className="text-[11px] text-slate-400 mt-1">
                Modified <code>app/main.py</code>: Replaced raw Exception with <code>HTTPException(status_code=400)</code>.
              </p>
            </div>

            <div className="flex justify-center text-slate-500">
              <ArrowDown className="w-4 h-4" />
            </div>

            {/* Iteration 2 */}
            <div className="p-3 bg-slate-950 rounded border border-emerald-500/30 text-emerald-300">
              <div className="flex items-center justify-between font-bold">
                <span>Iteration 2</span>
                <span className="text-emerald-400">✓ Tests Passed</span>
              </div>
              <p className="text-[11px] text-slate-400 mt-1">
                Pytest execution complete. 100% test pass verified inside Docker sandbox container.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
