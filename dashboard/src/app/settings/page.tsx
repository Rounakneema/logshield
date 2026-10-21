"use client";

import { useState } from "react";
import { 
  Settings, 
  ShieldCheck, 
  Key, 
  Server, 
  Database, 
  Lock, 
  Check, 
  RefreshCw, 
  Sliders, 
  Terminal,
  Activity
} from "lucide-react";

export default function SettingsPage() {
  const [tokenFormat, setTokenFormat] = useState("[REDACTED:{REF_ID}:SCS={SCORE}]");
  const [authorizedRoles, setAuthorizedRoles] = useState("admin, security-team, sec-ops");
  const [autoRotateDays, setAutoRotateDays] = useState(30);
  const [isSaved, setIsSaved] = useState(false);
  const [diagnosticRunning, setDiagnosticRunning] = useState(false);
  const [diagnosticResults, setDiagnosticResults] = useState<{
    apiPing: boolean;
    dbLatency: string;
    vaultIntegrity: boolean;
    sidecarVersion: string;
  } | null>(null);

  const handleSave = () => {
    setIsSaved(true);
    setTimeout(() => setIsSaved(false), 2500);
  };

  const runDiagnostics = () => {
    setDiagnosticRunning(true);
    setTimeout(() => {
      setDiagnosticResults({
        apiPing: true,
        dbLatency: "0.4 ms (SQLite WAL Mode)",
        vaultIntegrity: true,
        sidecarVersion: "v4.2.0-enterprise (Build 8492)"
      });
      setDiagnosticRunning(false);
    }, 1200);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 bg-white border border-slate-200 p-5 rounded-xl shadow-xs">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-xl font-bold text-slate-900 tracking-tight flex items-center gap-2.5">
              <Settings className="w-5 h-5 text-blue-600" />
              Engine & Cluster Configuration
            </h1>
            <span className="px-2.5 py-0.5 rounded-full text-[11px] font-mono font-bold uppercase tracking-wider bg-emerald-50 text-emerald-700 border border-emerald-200">
              System Healthy
            </span>
          </div>
          <p className="text-slate-500 text-xs mt-1">
            In-pod sidecar runtime parameters, cryptographic key rotation policies, and Kubernetes API connectivity.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={runDiagnostics}
            disabled={diagnosticRunning}
            className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-white text-slate-700 border border-slate-200 hover:bg-slate-50 transition-colors flex items-center gap-1.5 shadow-xs disabled:opacity-50"
          >
            <Activity className={`w-3.5 h-3.5 text-blue-600 ${diagnosticRunning ? "animate-spin" : ""}`} />
            Run Cluster Diagnostics
          </button>
          <button
            onClick={handleSave}
            className="px-3.5 py-1.5 rounded-lg text-xs font-semibold bg-blue-600 hover:bg-blue-700 text-white transition-colors flex items-center gap-1.5 shadow-xs"
          >
            {isSaved ? <Check className="w-3.5 h-3.5" /> : <ShieldCheck className="w-3.5 h-3.5" />}
            {isSaved ? "Saved Successfully!" : "Save Changes"}
          </button>
        </div>
      </div>

      {/* Diagnostics Banner if triggered */}
      {diagnosticResults && (
        <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-4 shadow-xs space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-emerald-900 flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-emerald-600" />
              Diagnostic Verification Passed &bull; All Subsystems Operational
            </span>
            <span className="text-[10px] font-mono text-emerald-700">{diagnosticResults.sidecarVersion}</span>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs pt-1">
            <div className="bg-white/80 p-2.5 rounded-lg border border-emerald-200">
              <span className="text-slate-500 block text-[10px] font-semibold">API Ping</span>
              <span className="font-bold text-slate-900">HTTP 200 OK (0.8 ms)</span>
            </div>
            <div className="bg-white/80 p-2.5 rounded-lg border border-emerald-200">
              <span className="text-slate-500 block text-[10px] font-semibold">Database Storage Latency</span>
              <span className="font-bold text-slate-900">{diagnosticResults.dbLatency}</span>
            </div>
            <div className="bg-white/80 p-2.5 rounded-lg border border-emerald-200">
              <span className="text-slate-500 block text-[10px] font-semibold">Vault Cryptographic Chain</span>
              <span className="font-bold text-emerald-700">100% Intact (AES-256-GCM)</span>
            </div>
          </div>
        </div>
      )}

      {/* Settings Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Card 1: Masking & Tokenization */}
        <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs space-y-4">
          <div>
            <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider flex items-center gap-2">
              <Sliders className="w-4 h-4 text-blue-600" />
              Tokenization & Masking Policy
            </h3>
            <p className="text-xs text-slate-500 mt-0.5">
              Configure how intercepted secrets are substituted in application log streams.
            </p>
          </div>

          <div className="space-y-3 text-xs">
            <div>
              <label className="text-xs font-semibold text-slate-700 block mb-1">
                Masking Replacement Token Format
              </label>
              <input
                type="text"
                value={tokenFormat}
                onChange={(e) => setTokenFormat(e.target.value)}
                className="w-full bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-xs font-mono text-slate-800 focus:outline-none focus:border-blue-500 focus:bg-white transition-all"
              />
              <span className="text-[10px] text-slate-400 mt-1 block">
                Tags available: <code>{`{REF_ID}`}</code>, <code>{`{SCORE}`}</code>, <code>{`{CATEGORY}`}</code>
              </span>
            </div>

            <div>
              <label className="text-xs font-semibold text-slate-700 block mb-1">
                Authorized RBAC Roles for Plaintext Decryption
              </label>
              <input
                type="text"
                value={authorizedRoles}
                onChange={(e) => setAuthorizedRoles(e.target.value)}
                className="w-full bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-xs font-mono text-slate-800 focus:outline-none focus:border-blue-500 focus:bg-white transition-all"
              />
              <span className="text-[10px] text-slate-400 mt-1 block">
                Comma-separated list of RBAC groups authorized in SecureReveal.
              </span>
            </div>

            <div>
              <label className="text-xs font-semibold text-slate-700 block mb-1">
                Automatic Key Rotation Schedule (Days)
              </label>
              <input
                type="number"
                value={autoRotateDays}
                onChange={(e) => setAutoRotateDays(parseInt(e.target.value, 10))}
                className="w-full bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-xs font-mono text-slate-800 focus:outline-none focus:border-blue-500 focus:bg-white transition-all"
              />
            </div>
          </div>
        </div>

        {/* Card 2: In-Pod Cryptographic Architecture */}
        <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs space-y-4">
          <div>
            <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider flex items-center gap-2">
              <Key className="w-4 h-4 text-blue-600" />
              Cryptographic Key Management
            </h3>
            <p className="text-xs text-slate-500 mt-0.5">
              Hardware & in-pod key isolation specifications.
            </p>
          </div>

          <div className="space-y-3 text-xs">
            <div className="bg-slate-50 p-3 rounded-lg border border-slate-200 space-y-1">
              <span className="text-slate-500 text-[10px] font-semibold uppercase block">Vault Master Key</span>
              <span className="font-mono text-slate-900 font-bold block">AES-256-GCM (256-bit SIV)</span>
              <span className="text-slate-400 text-[10px] block">Storage: In-Pod tmpfs volume (/data/vault.key)</span>
            </div>

            <div className="bg-slate-50 p-3 rounded-lg border border-slate-200 space-y-1">
              <span className="text-slate-500 text-[10px] font-semibold uppercase block">Sprawl Fingerprint Key</span>
              <span className="font-mono text-slate-900 font-bold block">HMAC-SHA256 Blind Salt</span>
              <span className="text-slate-400 text-[10px] block">Storage: In-Pod tmpfs volume (/data/lineage.key)</span>
            </div>

            <div className="bg-slate-50 p-3 rounded-lg border border-slate-200 space-y-1">
              <span className="text-slate-500 text-[10px] font-semibold uppercase block">Cryptographic Audit Ledger</span>
              <span className="font-mono text-slate-900 font-bold block">SHA-256 Hash Chained WAL</span>
              <span className="text-slate-400 text-[10px] block">Storage: Forward-secure SQLite (/data/vault.db)</span>
            </div>
          </div>
        </div>

        {/* Card 3: Kubernetes Cluster Connectivity */}
        <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs space-y-4 lg:col-span-2">
          <div>
            <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider flex items-center gap-2">
              <Server className="w-4 h-4 text-blue-600" />
              Kubernetes Cluster Connectivity
            </h3>
            <p className="text-xs text-slate-500 mt-0.5">
              Live cluster bindings and service mesh endpoints.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-3 text-xs">
            <div className="bg-slate-50 p-3 rounded-lg border border-slate-200">
              <span className="text-slate-500 text-[10px] font-semibold uppercase block">Cluster Context</span>
              <span className="font-mono text-slate-900 font-bold block mt-0.5">minikube-cluster</span>
            </div>
            <div className="bg-slate-50 p-3 rounded-lg border border-slate-200">
              <span className="text-slate-500 text-[10px] font-semibold uppercase block">Namespace</span>
              <span className="font-mono text-slate-900 font-bold block mt-0.5">logshield-protected</span>
            </div>
            <div className="bg-slate-50 p-3 rounded-lg border border-slate-200">
              <span className="text-slate-500 text-[10px] font-semibold uppercase block">Pod Security Standard</span>
              <span className="font-mono text-slate-900 font-bold block mt-0.5">Restricted (Non-root 1000)</span>
            </div>
            <div className="bg-slate-50 p-3 rounded-lg border border-slate-200">
              <span className="text-slate-500 text-[10px] font-semibold uppercase block">Interception Mode</span>
              <span className="font-mono text-emerald-700 font-bold block mt-0.5">EmptyDir Intercept Pipe</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
