import React, { useState } from 'react';
import { Search, Loader2, AlertCircle, ShieldCheck, Zap, BarChart3 } from 'lucide-react';
import api from '../lib/api';
import { cn } from '../lib/utils';
import { motion } from 'framer-motion';

interface AnalysisResult {
  sensitive_findings: string[];
  critical_functions: string[];
  complexity: {
    lines_of_code: number;
    function_count: number;
    variable_count: number;
  };
  recommended_level: string;
  reasons: string[];
  ai_explanation?: string;
}

const AIAnalysis = () => {
  const [code, setCode] = useState('');
  const [analyzing, setAnalyzing] = useState(false);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleAnalyze = async () => {
    if (!code.trim()) return;
    setAnalyzing(true);
    setError(null);
    try {
      const response = await api.post('/ai/analyze', { code });
      setResult(response.data);
    } catch (err: any) {
      setError(err.response?.data?.error || 'Analysis failed');
    } finally {
      setAnalyzing(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto pt-24 px-6 pb-12">
      <header className="mb-12">
        <h1 className="text-4xl font-bold tracking-tight mb-2">Smart AI Analysis</h1>
        <p className="text-muted-foreground">Detect sensitive patterns and get obfuscation recommendations.</p>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Input Section */}
        <div className="space-y-4">
          <div className="bg-card border border-border rounded-2xl overflow-hidden">
            <div className="px-4 py-2 border-b border-border bg-secondary/50 flex items-center justify-between">
              <span className="text-xs font-mono text-muted-foreground">source_code.py</span>
              <span className="text-xs text-muted-foreground">{code.length} characters</span>
            </div>
            <textarea
              value={code}
              onChange={(e) => setCode(e.target.value)}
              placeholder="Paste your code here..."
              className="w-full h-[400px] bg-transparent p-4 font-mono text-sm outline-none resize-none"
            />
          </div>
          <button
            onClick={handleAnalyze}
            disabled={analyzing || !code.trim()}
            className="w-full bg-white text-black font-bold py-3 rounded-xl hover:bg-neutral-200 transition-all flex items-center justify-center gap-2 disabled:opacity-50"
          >
            {analyzing ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Analyzing...
              </>
            ) : (
              <>
                <Search className="w-5 h-5" />
                Run Analysis
              </>
            )}
          </button>
          {error && (
            <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-xl flex items-center gap-3 text-red-500 text-sm">
              <AlertCircle className="w-4 h-4 shrink-0" />
              {error}
            </div>
          )}
        </div>

        {/* Results Section */}
        <div className="space-y-6">
          {!result && !analyzing && (
            <div className="h-full flex flex-col items-center justify-center text-center p-12 border-2 border-dashed border-border rounded-2xl opacity-50">
              <BarChart3 className="w-12 h-12 mb-4" />
              <p className="text-sm">Results will appear here after analysis</p>
            </div>
          )}

          {analyzing && (
            <div className="space-y-4 animate-pulse">
              <div className="h-32 bg-secondary rounded-2xl" />
              <div className="h-64 bg-secondary rounded-2xl" />
            </div>
          )}

          {result && (
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              className="space-y-6"
            >
              {/* Recommendation Card */}
              <div className="bg-white text-black p-6 rounded-2xl shadow-xl">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-bold uppercase tracking-wider">Recommendation</h3>
                  <div className={cn(
                    "px-3 py-1 rounded-full text-xs font-black uppercase",
                    result.recommended_level === 'high' ? "bg-red-500 text-white" : "bg-black text-white"
                  )}>
                    {result.recommended_level} Protection
                  </div>
                </div>
                <ul className="space-y-2">
                  {result.reasons.map((reason, i) => (
                    <li key={i} className="text-sm flex items-start gap-2">
                      <Zap className="w-4 h-4 mt-0.5 shrink-0" />
                      {reason}
                    </li>
                  ))}
                </ul>
              </div>

              {/* Metrics Grid */}
              <div className="grid grid-cols-3 gap-4">
                <div className="bg-card border border-border p-4 rounded-xl text-center">
                  <p className="text-xs text-muted-foreground uppercase mb-1">LOC</p>
                  <p className="text-xl font-bold font-mono">{result.complexity.lines_of_code}</p>
                </div>
                <div className="bg-card border border-border p-4 rounded-xl text-center">
                  <p className="text-xs text-muted-foreground uppercase mb-1">Functions</p>
                  <p className="text-xl font-bold font-mono">{result.complexity.function_count}</p>
                </div>
                <div className="bg-card border border-border p-4 rounded-xl text-center">
                  <p className="text-xs text-muted-foreground uppercase mb-1">Variables</p>
                  <p className="text-xl font-bold font-mono">{result.complexity.variable_count}</p>
                </div>
              </div>

              {/* Findings */}
              <div className="space-y-4">
                {result.sensitive_findings.length > 0 && (
                  <div className="bg-red-500/10 border border-red-500/20 p-4 rounded-xl">
                    <h4 className="text-sm font-bold text-red-500 mb-2 flex items-center gap-2">
                      <AlertCircle className="w-4 h-4" />
                      Sensitive Data Detected
                    </h4>
                    <ul className="text-xs space-y-1 text-red-400">
                      {result.sensitive_findings.map((f, i) => <li key={i}>{f}</li>)}
                    </ul>
                  </div>
                )}

                {result.critical_functions.length > 0 && (
                  <div className="bg-blue-500/10 border border-blue-500/20 p-4 rounded-xl">
                    <h4 className="text-sm font-bold text-blue-400 mb-2 flex items-center gap-2">
                      <ShieldCheck className="w-4 h-4" />
                      Critical Logic Identified
                    </h4>
                    <ul className="text-xs space-y-1 text-blue-300">
                      {result.critical_functions.map((f, i) => <li key={i}>{f}</li>)}
                    </ul>
                  </div>
                )}
              </div>

              {/* AI Explanation */}
              {result.ai_explanation && (
                <div className="bg-card border border-border p-6 rounded-2xl">
                  <h4 className="text-sm font-bold mb-4 uppercase tracking-widest text-muted-foreground">AI Risk Assessment</h4>
                  <div className="text-sm text-muted-foreground leading-relaxed whitespace-pre-wrap">
                    {result.ai_explanation}
                  </div>
                </div>
              )}
            </motion.div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AIAnalysis;
