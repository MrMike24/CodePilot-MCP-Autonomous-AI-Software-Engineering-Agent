import React from 'react';
import { Database, FileCode, Layers, Search, CheckCircle2, Cpu } from 'lucide-react';

export const CodeRAGView: React.FC = () => {
  const metadata = {
    repository: 'demo_repository',
    filesIndexed: 42,
    chunksCreated: 318,
    vectorStore: 'Qdrant',
    embeddingDimension: 1536,
    lastIndexTime: new Date().toISOString().replace('T', ' ').slice(0, 19),
  };

  const recentRetrievals = [
    { query: 'FastAPI user email validation bug', file: 'demo_repository/app/main.py', score: 0.91, symbol: 'create_user', lineRange: 'L18-L32' },
    { query: 'FastAPI user email validation bug', file: 'demo_repository/tests/test_api.py', score: 0.87, symbol: 'test_create_user_success', lineRange: 'L10-L16' },
    { query: 'User pydantic schema validation', file: 'demo_repository/app/models.py', score: 0.82, symbol: 'UserCreate', lineRange: 'L4-L8' },
  ];

  return (
    <div className="p-6 max-w-[1600px] mx-auto space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-xl font-bold text-slate-100 flex items-center gap-2">
          <Database className="w-5 h-5 text-blue-400" />
          Code-Aware RAG Engine Dashboard
        </h2>
        <p className="text-xs text-slate-400">
          AST-aware Python code chunking, vector embedding indexing, and Qdrant hybrid retrieval
        </p>
      </div>

      {/* Metadata Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        <div className="panel p-4">
          <span className="text-[10px] uppercase font-bold text-slate-400">Target Repository</span>
          <p className="text-lg font-bold text-slate-100 font-mono mt-1">{metadata.repository}</p>
        </div>
        <div className="panel p-4">
          <span className="text-[10px] uppercase font-bold text-slate-400">Files Indexed</span>
          <p className="text-lg font-bold text-blue-400 font-mono mt-1">{metadata.filesIndexed}</p>
        </div>
        <div className="panel p-4">
          <span className="text-[10px] uppercase font-bold text-slate-400">AST Code Chunks</span>
          <p className="text-lg font-bold text-emerald-400 font-mono mt-1">{metadata.chunksCreated}</p>
        </div>
        <div className="panel p-4">
          <span className="text-[10px] uppercase font-bold text-slate-400">Vector Store</span>
          <p className="text-lg font-bold text-purple-400 font-mono mt-1">{metadata.vectorStore}</p>
        </div>
        <div className="panel p-4">
          <span className="text-[10px] uppercase font-bold text-slate-400">Embedding Dimension</span>
          <p className="text-lg font-bold text-slate-300 font-mono mt-1">{metadata.embeddingDimension} D</p>
        </div>
      </div>

      {/* Retrieval Activity Table */}
      <div className="panel overflow-hidden">
        <div className="p-4 border-b border-slate-800 flex items-center justify-between">
          <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
            <Search className="w-4 h-4 text-blue-400" />
            Hybrid Retrieval Activity & Relevance Scores
          </h3>
          <span className="text-xs text-slate-400 font-mono">Last indexed: {metadata.lastIndexTime}</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left font-mono text-xs">
            <thead className="bg-slate-900/80 text-slate-400 uppercase tracking-wider border-b border-slate-800">
              <tr>
                <th className="py-3 px-4">Search Query</th>
                <th className="py-3 px-4">Retrieved File Path</th>
                <th className="py-3 px-4">Symbol Name</th>
                <th className="py-3 px-4">Line Range</th>
                <th className="py-3 px-4">Similarity Score</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/80">
              {recentRetrievals.map((r, idx) => (
                <tr key={idx} className="hover:bg-slate-900/40 transition-colors">
                  <td className="py-3 px-4 text-slate-200">{r.query}</td>
                  <td className="py-3 px-4 text-blue-400 font-bold">{r.file}</td>
                  <td className="py-3 px-4 text-emerald-400">{r.symbol}</td>
                  <td className="py-3 px-4 text-slate-400">{r.lineRange}</td>
                  <td className="py-3 px-4">
                    <span className="px-2.5 py-0.5 rounded text-emerald-400 bg-emerald-950/40 border border-emerald-500/30 font-bold">
                      {(r.score * 100).toFixed(0)}% ({r.score})
                    </span>
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
