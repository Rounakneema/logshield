"use client";

import { useState } from "react";
import { 
  FileText, 
  ShieldCheck, 
  CheckCircle2, 
  AlertTriangle, 
  Sliders, 
  Lock, 
  Layers, 
  Zap, 
  Search, 
  Check, 
  RefreshCw,
  Plus
} from "lucide-react";

interface PolicyRule {
  id: string;
  name: string;
  pattern: string;
  category: string;
  threshold: number;
  action: "MASK & VAULT" | "FLAG" | "PASS";
  entropyCheck: boolean;
  active: boolean;
}

const INITIAL_RULES: PolicyRule[] = [
  {
    id: "pol-aws",
    name: "AWS IAM Access Key & Secret",
    pattern: "AKIA[0-9A-Z]{16} | wJalrXUtnFEMI...",
    category: "Cloud Infrastructure",
    threshold: 85,
    action: "MASK & VAULT",
    entropyCheck: true,
    active: true
  },
  {
    id: "pol-stripe",
    name: "Stripe Secret & Restricted API Keys",
    pattern: "sk_live_[0-9a-zA-Z]{24} | rk_live_...",
    category: "Payment Gateway",
    threshold: 90,
    action: "MASK & VAULT",
    entropyCheck: true,
    active: true
  },
  {
    id: "pol-db",
    name: "Database Connection URIs",
    pattern: "postgres://*:*@*:*/* | mysql://...",
    category: "Database Credentials",
    threshold: 80,
    action: "MASK & VAULT",
    entropyCheck: false,
    active: true
  },
  {
    id: "pol-jwt",
    name: "JWT & OAuth Bearer Tokens",
    pattern: "eyJhbGciOi... (Base64 Header.Payload.Sig)",
    category: "Authentication",
    threshold: 75,
    action: "MASK & VAULT",
    entropyCheck: true,
    active: true
  },
  {
    id: "pol-github",
    name: "GitHub Personal Access Tokens",
    pattern: "ghp_[0-9a-zA-Z]{36} | gho_...",
    category: "Developer Tools",
    threshold: 90,
    action: "MASK & VAULT",
    entropyCheck: true,
    active: true
  },
  {
    id: "pol-keys",
    name: "Private Cryptographic Keys",
    pattern: "-----BEGIN RSA PRIVATE KEY-----",
    category: "Cryptography",
    threshold: 95,
    action: "MASK & VAULT",
    entropyCheck: false,
    active: true
  },
  {
    id: "pol-entropy",
    name: "Generic High-Entropy Base64 / Hex",
    pattern: "Shannon Entropy H(X) > 4.2",
    category: "Heuristic",
    threshold: 70,
    action: "FLAG",
    entropyCheck: true,
    active: true
  }
];

const NEGATIVE_ALLOWLIST = [
  {
    name: "UUIDv4 / GUID Tokens",
    example: "550e8400-e29b-41d4-a716-446655440000",
    action: "PASS (0.8 µs bypass)",
    rule: "Matches RFC 4122 version 4 layout"
  },
  {
    name: "Git Commit SHA-1 Hashes",
    example: "4b825dc642cb6eb9a060e54bf8d69288fbee4904",
    action: "PASS (0.9 µs bypass)",
    rule: "40-character lowercase hexadecimal"
  },
  {
    name: "OpenTelemetry Trace IDs",
    example: "4bf92f3577b34da6a3ce929d0e0e4736",
    action: "PASS (0.8 µs bypass)",
    rule: "W3C TraceContext traceparent structure"
  },
  {
    name: "Nginx / Apache Common Log Format",
    example: '192.168.1.1 - - [16/Oct/2026] "GET /api HTTP/1.1" 200',
    action: "PASS (0.5 µs bypass)",
    rule: "IP address and standard HTTP verbs"
  }
];

export default function PoliciesPage() {
  const [rules, setRules] = useState<PolicyRule[]>(INITIAL_RULES);
  const [enforcementMode, setEnforcementMode] = useState<"strict" | "balanced" | "permissive">("strict");
  const [savedSuccess, setSavedSuccess] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");

  const toggleRule = (id: string) => {
    setRules(prev => prev.map(r => r.id === id ? { ...r, active: !r.active } : r));
  };

  const handleDeploy = () => {
    setSavedSuccess(true);
    setTimeout(() => setSavedSuccess(false), 3000);
  };

  const filteredRules = rules.filter(r => {
    if (!searchQuery) return true;
    const q = searchQuery.toLowerCase();
    return r.name.toLowerCase().includes(q) || r.category.toLowerCase().includes(q) || r.pattern.toLowerCase().includes(q);
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 bg-white border border-slate-200 p-5 rounded-xl shadow-xs">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-xl font-bold text-slate-900 tracking-tight flex items-center gap-2.5">
              <FileText className="w-5 h-5 text-blue-600" />
              Detection & Redaction Policies
            </h1>
            <span className="px-2.5 py-0.5 rounded-full text-[11px] font-mono font-bold uppercase tracking-wider bg-blue-50 text-blue-700 border border-blue-200">
              1,361 Patterns Active
            </span>
          </div>
          <p className="text-slate-500 text-xs mt-1">
            Deterministic governance rules, pattern thresholds, and negative sample suppressors enforced across in-pod sidecars.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={handleDeploy}
            className="px-3.5 py-1.5 rounded-lg text-xs font-semibold bg-blue-600 hover:bg-blue-700 text-white transition-colors flex items-center gap-1.5 shadow-xs"
          >
            {savedSuccess ? <Check className="w-3.5 h-3.5" /> : <ShieldCheck className="w-3.5 h-3.5" />}
            {savedSuccess ? "Policy Deployed to Cluster!" : "Deploy Policies to Pods"}
          </button>
        </div>
      </div>

      {/* Policy Level Card */}
      <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs space-y-4">
        <div>
          <h2 className="text-sm font-bold text-slate-900 uppercase tracking-wider">
            Cluster Enforcement Profile
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Select the SCS threshold calibration applied across all 5 Kubernetes microservices.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div 
            onClick={() => setEnforcementMode("strict")}
            className={`p-4 rounded-xl border cursor-pointer transition-all ${
              enforcementMode === "strict"
                ? "bg-blue-50 border-blue-300 ring-2 ring-blue-500/10 shadow-xs"
                : "bg-white border-slate-200 hover:border-slate-300"
            }`}
          >
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-bold text-slate-900">Strict Enterprise (Recommended)</span>
              <span className="w-2 h-2 rounded-full bg-blue-600" />
            </div>
            <p className="text-xs text-slate-500 leading-relaxed">
              Masks any token with SCS score &ge; 70. Flags 40-69 for telemetry review. Enforces zero-leak guarantee.
            </p>
          </div>

          <div 
            onClick={() => setEnforcementMode("balanced")}
            className={`p-4 rounded-xl border cursor-pointer transition-all ${
              enforcementMode === "balanced"
                ? "bg-blue-50 border-blue-300 ring-2 ring-blue-500/10 shadow-xs"
                : "bg-white border-slate-200 hover:border-slate-300"
            }`}
          >
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-bold text-slate-900">Balanced Development</span>
              <span className="w-2 h-2 rounded-full bg-slate-400" />
            </div>
            <p className="text-xs text-slate-500 leading-relaxed">
              Masks tokens with SCS score &ge; 80. Flags 50-79. Tuned for staging and dev clusters with experimental endpoints.
            </p>
          </div>

          <div 
            onClick={() => setEnforcementMode("permissive")}
            className={`p-4 rounded-xl border cursor-pointer transition-all ${
              enforcementMode === "permissive"
                ? "bg-blue-50 border-blue-300 ring-2 ring-blue-500/10 shadow-xs"
                : "bg-white border-slate-200 hover:border-slate-300"
            }`}
          >
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-bold text-slate-900">Permissive / Audit-Only</span>
              <span className="w-2 h-2 rounded-full bg-slate-300" />
            </div>
            <p className="text-xs text-slate-500 leading-relaxed">
              Flags all detected credentials without tokenizing logs. Records all detections into SecureReveal for inspection.
            </p>
          </div>
        </div>
      </div>

      {/* Active Detectors Table */}
      <div className="bg-white border border-slate-200 rounded-xl shadow-xs overflow-hidden">
        <div className="p-4 border-b border-slate-200 flex flex-col md:flex-row gap-3 items-center justify-between">
          <div className="flex items-center gap-2">
            <Sliders className="w-4 h-4 text-blue-600" />
            <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider">
              Configured Credential Detectors ({rules.length})
            </h3>
          </div>

          <div className="relative w-full md:w-64">
            <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search detectors..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-slate-50 border border-slate-200 rounded-lg pl-9 pr-3 py-1.5 text-xs text-slate-800 placeholder-slate-400 focus:outline-none focus:border-blue-500 focus:bg-white transition-all"
            />
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 uppercase font-semibold text-[11px]">
              <tr>
                <th className="px-5 py-3">Rule Name & Pattern</th>
                <th className="px-5 py-3">Classification</th>
                <th className="px-5 py-3">SCS Threshold</th>
                <th className="px-5 py-3">Entropy Filter</th>
                <th className="px-5 py-3">Enforcement Action</th>
                <th className="px-5 py-3 text-right">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {filteredRules.map((rule) => (
                <tr key={rule.id} className="hover:bg-slate-50/80 transition-colors">
                  <td className="px-5 py-3.5">
                    <span className="font-bold text-slate-900 block">{rule.name}</span>
                    <span className="text-[11px] text-slate-400 font-mono block mt-0.5">{rule.pattern}</span>
                  </td>
                  <td className="px-5 py-3.5">
                    <span className="px-2 py-0.5 rounded text-[11px] font-semibold bg-slate-100 text-slate-700 border border-slate-200">
                      {rule.category}
                    </span>
                  </td>
                  <td className="px-5 py-3.5 font-mono text-slate-700 font-bold">
                    &ge; {rule.threshold}
                  </td>
                  <td className="px-5 py-3.5">
                    <span className={`text-[11px] font-semibold ${rule.entropyCheck ? "text-emerald-700" : "text-slate-400"}`}>
                      {rule.entropyCheck ? "H(X) Enabled" : "Pattern Match Only"}
                    </span>
                  </td>
                  <td className="px-5 py-3.5">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                      rule.action === "MASK & VAULT"
                        ? "bg-emerald-50 text-emerald-700 border border-emerald-200"
                        : "bg-amber-50 text-amber-700 border border-amber-200"
                    }`}>
                      {rule.action}
                    </span>
                  </td>
                  <td className="px-5 py-3.5 text-right">
                    <button
                      onClick={() => toggleRule(rule.id)}
                      className={`px-3 py-1 rounded-lg text-xs font-semibold transition-colors ${
                        rule.active
                          ? "bg-blue-50 text-blue-700 border border-blue-200 hover:bg-blue-100"
                          : "bg-slate-100 text-slate-500 border border-slate-200 hover:bg-slate-200"
                      }`}
                    >
                      {rule.active ? "Active" : "Disabled"}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Negative Sample Allowlist */}
      <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs space-y-3">
        <div>
          <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-600" />
            Negative Allowlist (Zero False-Positive Suppressors)
          </h3>
          <p className="text-xs text-slate-500 mt-0.5">
            Pre-compiled negative heuristics that bypass non-secret high-entropy structures in &lt; 1 µs without heavy computation.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
          {NEGATIVE_ALLOWLIST.map((item, idx) => (
            <div key={idx} className="bg-slate-50 border border-slate-200 rounded-lg p-3 space-y-1">
              <div className="flex items-center justify-between">
                <span className="font-bold text-slate-800">{item.name}</span>
                <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
                  {item.action}
                </span>
              </div>
              <p className="font-mono text-[11px] text-slate-500 truncate">{item.example}</p>
              <span className="text-[10px] text-slate-400 block">{item.rule}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
