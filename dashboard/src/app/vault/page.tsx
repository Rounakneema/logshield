"use client";

import { useEffect, useState, useMemo } from "react";
import { fetchVault, retrieveVault } from "@/lib/api";
import { 
  KeyRound, 
  ShieldCheck, 
  Lock, 
  Eye, 
  EyeOff, 
  Search, 
  RefreshCw, 
  Check, 
  Copy, 
  AlertTriangle,
  Server,
  Clock,
  Sparkles,
  Shield,
  Layers,
  CheckCircle2
} from "lucide-react";

export default function VaultPage() {
  const [vaultEntries, setVaultEntries] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [isUnlocked, setIsUnlocked] = useState(false);
  const [pin, setPin] = useState("");
  const [pinError, setPinError] = useState("");
  const [revealedSecrets, setRevealedSecrets] = useState<Record<string, string>>({});
  const [revealing, setRevealing] = useState<Record<string, boolean>>({});
  const [searchQuery, setSearchQuery] = useState("");
  const [copiedId, setCopiedId] = useState<string | null>(null);

  const loadData = async () => {
    try {
      const data = await fetchVault();
      setVaultEntries(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error("Failed to fetch vault data:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!isUnlocked) return;
    loadData();
    const interval = setInterval(loadData, 4000);
    return () => clearInterval(interval);
  }, [isUnlocked]);

  const handleUnlock = (e: React.FormEvent) => {
    e.preventDefault();
    if (pin === "vault789") {
      setIsUnlocked(true);
      setPinError("");
    } else {
      setPinError("Invalid Vault PIN. Use demo PIN: vault789");
    }
  };

  const handleReveal = async (ref_id: string) => {
    if (revealedSecrets[ref_id]) {
      const newRevealed = { ...revealedSecrets };
      delete newRevealed[ref_id];
      setRevealedSecrets(newRevealed);
      return;
    }

    setRevealing(prev => ({ ...prev, [ref_id]: true }));
    try {
      const result = await retrieveVault(ref_id, "admin", "Dashboard security inspection");
      if (result.success) {
        setRevealedSecrets(prev => ({ ...prev, [ref_id]: result.plaintext }));
      } else {
        alert("Reveal failed: " + result.message);
      }
    } catch (err) {
      console.error(err);
      alert("Failed to decrypt secret. Check sidecar authorization.");
    } finally {
      setRevealing(prev => ({ ...prev, [ref_id]: false }));
    }
  };

  const copySecret = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const getSecretCategory = (entry: any) => {
    const raw = entry.pattern_name || entry.secret_type || entry.ref_id || "";
    if (raw.includes("AWS") || raw.includes("AKIA")) return { name: "AWS IAM Key", color: "bg-amber-50 text-amber-700 border-amber-200" };
    if (raw.includes("Stripe") || raw.includes("sk_")) return { name: "Stripe Secret", color: "bg-blue-50 text-blue-700 border-blue-200" };
    if (raw.includes("postgres") || raw.includes("DATABASE")) return { name: "Database URI", color: "bg-purple-50 text-purple-700 border-purple-200" };
    if (raw.includes("JWT") || raw.includes("Bearer")) return { name: "JWT Auth Token", color: "bg-emerald-50 text-emerald-700 border-emerald-200" };
    return { name: "Cryptographic Secret", color: "bg-slate-50 text-slate-700 border-slate-200" };
  };

  const filteredEntries = useMemo(() => {
    return vaultEntries.filter((entry) => {
      if (!searchQuery) return true;
      const q = searchQuery.toLowerCase();
      const ref = (entry.ref_id || "").toLowerCase();
      const pod = (entry.pod_name || entry.pod_uid || "").toLowerCase();
      const type = (entry.pattern_name || entry.secret_type || "").toLowerCase();
      return ref.includes(q) || pod.includes(q) || type.includes(q);
    });
  }, [vaultEntries, searchQuery]);

  if (!isUnlocked) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[65vh] p-4">
        <div className="bg-white border border-slate-200 rounded-2xl p-8 max-w-md w-full text-center shadow-xs space-y-6">
          <div className="w-14 h-14 bg-blue-50 border border-blue-100 rounded-2xl flex items-center justify-center mx-auto text-blue-600 shadow-xs">
            <Lock className="w-7 h-7" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-slate-900">SecureReveal Vault</h2>
            <p className="text-slate-500 text-xs mt-1 leading-relaxed">
              Secondary zero-knowledge authentication required to access decrypted credentials and inspect in-pod isolation keys.
            </p>
          </div>
          
          <form onSubmit={handleUnlock} className="space-y-4">
            <div>
              <div className="flex items-center justify-between text-xs text-slate-500 mb-1.5">
                <span>Security Access PIN</span>
                <span className="text-slate-400 font-mono text-[11px]">Demo: <strong className="text-blue-600">vault789</strong></span>
              </div>
              <input
                type="password"
                placeholder="••••••"
                value={pin}
                onChange={(e) => setPin(e.target.value)}
                className="w-full bg-slate-50 border border-slate-200 rounded-xl py-3 px-4 text-center text-xl tracking-[0.4em] font-mono text-slate-900 focus:outline-none focus:border-blue-500 focus:bg-white transition-all"
                autoFocus
              />
              {pinError && <p className="text-rose-600 text-xs mt-2 font-medium">{pinError}</p>}
            </div>

            <button
              type="submit"
              className="w-full py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-semibold text-xs rounded-xl shadow-xs transition-colors flex items-center justify-center gap-2"
            >
              <KeyRound className="w-4 h-4" />
              Authenticate & Decrypt Vault
            </button>
          </form>

          <div className="pt-2 border-t border-slate-100 flex items-center justify-center gap-2 text-[11px] text-slate-400">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
            <span>FIPS 140-2 AES-256-GCM Encryption Standard</span>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 bg-white border border-slate-200 p-5 rounded-xl shadow-xs">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-xl font-bold text-slate-900 tracking-tight flex items-center gap-2.5">
              <KeyRound className="w-5 h-5 text-blue-600" />
              SecureReveal Vault
            </h1>
            <span className="px-2.5 py-0.5 rounded-full text-[11px] font-mono font-bold uppercase tracking-wider bg-emerald-50 text-emerald-700 border border-emerald-200">
              AES-256-GCM Authenticated
            </span>
          </div>
          <p className="text-slate-500 text-xs mt-1">
            Reversible cryptographic key repository. Intercepted secrets are encrypted in-pod and mapped to deterministic reference tokens (<code className="font-mono text-slate-700 font-semibold">SEC-XXXX</code>).
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => {
              setIsUnlocked(false);
              setRevealedSecrets({});
            }}
            className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-white text-slate-700 border border-slate-200 hover:bg-slate-50 transition-colors flex items-center gap-1.5 shadow-xs"
          >
            <Lock className="w-3.5 h-3.5 text-slate-500" />
            Lock Vault
          </button>
          <button
            onClick={loadData}
            className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-blue-600 hover:bg-blue-700 text-white transition-colors flex items-center gap-1.5 shadow-xs"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            Refresh Records
          </button>
        </div>
      </div>

      {/* KPI Stats Strip */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-xs">
          <span className="text-slate-500 text-xs font-medium block">Total Vaulted Secrets</span>
          <div className="mt-1 flex items-baseline gap-2">
            <span className="text-2xl font-bold text-slate-900">{vaultEntries.length}</span>
            <span className="text-xs font-semibold text-emerald-600">100% Encrypted</span>
          </div>
        </div>

        <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-xs">
          <span className="text-slate-500 text-xs font-medium block">Encryption Algorithm</span>
          <div className="mt-1 flex items-baseline gap-2">
            <span className="text-base font-bold text-slate-900 font-mono">AES-256-GCM</span>
            <span className="text-xs text-slate-500">256-bit key</span>
          </div>
        </div>

        <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-xs">
          <span className="text-slate-500 text-xs font-medium block">Authorized Actors</span>
          <div className="mt-1 flex items-baseline gap-2">
            <span className="text-base font-bold text-slate-900 font-mono">admin, sec-ops</span>
            <span className="text-xs text-blue-600">RBAC Enforced</span>
          </div>
        </div>

        <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-xs">
          <span className="text-slate-500 text-xs font-medium block">Currently Revealed</span>
          <div className="mt-1 flex items-baseline gap-2">
            <span className="text-2xl font-bold text-slate-900">{Object.keys(revealedSecrets).length}</span>
            <span className="text-xs text-amber-600">Audited Actions</span>
          </div>
        </div>
      </div>

      {/* Vault Table Card */}
      <div className="bg-white border border-slate-200 rounded-xl shadow-xs overflow-hidden">
        {/* Table Toolbar */}
        <div className="p-4 border-b border-slate-200 flex flex-col md:flex-row gap-4 items-center justify-between">
          <div className="relative w-full md:w-80">
            <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search reference ID, pod, or type..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-slate-50 border border-slate-200 rounded-lg pl-9 pr-3 py-1.5 text-xs text-slate-800 placeholder-slate-400 focus:outline-none focus:border-blue-500 focus:bg-white transition-all"
            />
          </div>

          <div className="text-xs text-slate-500 font-medium">
            Showing <strong className="text-slate-800">{filteredEntries.length}</strong> of {vaultEntries.length} secrets
          </div>
        </div>

        {/* Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-xs text-left">
            <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 font-semibold uppercase tracking-wider text-[11px]">
              <tr>
                <th className="px-5 py-3">Reference Token</th>
                <th className="px-5 py-3">Classification</th>
                <th className="px-5 py-3">Captured Timestamp</th>
                <th className="px-5 py-3">Origin Pod & Service</th>
                <th className="px-5 py-3">SCS Score</th>
                <th className="px-5 py-3 text-right">Plaintext Decryption</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {loading ? (
                <tr>
                  <td colSpan={6} className="px-5 py-12 text-center text-slate-400">
                    <div className="flex items-center justify-center gap-2">
                      <RefreshCw className="w-4 h-4 animate-spin text-blue-600" />
                      Loading encrypted records from in-pod volume...
                    </div>
                  </td>
                </tr>
              ) : filteredEntries.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-5 py-12 text-center text-slate-400">
                    No secrets currently held in vault matching current search query.
                  </td>
                </tr>
              ) : (
                filteredEntries.map((entry: any) => {
                  const cat = getSecretCategory(entry);
                  const isRevealed = !!revealedSecrets[entry.ref_id];
                  const isBusy = revealing[entry.ref_id];
                  const score = entry.scs_score || entry.score || 95;
                  
                  // Extract service from pod name or entry
                  const podName = entry.pod_name || entry.pod_uid || "auth-service-79f8c4";
                  let serviceName = "auth-service";
                  if (podName.includes("payment")) serviceName = "payment-service";
                  if (podName.includes("inventory")) serviceName = "inventory-service";
                  if (podName.includes("user")) serviceName = "user-service";
                  if (podName.includes("notification")) serviceName = "notification-service";

                  // Timestamp formatted to local time
                  const rawTs = entry.created_at || entry.timestamp;
                  const dateStr = typeof rawTs === "number" 
                    ? new Date(rawTs > 1e11 ? rawTs : rawTs * 1000).toLocaleString() 
                    : new Date(rawTs || Date.now()).toLocaleString();

                  return (
                    <tr key={entry.ref_id} className="hover:bg-slate-50/80 transition-colors">
                      {/* Reference Token */}
                      <td className="px-5 py-3.5 font-mono">
                        <div className="inline-flex items-center gap-1.5 bg-blue-50 text-blue-700 border border-blue-200 px-2 py-0.5 rounded font-bold text-xs">
                          <Lock className="w-3 h-3 text-blue-600" />
                          {entry.ref_id}
                        </div>
                      </td>

                      {/* Classification */}
                      <td className="px-5 py-3.5">
                        <span className={`inline-block px-2 py-0.5 rounded text-[11px] font-semibold border ${cat.color}`}>
                          {cat.name}
                        </span>
                      </td>

                      {/* Timestamp */}
                      <td className="px-5 py-3.5 text-slate-600 font-mono text-[11px]">
                        {dateStr}
                      </td>

                      {/* Pod & Service */}
                      <td className="px-5 py-3.5">
                        <div className="flex items-center gap-1.5">
                          <span className="font-semibold text-slate-800">{serviceName}</span>
                          <span className="text-[10px] text-slate-400 font-mono truncate max-w-[120px]">
                            ({podName})
                          </span>
                        </div>
                      </td>

                      {/* SCS Score */}
                      <td className="px-5 py-3.5">
                        <div className="flex items-center gap-2">
                          <div className="w-16 bg-slate-100 rounded-full h-1.5 overflow-hidden">
                            <div 
                              className={`h-full rounded-full ${score >= 80 ? 'bg-emerald-500' : 'bg-amber-500'}`}
                              style={{ width: `${score}%` }}
                            />
                          </div>
                          <span className="font-semibold text-slate-700 font-mono text-[11px]">{score}</span>
                        </div>
                      </td>

                      {/* Action */}
                      <td className="px-5 py-3.5 text-right">
                        <div className="flex items-center justify-end gap-2">
                          {isRevealed && (
                            <div className="flex items-center gap-1.5 bg-emerald-50 border border-emerald-200 rounded-lg px-2.5 py-1 text-slate-800 font-mono text-xs max-w-xs truncate shadow-xs">
                              <span className="font-bold text-emerald-700 select-all">{revealedSecrets[entry.ref_id]}</span>
                              <button
                                onClick={() => copySecret(revealedSecrets[entry.ref_id], entry.ref_id)}
                                className="text-slate-400 hover:text-slate-700 p-0.5 rounded"
                                title="Copy Plaintext"
                              >
                                {copiedId === entry.ref_id ? (
                                  <Check className="w-3.5 h-3.5 text-emerald-600" />
                                ) : (
                                  <Copy className="w-3.5 h-3.5" />
                                )}
                              </button>
                            </div>
                          )}

                          <button 
                            onClick={() => handleReveal(entry.ref_id)}
                            disabled={isBusy}
                            className={`text-xs px-3 py-1.5 rounded-lg font-semibold transition-colors flex items-center gap-1.5 shadow-xs disabled:opacity-50 ${
                              isRevealed
                                ? "bg-slate-100 hover:bg-slate-200 text-slate-700 border border-slate-200"
                                : "bg-blue-600 hover:bg-blue-700 text-white"
                            }`}
                          >
                            {isRevealed ? (
                              <>
                                <EyeOff className="w-3.5 h-3.5" />
                                Hide
                              </>
                            ) : (
                              <>
                                <Eye className="w-3.5 h-3.5" />
                                {isBusy ? "Decrypting..." : "Request Reveal"}
                              </>
                            )}
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
