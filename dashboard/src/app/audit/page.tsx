"use client";

import { useEffect, useState } from "react";
import { 
  ShieldCheck, 
  ShieldAlert, 
  AlertTriangle, 
  CheckCircle2, 
  RefreshCw, 
  Search, 
  Database,
  ArrowRight,
  Hash,
  Activity,
  History,
  Lock,
  Download,
  KeyRound,
  Check,
  Copy
} from "lucide-react";
import { fetchAuditLogs, fetchRecentReveals, verifyAudit, simulateTamper } from "@/lib/api";

export default function AuditPage() {
  const [logs, setLogs] = useState<any[]>([]);
  const [total, setTotal] = useState(0);
  const [recentReveals, setRecentReveals] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [verifying, setVerifying] = useState(false);
  const [tampering, setTampering] = useState(false);
  const [copiedId, setCopiedId] = useState<string | null>(null);
  
  // Verification State
  const [chainStatus, setChainStatus] = useState<{
    is_valid: boolean;
    broken_id: number | null;
    message: string;
    total_records: number;
    verified_at?: number;
  }>({
    is_valid: true,
    broken_id: null,
    message: "Verifying cryptographic chain...",
    total_records: 0
  });

  // Filter States - Default to "all" so user immediately sees all system events in real-time order!
  const [searchActor, setSearchActor] = useState("");
  const [actionFilter, setActionFilter] = useState("all");
  const [outcomeFilter, setOutcomeFilter] = useState("all");

  useEffect(() => {
    if (typeof window !== "undefined") {
      const params = new URLSearchParams(window.location.search);
      const q = params.get("q") || params.get("ref_id");
      if (q) {
        setSearchActor(q);
        setActionFilter("all"); // If a specific secret is queried, show all events for it
      }
    }
  }, []);

  const loadLogs = async () => {
    try {
      setLoading(true);
      const [res, reveals] = await Promise.all([
        fetchAuditLogs({
          limit: 100,
          q: searchActor.trim() || undefined,
          action: actionFilter !== "all" ? actionFilter : undefined,
          outcome: outcomeFilter !== "all" ? outcomeFilter : undefined
        }),
        fetchRecentReveals()
      ]);
      if (res?.entries) {
        setLogs(res.entries);
        setTotal(res.total);
      } else if (Array.isArray(res)) {
        setLogs(res);
        setTotal(res.length);
      }
      if (reveals && Array.isArray(reveals)) {
        setRecentReveals(reveals);
      }
    } catch (err) {
      console.error("Failed to load audit logs:", err);
    } finally {
      setLoading(false);
    }
  };

  const checkIntegrity = async () => {
    setVerifying(true);
    try {
      const data = await verifyAudit();
      setChainStatus(data);
    } catch (err) {
      console.error("Verification failed:", err);
      setChainStatus({
        is_valid: false,
        broken_id: -1,
        message: "Failed to connect to verification engine",
        total_records: 0
      });
    } finally {
      setVerifying(false);
    }
  };

  useEffect(() => {
    loadLogs();
    checkIntegrity();
  }, [actionFilter, outcomeFilter]);

  const handleSimulateTamper = async () => {
    setTampering(true);
    try {
      await simulateTamper("tamper", 1);
      await checkIntegrity();
      await loadLogs();
    } catch (err) {
      console.error(err);
    } finally {
      setTampering(false);
    }
  };

  const handleResetTamper = async () => {
    setTampering(true);
    try {
      await simulateTamper("reset");
      await checkIntegrity();
      await loadLogs();
    } catch (err) {
      console.error(err);
    } finally {
      setTampering(false);
    }
  };

  const handleExport = () => {
    const jsonStr = JSON.stringify(logs, null, 2);
    const blob = new Blob([jsonStr], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `logshield-audit-ledger-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const copyRefId = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(text);
    setTimeout(() => setCopiedId(null), 2000);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 bg-white border border-slate-200 p-5 rounded-xl shadow-xs">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-xl font-bold text-slate-900 tracking-tight flex items-center gap-2.5">
              <History className="w-5 h-5 text-blue-600" />
              Cryptographic Audit Ledger & Forensics
            </h1>
            <span className="px-2.5 py-0.5 rounded-full text-[11px] font-mono font-bold uppercase tracking-wider bg-emerald-50 text-emerald-700 border border-emerald-200">
              SHA-256 Chained
            </span>
          </div>
          <p className="text-slate-500 text-xs mt-1">
            Pre-authorization audit logging with forward-secure SHA-256 hash chaining and HMAC-SHA256 signatures. Guaranteed non-repudiation across all vault operations.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={handleExport}
            className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-white text-slate-700 border border-slate-200 hover:bg-slate-50 transition-colors flex items-center gap-1.5 shadow-xs"
          >
            <Download className="w-3.5 h-3.5 text-slate-500" />
            Export Ledger
          </button>
          <button
            onClick={checkIntegrity}
            disabled={verifying}
            className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-blue-600 hover:bg-blue-700 text-white transition-colors flex items-center gap-1.5 shadow-xs disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${verifying ? "animate-spin text-white" : ""}`} />
            Verify Hash Chain
          </button>
        </div>
      </div>

      {/* Cryptographic Chain Integrity Banner */}
      <div className={`p-5 rounded-xl border transition-all shadow-xs ${
        chainStatus.is_valid
          ? "bg-emerald-50 border-emerald-200 text-emerald-950"
          : "bg-rose-50 border-rose-300 text-rose-950 animate-pulse"
      }`}>
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-5">
          <div className="flex items-start gap-3.5">
            <div className={`p-2.5 rounded-xl border ${
              chainStatus.is_valid
                ? "bg-emerald-100 border-emerald-300 text-emerald-700"
                : "bg-rose-100 border-rose-300 text-rose-700"
            }`}>
              {chainStatus.is_valid ? (
                <ShieldCheck className="w-6 h-6" />
              ) : (
                <ShieldAlert className="w-6 h-6 text-rose-600" />
              )}
            </div>

            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-base font-bold">
                  {chainStatus.is_valid
                    ? "Cryptographic Hash Chain: VERIFIED & SEALED"
                    : "TAMPER ALERT: CRYPTOGRAPHIC INTEGRITY VIOLATION DETECTED"}
                </h3>
                <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold uppercase tracking-wider ${
                  chainStatus.is_valid
                    ? "bg-emerald-200 text-emerald-800"
                    : "bg-rose-200 text-rose-800"
                }`}>
                  {chainStatus.is_valid ? "INTACT" : `VIOLATION AT BLOCK #${chainStatus.broken_id}`}
                </span>
              </div>
              <p className="text-xs mt-0.5 opacity-90 max-w-2xl leading-relaxed">
                {chainStatus.message}. Every transaction event is mathematically chained to its immediate predecessor using SHA-256 and signed with the node master key.
              </p>
              <div className="flex items-center gap-4 text-[11px] font-mono opacity-75 mt-1.5">
                <span>Total Chained Blocks: <strong>{chainStatus.total_records || total}</strong></span>
                <span>•</span>
                <span>Algorithm: <strong>HMAC-SHA256</strong></span>
                <span>•</span>
                <span>Storage Mode: <strong>SQLite WAL Pre-Auth</strong></span>
              </div>
            </div>
          </div>

          {/* Tamper Simulation Interactive Trigger */}
          <div className="flex items-center gap-2 w-full md:w-auto">
            {chainStatus.is_valid ? (
              <button
                onClick={handleSimulateTamper}
                disabled={tampering}
                className="w-full md:w-auto px-3.5 py-1.5 rounded-lg font-bold text-xs bg-white text-rose-700 hover:bg-rose-100 border border-rose-200 transition-colors flex items-center justify-center gap-1.5 shadow-xs"
              >
                <AlertTriangle className="w-3.5 h-3.5 text-rose-600" />
                Simulate Tamper Attack
              </button>
            ) : (
              <button
                onClick={handleResetTamper}
                disabled={tampering}
                className="w-full md:w-auto px-4 py-1.5 rounded-lg font-bold text-xs bg-emerald-600 text-white hover:bg-emerald-700 transition-colors flex items-center justify-center gap-1.5 shadow-xs"
              >
                <CheckCircle2 className="w-3.5 h-3.5" />
                Restore Ledger Integrity
              </button>
            )}
          </div>
        </div>
      </div>

      {/* High-Priority Secret Decryption Activity Banner */}
      {recentReveals.length > 0 && (
        <div className="bg-purple-50/50 border border-purple-200/80 rounded-xl p-4 shadow-xs">
          <div className="flex items-center justify-between mb-2.5">
            <div className="flex items-center gap-2">
              <KeyRound className="w-4 h-4 text-purple-700" />
              <h3 className="text-xs font-bold text-purple-950 uppercase tracking-wider">
                Recent Secret Access & Reveal Audits (Guaranteed Non-Repudiation)
              </h3>
            </div>
            <span className="text-[11px] text-purple-700 font-medium">
              Chained & Signed
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2.5">
            {recentReveals.slice(0, 3).map((rev: any) => (
              <div 
                key={rev.id} 
                className="bg-white border border-purple-200 rounded-lg p-2.5 text-xs flex flex-col justify-between shadow-2xs hover:border-purple-400 transition-colors cursor-pointer"
                onClick={() => {
                  setSearchActor(rev.ref_id);
                  setActionFilter("all");
                }}
              >
                <div className="flex items-center justify-between">
                  <span className="font-mono font-bold text-purple-700 text-xs">{rev.ref_id}</span>
                  <span className={`px-1.5 py-0.2 rounded text-[10px] font-bold ${
                    rev.outcome === "SUCCESS"
                      ? "bg-emerald-50 text-emerald-700 border border-emerald-200"
                      : "bg-amber-50 text-amber-700 border border-amber-200"
                  }`}>
                    {rev.outcome}
                  </span>
                </div>
                <div className="text-[11px] text-slate-500 mt-1 truncate">
                  <strong className="text-slate-800">{rev.actor}</strong> ({rev.pod_name})
                </div>
                <div className="text-[10px] text-slate-400 mt-0.5 flex items-center justify-between">
                  <span>Block #{rev.id}</span>
                  <span>{new Date(rev.timestamp * 1000).toLocaleTimeString()}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Quick Navigation Tabs */}
      <div className="flex flex-wrap items-center gap-2 border-b border-slate-200 pb-2">
        <button
          onClick={() => { setActionFilter("RETRIEVE"); setOutcomeFilter("all"); }}
          className={`px-3.5 py-2 rounded-lg text-xs font-semibold flex items-center gap-2 transition-all ${
            actionFilter === "RETRIEVE"
              ? "bg-purple-600 text-white shadow-xs"
              : "bg-white text-slate-600 hover:bg-slate-100 border border-slate-200"
          }`}
        >
          <KeyRound className="w-3.5 h-3.5" />
          <span>Secret Access / Reveal Audits</span>
          <span className="px-1.5 py-0.2 rounded text-[10px] bg-white/20 font-mono">
            {actionFilter === "RETRIEVE" ? total : ""}
          </span>
        </button>

        <button
          onClick={() => { setActionFilter("all"); setOutcomeFilter("all"); }}
          className={`px-3.5 py-2 rounded-lg text-xs font-semibold flex items-center gap-2 transition-all ${
            actionFilter === "all"
              ? "bg-blue-600 text-white shadow-xs"
              : "bg-white text-slate-600 hover:bg-slate-100 border border-slate-200"
          }`}
        >
          <Activity className="w-3.5 h-3.5" />
          <span>All System Events</span>
        </button>

        <button
          onClick={() => { setActionFilter("STORE"); setOutcomeFilter("all"); }}
          className={`px-3.5 py-2 rounded-lg text-xs font-semibold flex items-center gap-2 transition-all ${
            actionFilter === "STORE"
              ? "bg-slate-800 text-white shadow-xs"
              : "bg-white text-slate-600 hover:bg-slate-100 border border-slate-200"
          }`}
        >
          <Database className="w-3.5 h-3.5" />
          <span>In-Pod Vault Ingestions</span>
        </button>
      </div>

      {/* Filter and Search Bar */}
      <div className="flex flex-col md:flex-row gap-3 items-center justify-between">
        <div className="flex flex-1 gap-2 w-full">
          <div className="relative flex-1">
            <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search reference token (SEC-XXXX), actor, or reason..."
              value={searchActor}
              onChange={(e) => setSearchActor(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && loadLogs()}
              className="w-full bg-white border border-slate-200 rounded-lg pl-9 pr-4 py-2 text-xs text-slate-800 placeholder-slate-400 focus:outline-none focus:border-blue-500 transition-colors"
            />
          </div>

          <button
            onClick={loadLogs}
            className="px-4 py-2 rounded-lg text-xs font-semibold bg-white border border-slate-200 text-slate-700 hover:bg-slate-50 transition-colors shadow-xs"
          >
            Search
          </button>
        </div>

        <div className="flex gap-2 w-full md:w-auto">
          {/* Action Filter */}
          <select
            value={actionFilter}
            onChange={(e) => setActionFilter(e.target.value)}
            className="bg-white border border-slate-200 rounded-lg px-3 py-2 text-xs text-slate-700 focus:outline-none focus:border-blue-500 font-medium"
          >
            <option value="all">All Actions</option>
            <option value="RETRIEVE">Secret Decryption (RETRIEVE)</option>
            <option value="STORE">In-Pod Stream Stores (STORE)</option>
            <option value="TAMPER_TEST">Integrity Tests (TAMPER_TEST)</option>
          </select>

          {/* Outcome Filter */}
          <select
            value={outcomeFilter}
            onChange={(e) => setOutcomeFilter(e.target.value)}
            className="bg-white border border-slate-200 rounded-lg px-3 py-2 text-xs text-slate-700 focus:outline-none focus:border-blue-500 font-medium"
          >
            <option value="all">All Outcomes</option>
            <option value="ATTEMPTED">ATTEMPTED (Pre-Auth Intent Logged)</option>
            <option value="SUCCESS">SUCCESS (Decrypted & Released)</option>
            <option value="DENIED">DENIED (RBAC Blocked)</option>
            <option value="NOT_FOUND">NOT_FOUND</option>
            <option value="TAMPER_DETECTED">TAMPER_DETECTED</option>
          </select>
        </div>
      </div>

      {/* Forensic Ledger Table */}
      <div className="bg-white border border-slate-200 rounded-xl shadow-xs overflow-hidden">
        <div className="p-4 border-b border-slate-200 bg-slate-50 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Database className="w-4 h-4 text-blue-600" />
            <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider">Cryptographically Linked Ledger Blocks</h3>
          </div>
          <span className="text-xs text-slate-500 font-mono">
            Showing {logs.length} of {total} events
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50/50 text-slate-500 uppercase font-semibold text-[11px] border-b border-slate-200">
              <tr>
                <th className="px-5 py-3">Block #</th>
                <th className="px-5 py-3">Timestamp</th>
                <th className="px-5 py-3">Actor & Identity</th>
                <th className="px-5 py-3">Action</th>
                <th className="px-5 py-3">Vault Ref ID</th>
                <th className="px-5 py-3">Audit Outcome</th>
                <th className="px-5 py-3">SHA-256 Hash Chaining</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-mono">
              {loading ? (
                <tr>
                  <td colSpan={7} className="px-5 py-12 text-center text-slate-400 font-sans">
                    <div className="flex items-center justify-center gap-2">
                      <RefreshCw className="w-4 h-4 animate-spin text-blue-600" />
                      Loading cryptographic ledger entries...
                    </div>
                  </td>
                </tr>
              ) : logs.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-5 py-12 text-center text-slate-400 font-sans italic">
                    No audit records found matching criteria.
                  </td>
                </tr>
              ) : (
                logs.map((log: any) => {
                  const isCorrupted = chainStatus.broken_id === log.id;
                  const dateStr = log.timestamp 
                    ? new Date(log.timestamp * 1000).toLocaleString() 
                    : "N/A";

                  const isRetrieve = log.action === "RETRIEVE" || log.action === "REVEAL_REQUEST";

                  return (
                    <tr 
                      key={log.id} 
                      className={`transition-colors ${
                        isCorrupted 
                          ? "bg-rose-50/80 text-rose-900 border-y border-rose-300 font-bold" 
                          : isRetrieve
                          ? "bg-purple-50/30 hover:bg-purple-50/60 text-slate-800 border-l-4 border-purple-500"
                          : "hover:bg-slate-50/80 text-slate-700"
                      }`}
                    >
                      <td className="px-5 py-3.5 font-bold text-slate-900">
                        <div className="flex items-center gap-1.5">
                          <span>#{log.id}</span>
                          {isRetrieve && (
                            <span className="px-1.5 py-0.2 rounded bg-purple-100 text-purple-800 text-[9px] font-sans font-bold border border-purple-200">
                              REVEAL ACCESS
                            </span>
                          )}
                          {isCorrupted && (
                            <span className="ml-1.5 px-1.5 py-0.5 rounded bg-rose-600 text-white text-[9px] font-sans font-bold">
                              TAMPERED
                            </span>
                          )}
                        </div>
                      </td>
                      <td className="px-5 py-3.5 text-slate-500 text-[11px] whitespace-nowrap">
                        {dateStr}
                      </td>
                      <td className="px-5 py-3.5">
                        <span className="font-semibold text-slate-900 block font-sans">{log.actor}</span>
                        <span className="text-[10px] text-slate-400 block font-mono">
                          {log.client_ip || "127.0.0.1"} • {log.pod_name || "default"}
                        </span>
                        {log.reason && log.reason !== "automatic_detection" && (
                          <span className="text-[10px] text-slate-500 italic block font-sans mt-0.5">
                            "{log.reason}"
                          </span>
                        )}
                      </td>
                      <td className="px-5 py-3.5">
                        <span className={`px-2.5 py-0.5 rounded text-[10px] font-bold border ${
                          log.action === "RETRIEVE" || log.action === "REVEAL_REQUEST"
                            ? "bg-purple-50 text-purple-700 border-purple-200 font-mono"
                            : log.action === "STORE" || log.action === "VAULT_STORE"
                            ? "bg-blue-50 text-blue-700 border-blue-200 font-mono"
                            : "bg-slate-50 text-slate-700 border-slate-200 font-mono"
                        }`}>
                          {log.action}
                        </span>
                      </td>
                      <td className="px-5 py-3.5">
                        <div className="flex items-center gap-1.5">
                          <span className="font-mono text-blue-700 font-bold">
                            {log.ref_id || "N/A"}
                          </span>
                          {log.ref_id && (
                            <button
                              onClick={() => copyRefId(log.ref_id)}
                              className="text-slate-400 hover:text-slate-600 p-0.5"
                              title="Copy Ref ID"
                            >
                              {copiedId === log.ref_id ? (
                                <Check className="w-3 h-3 text-emerald-600" />
                              ) : (
                                <Copy className="w-3 h-3" />
                              )}
                            </button>
                          )}
                        </div>
                      </td>
                      <td className="px-5 py-3.5">
                        <span className={`px-2.5 py-0.5 rounded text-[10px] font-bold flex items-center gap-1 w-fit ${
                          log.outcome === "SUCCESS"
                            ? "bg-emerald-50 text-emerald-700 border border-emerald-200"
                            : log.outcome === "ATTEMPTED"
                            ? "bg-amber-50 text-amber-700 border border-amber-200"
                            : log.outcome === "DENIED"
                            ? "bg-rose-50 text-rose-700 border border-rose-200"
                            : "bg-slate-50 text-slate-600 border border-slate-200"
                        }`}>
                          {log.outcome === "SUCCESS" && <CheckCircle2 className="w-3 h-3 text-emerald-600" />}
                          {log.outcome === "ATTEMPTED" && <Lock className="w-3 h-3 text-amber-600" />}
                          {log.outcome === "DENIED" && <ShieldAlert className="w-3 h-3 text-rose-600" />}
                          <span>{log.outcome}</span>
                        </span>
                      </td>
                      <td className="px-5 py-3.5 text-[11px]">
                        <div className="flex items-center gap-1.5" title={`Prev: ${log.prev_hash}\nEntry: ${log.entry_hash}`}>
                          <Hash className="w-3 h-3 text-slate-400" />
                          <span className="text-slate-400">
                            {log.prev_hash ? log.prev_hash.substring(0, 8) : "00000000"}...
                          </span>
                          <ArrowRight className="w-3 h-3 text-slate-400" />
                          <span className={`font-bold ${isCorrupted ? "text-rose-600 underline" : "text-emerald-700"}`}>
                            {log.entry_hash ? log.entry_hash.substring(0, 8) : "N/A"}...
                          </span>
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
