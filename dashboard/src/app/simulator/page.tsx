"use client";

import { useEffect, useState, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { 
  FlaskConical, 
  Play, 
  CheckCircle2, 
  AlertTriangle, 
  Layers, 
  Sliders, 
  Clock, 
  ShieldCheck, 
  Terminal, 
  Code2,
  Check,
  Zap,
  ArrowRight
} from "lucide-react";
import { simulatePipeline } from "@/lib/api";

const PRESETS = [
  {
    name: "AWS IAM Secret Key",
    desc: "Critical cloud credentials",
    category: "Cloud Provider",
    line: '2026-10-16 12:00:00 [AWS-SYNC] S3 asset sync AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY and AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE'
  },
  {
    name: "PostgreSQL Database URL",
    desc: "Production database URI with password",
    category: "Database",
    line: '2026-10-16 12:00:02 DEBUG auth-service Connected to DATABASE_URL=postgres://admin:MyP@ssw0rd123@auth-db:5432/prod'
  },
  {
    name: "Stripe Secret API Key",
    desc: "Payment gateway credentials",
    category: "Payment",
    line: '2026-10-16 12:00:04 DEBUG payment-service Charging via STRIPE_SECRET_KEY=sk_test_51Mz94kLmNoPqRsTuVwXyZ0123456789'
  },
  {
    name: "JWT Bearer Token",
    desc: "Full session auth token",
    category: "Auth",
    line: '2026-10-16 12:00:08 DEBUG user-service Auth token issued Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c'
  },
  {
    name: "Safe UUID (Negative Sample)",
    desc: "High entropy hex UUID - Should PASS",
    category: "Safe/Negative",
    line: '2026-10-16 12:00:05 INFO inventory-service Querying catalog trace_id=550e8400-e29b-41d4-a716-446655440000'
  },
  {
    name: "Nginx Log (Negative Sample)",
    desc: "High volume web traffic - Fast bypass",
    category: "Safe/Negative",
    line: '192.168.1.100 - - [16/Oct/2026:12:00:00 +0000] "GET /api/v1/health HTTP/1.1" 200 48'
  },
  {
    name: "Git Commit SHA (Negative Sample)",
    desc: "40-character hex commit - Should PASS",
    category: "Safe/Negative",
    line: 'Deployed revision release_commit=4b825dc642cb6eb9a060e54bf8d69288fbee4904 cleanly to production'
  }
];

function SimulatorContent() {
  const searchParams = useSearchParams();
  const initialLine = searchParams.get("line") || PRESETS[0].line;

  const [inputLine, setInputLine] = useState(initialLine);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  const runSimulation = async (line: string) => {
    setLoading(true);
    try {
      const data = await simulatePipeline(line);
      setResult(data);
    } catch (err) {
      console.error("Simulation failed:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    runSimulation(initialLine);
  }, []);

  const selectPreset = (presetLine: string) => {
    setInputLine(presetLine);
    runSimulation(presetLine);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 bg-white border border-slate-200 p-5 rounded-xl shadow-xs">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-xl font-bold text-slate-900 tracking-tight flex items-center gap-2.5">
              <FlaskConical className="w-5 h-5 text-blue-600" />
              6-Stage Pipeline Simulator & Benchmark
            </h1>
            <span className="px-2.5 py-0.5 rounded-full text-[11px] font-mono font-bold uppercase tracking-wider bg-blue-50 text-blue-700 border border-blue-200">
              Interactive Sandbox
            </span>
          </div>
          <p className="text-slate-500 text-xs mt-1">
            Test arbitrary log lines in real-time. Inspect stage-by-stage zero-regex candidate filtering, Shannon entropy analysis, multi-factor confidence scoring, and microsecond telemetry.
          </p>
        </div>

        {result && (
          <div className="flex items-center gap-3 bg-slate-50 px-3.5 py-2 rounded-xl border border-slate-200">
            <Clock className="w-4 h-4 text-blue-600" />
            <div>
              <span className="text-[10px] text-slate-500 uppercase tracking-wider block font-semibold">Latency</span>
              <span className="font-mono text-xs font-bold text-slate-800">
                {result.latency_microseconds} µs ({result.latency_ms} ms)
              </span>
            </div>
          </div>
        )}
      </div>

      {/* Preset Quick Chips */}
      <div className="space-y-2">
        <label className="text-[11px] font-bold uppercase tracking-wider text-slate-500 flex items-center gap-1.5">
          <Sliders className="w-3.5 h-3.5 text-blue-600" />
          Test Presets (Real-World Secrets & Negative Samples)
        </label>
        <div className="flex flex-wrap gap-1.5">
          {PRESETS.map((p, idx) => {
            const isSelected = inputLine === p.line;
            const isSafe = p.category.includes("Safe");
            return (
              <button
                key={idx}
                onClick={() => selectPreset(p.line)}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all flex items-center gap-2 border ${
                  isSelected
                    ? "bg-blue-50 text-blue-700 border-blue-300 font-semibold shadow-xs"
                    : "bg-white text-slate-600 border-slate-200 hover:text-slate-900 hover:bg-slate-50"
                }`}
              >
                <span className={`w-1.5 h-1.5 rounded-full ${isSafe ? "bg-emerald-500" : "bg-amber-500"}`} />
                {p.name}
              </button>
            );
          })}
        </div>
      </div>

      {/* Input Editor & Run Button */}
      <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs space-y-4">
        <div className="flex items-center justify-between">
          <label className="text-xs font-bold uppercase tracking-wider text-slate-700 flex items-center gap-2">
            <Terminal className="w-4 h-4 text-blue-600" />
            Log Line Input
          </label>
          <span className="text-xs text-slate-400 font-mono">
            {inputLine.length} characters
          </span>
        </div>

        <textarea
          rows={3}
          value={inputLine}
          onChange={(e) => setInputLine(e.target.value)}
          placeholder="Paste or type an application log line here..."
          className="w-full bg-slate-50 border border-slate-200 rounded-xl p-3 font-mono text-xs text-slate-900 focus:outline-none focus:border-blue-500 focus:bg-white transition-all leading-relaxed"
        />

        <div className="flex items-center justify-between pt-1">
          <span className="text-xs text-slate-500">
            Pipeline processes tokens via in-pod Aho-Corasick automaton & Shannon entropy calculations.
          </span>
          <button
            onClick={() => runSimulation(inputLine)}
            disabled={loading || !inputLine.trim()}
            className="px-5 py-2 rounded-lg font-bold text-xs bg-blue-600 hover:bg-blue-700 text-white transition-all flex items-center gap-2 shadow-xs disabled:opacity-50"
          >
            {loading ? (
              <>Running Pipeline...</>
            ) : (
              <>
                <Play className="w-3.5 h-3.5 fill-white" />
                Simulate 6-Stage Pipeline
              </>
            )}
          </button>
        </div>
      </div>

      {/* Result Section */}
      {result && (
        <div className="space-y-6">
          {/* Verdict Banner */}
          <div className={`p-5 rounded-xl border flex flex-col md:flex-row justify-between items-start md:items-center gap-4 ${
            result.overall_decision === "MASK"
              ? "bg-emerald-50 border-emerald-200 text-emerald-950"
              : result.overall_decision === "FLAG"
              ? "bg-amber-50 border-amber-200 text-amber-950"
              : "bg-blue-50 border-blue-200 text-blue-950"
          }`}>
            <div className="flex items-center gap-3.5">
              <div className={`p-2.5 rounded-xl border ${
                result.overall_decision === "MASK"
                  ? "bg-emerald-100 border-emerald-300 text-emerald-700"
                  : result.overall_decision === "FLAG"
                  ? "bg-amber-100 border-amber-300 text-amber-700"
                  : "bg-blue-100 border-blue-300 text-blue-700"
              }`}>
                {result.overall_decision === "MASK" ? (
                  <ShieldCheck className="w-6 h-6" />
                ) : result.overall_decision === "FLAG" ? (
                  <AlertTriangle className="w-6 h-6" />
                ) : (
                  <CheckCircle2 className="w-6 h-6" />
                )}
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h3 className="text-base font-bold">
                    Pipeline Decision: {result.overall_decision}
                  </h3>
                  <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider ${
                    result.overall_decision === "MASK"
                      ? "bg-emerald-200 text-emerald-800"
                      : result.overall_decision === "FLAG"
                      ? "bg-amber-200 text-amber-800"
                      : "bg-blue-200 text-blue-800"
                  }`}>
                    {result.overall_decision === "MASK" ? "Redacted & Vaulted" : result.overall_decision === "FLAG" ? "Flagged for Audit" : "Clean Line Passed"}
                  </span>
                </div>
                <p className="text-xs mt-0.5 opacity-80">
                  {result.overall_decision === "MASK"
                    ? "Credential detected with calibrated confidence ≥ 70. Secret vaulted into SecureReveal AES-256-GCM repository and replaced with token."
                    : result.overall_decision === "FLAG"
                    ? "Suspicious pattern detected (SCS 40-69). Emitted with warning tag for telemetry review."
                    : "Zero credential patterns detected. Line bypassed cleanly without modification in sub-millisecond time."}
                </p>
              </div>
            </div>

            <div className="flex items-center gap-4 text-xs font-medium">
              <div className="text-right">
                <span className="text-[10px] uppercase tracking-wider block opacity-70">Tokens Scanned</span>
                <span className="font-mono font-bold text-sm">
                  {result.stages?.stage_1_preprocessor?.tokens_extracted || 0} tokens
                </span>
              </div>
            </div>
          </div>

          {/* Sanitized Stream Output Preview */}
          <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs space-y-2">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-700 flex items-center gap-2">
              <Code2 className="w-4 h-4 text-blue-600" />
              Final Output Stream Emitted to EmptyDir Volume & Fluent Bit
            </span>
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-3.5 font-mono text-xs text-emerald-400 break-all leading-relaxed">
              {result.sanitized_line}
            </div>
          </div>

          {/* 6-Stage Decomposition Flow */}
          <div className="space-y-3">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 flex items-center gap-1.5">
              <Layers className="w-4 h-4 text-blue-600" />
              6-Stage Pipeline Telemetry & Decomposition
            </h3>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {/* Stage 1 */}
              <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-xs space-y-2.5">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-slate-900 flex items-center gap-1.5">
                    <span className="w-5 h-5 rounded-md bg-blue-50 text-blue-600 border border-blue-200 flex items-center justify-center text-[10px] font-bold">1</span>
                    Preprocessor
                  </span>
                  <span className="text-[10px] text-slate-400 uppercase font-semibold">Normalize</span>
                </div>
                <p className="text-xs text-slate-500">
                  Splits into structured tokens, unwraps JSON objects, and decodes URL percent-encoding.
                </p>
                <div className="bg-slate-50 rounded-lg p-2.5 text-xs space-y-1 font-mono text-slate-700 border border-slate-100">
                  <div className="flex justify-between">
                    <span className="text-slate-500">Tokens:</span>
                    <span className="font-semibold">{result.stages.stage_1_preprocessor.tokens_extracted}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-500">JSON Wrapped:</span>
                    <span className={`font-semibold ${result.stages.stage_1_preprocessor.is_json ? "text-emerald-700" : "text-slate-500"}`}>
                      {result.stages.stage_1_preprocessor.is_json ? "YES" : "NO"}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-500">URL Decoded:</span>
                    <span>{result.stages.stage_1_preprocessor.url_decoded} values</span>
                  </div>
                </div>
              </div>

              {/* Stage 2 */}
              <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-xs space-y-2.5">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-slate-900 flex items-center gap-1.5">
                    <span className="w-5 h-5 rounded-md bg-blue-50 text-blue-600 border border-blue-200 flex items-center justify-center text-[10px] font-bold">2</span>
                    Candidate Finder
                  </span>
                  <span className="text-[10px] text-slate-400 uppercase font-semibold">Zero-Regex Exit</span>
                </div>
                <p className="text-xs text-slate-500">
                  Rapid heuristic filter that skips 90%+ of non-secret lines in &lt; 5 µs without regex invocation.
                </p>
                <div className="bg-slate-50 rounded-lg p-2.5 text-xs space-y-1 font-mono text-slate-700 border border-slate-100">
                  <div className="flex justify-between">
                    <span className="text-slate-500">Candidate Match:</span>
                    <span className={`font-bold ${result.stages.stage_2_candidate_finder.is_candidate ? "text-amber-700" : "text-emerald-700"}`}>
                      {result.stages.stage_2_candidate_finder.is_candidate ? "DETECTED" : "CLEAN"}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-500">Fast Bypass:</span>
                    <span className={`font-semibold ${result.stages.stage_2_candidate_finder.bypassed ? "text-emerald-700" : "text-slate-500"}`}>
                      {result.stages.stage_2_candidate_finder.bypassed ? "TRIGGERED (0 overhead)" : "NO"}
                    </span>
                  </div>
                </div>
              </div>

              {/* Stage 3 */}
              <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-xs space-y-2.5">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-slate-900 flex items-center gap-1.5">
                    <span className="w-5 h-5 rounded-md bg-blue-50 text-blue-600 border border-blue-200 flex items-center justify-center text-[10px] font-bold">3</span>
                    Context Engine
                  </span>
                  <span className="text-[10px] text-slate-400 uppercase font-semibold">Varnames</span>
                </div>
                <p className="text-xs text-slate-500">
                  Evaluates surrounding parameter keys (e.g. `password`, `key`, `token`) vs negative keys (`commit`, `uuid`).
                </p>
                <div className="bg-slate-50 rounded-lg p-2.5 text-xs space-y-1 font-mono text-slate-700 border border-slate-100">
                  <div className="flex justify-between">
                    <span className="text-slate-500">Engine State:</span>
                    <span className="text-blue-700 font-semibold">
                      {result.stages.stage_3_context_engine.active ? "ACTIVE EVALUATION" : "BYPASSED"}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-500">Target Type:</span>
                    <span>{result.stages.stage_2_candidate_finder.is_candidate ? "High entropy / Keyed" : "Plain log stream"}</span>
                  </div>
                </div>
              </div>

              {/* Stage 4 */}
              <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-xs space-y-2.5">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-slate-900 flex items-center gap-1.5">
                    <span className="w-5 h-5 rounded-md bg-blue-50 text-blue-600 border border-blue-200 flex items-center justify-center text-[10px] font-bold">4</span>
                    Secret Classifier
                  </span>
                  <span className="text-[10px] text-slate-400 uppercase font-semibold">Detectors</span>
                </div>
                <p className="text-xs text-slate-500">
                  Specialized detector matchers (AWS, Stripe, Database URI, Bearer, Private Keys, etc.).
                </p>
                <div className="bg-slate-50 rounded-lg p-2.5 text-xs space-y-1 font-mono text-slate-700 border border-slate-100">
                  <div className="flex justify-between">
                    <span className="text-slate-500">Matched Classifiers:</span>
                    <span className="text-blue-700 font-bold truncate max-w-[140px]">
                      {result.stages.stage_4_secret_classifier.matches.length > 0 
                        ? result.stages.stage_4_secret_classifier.matches.join(", ") 
                        : "None (Clean)"}
                    </span>
                  </div>
                </div>
              </div>

              {/* Stage 5 */}
              <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-xs space-y-2.5">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-slate-900 flex items-center gap-1.5">
                    <span className="w-5 h-5 rounded-md bg-blue-50 text-blue-600 border border-blue-200 flex items-center justify-center text-[10px] font-bold">5</span>
                    Confidence Model
                  </span>
                  <span className="text-[10px] text-slate-400 uppercase font-semibold">SCS Weights</span>
                </div>
                <p className="text-xs text-slate-500">
                  Multi-factor linear / Bayesian fusion model yielding calibrated SCS score (0 - 100).
                </p>
                <div className="bg-slate-50 rounded-lg p-2.5 text-xs space-y-1 font-mono text-slate-700 border border-slate-100">
                  <div className="flex justify-between">
                    <span className="text-slate-500">Base Weight:</span>
                    <span>{result.stages.stage_5_confidence_model.weights?.base || 0.40}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-500">Entropy Weight:</span>
                    <span>{result.stages.stage_5_confidence_model.weights?.entropy || 0.20}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-500">Varname Weight:</span>
                    <span>{result.stages.stage_5_confidence_model.weights?.varname || 0.20}</span>
                  </div>
                </div>
              </div>

              {/* Stage 6 */}
              <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-xs space-y-2.5">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-slate-900 flex items-center gap-1.5">
                    <span className="w-5 h-5 rounded-md bg-blue-50 text-blue-600 border border-blue-200 flex items-center justify-center text-[10px] font-bold">6</span>
                    Decision Gate
                  </span>
                  <span className="text-[10px] text-slate-400 uppercase font-semibold">Redact / Pass</span>
                </div>
                <p className="text-xs text-slate-500">
                  Enforces threshold policies: MASK (≥70), FLAG (40-69), PASS (&lt;40).
                </p>
                <div className="bg-slate-50 rounded-lg p-2.5 text-xs space-y-1 font-mono text-slate-700 border border-slate-100">
                  <div className="flex justify-between">
                    <span className="text-slate-500">Gate Policy:</span>
                    <span>MASK ≥ 70</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-500">Final Decision:</span>
                    <span className="font-bold text-emerald-700">
                      {result.stages.stage_6_decision_gate.decision}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Tokens Deep Dive Table */}
          {result.tokens && result.tokens.length > 0 && (
            <div className="bg-white border border-slate-200 rounded-xl overflow-hidden shadow-xs">
              <div className="p-4 border-b border-slate-200 bg-slate-50 flex items-center justify-between">
                <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider flex items-center gap-2">
                  <Sliders className="w-4 h-4 text-blue-600" />
                  Evaluated Tokens & Factor Decomposition
                </h4>
                <span className="text-xs text-slate-500">
                  {result.tokens.length} candidate token{result.tokens.length > 1 ? "s" : ""} analyzed
                </span>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead className="bg-slate-50/50 text-slate-500 uppercase font-semibold text-[11px] border-b border-slate-200">
                    <tr>
                      <th className="px-5 py-3">Token Substring</th>
                      <th className="px-5 py-3">Classifier Match</th>
                      <th className="px-5 py-3">Decision</th>
                      <th className="px-5 py-3">SCS Score</th>
                      <th className="px-5 py-3">Factor Breakdown (Entropy / Var / Context)</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100 font-mono">
                    {result.tokens.map((t: any, idx: number) => (
                      <tr key={idx} className="hover:bg-slate-50/80 transition-colors">
                        <td className="px-5 py-3 font-bold text-slate-900">
                          {t.token.length > 30 ? `${t.token.substring(0, 16)}...${t.token.substring(t.token.length - 8)}` : t.token}
                        </td>
                        <td className="px-5 py-3 text-slate-700 font-sans">
                          {t.detector_name || "Pattern Heuristic"}
                        </td>
                        <td className="px-5 py-3">
                          <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                            t.decision === "MASK"
                              ? "bg-emerald-50 text-emerald-700 border border-emerald-200"
                              : t.decision === "FLAG"
                              ? "bg-amber-50 text-amber-700 border border-amber-200"
                              : "bg-slate-100 text-slate-600 border border-slate-200"
                          }`}>
                            {t.decision}
                          </span>
                        </td>
                        <td className="px-5 py-3">
                          <div className="flex items-center gap-2">
                            <span className="font-bold text-slate-900">{t.score}</span>
                            <div className="w-16 h-1.5 bg-slate-100 rounded-full overflow-hidden">
                              <div
                                className={`h-full ${
                                  t.score >= 70 ? "bg-emerald-500" : t.score >= 40 ? "bg-amber-500" : "bg-blue-500"
                                }`}
                                style={{ width: `${Math.min(100, t.score)}%` }}
                              />
                            </div>
                          </div>
                        </td>
                        <td className="px-5 py-3 text-slate-600">
                          <div className="flex gap-2">
                            <span className="bg-slate-100 px-2 py-0.5 rounded border border-slate-200 text-[11px]">
                              H: {t.factors?.entropy !== undefined ? Number(t.factors.entropy).toFixed(2) : "N/A"}
                            </span>
                            <span className="bg-slate-100 px-2 py-0.5 rounded border border-slate-200 text-[11px]">
                              Var: {t.factors?.varname !== undefined ? t.factors.varname : "N/A"}
                            </span>
                            <span className="bg-slate-100 px-2 py-0.5 rounded border border-slate-200 text-[11px]">
                              Ctx: {t.factors?.context !== undefined ? t.factors.context : "N/A"}
                            </span>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default function SimulatorPage() {
  return (
    <Suspense fallback={<div className="text-slate-400 p-8">Loading simulator...</div>}>
      <SimulatorContent />
    </Suspense>
  );
}
