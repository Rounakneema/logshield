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
  Download
} from "lucide-react";
import { fetchAuditLogs, verifyAudit, simulateTamper } from "@/lib/api";

export default function AuditPage() {
  const [logs, setLogs] = useState<any[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [verifying, setVerifying] = useState(false);
  const [tampering, setTampering] = useState(false);
  
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

  // Filter States
  const [searchActor, setSearchActor] = useState("");
  const [actionFilter, setActionFilter] = useState("all");
  const [outcomeFilter, setOutcomeFilter] = useState("all");

  const loadLogs = async () => {
    try {
      const res = await fetchAuditLogs({
        limit: 100,
        actor: searchActor || undefined,
        action: actionFilter !== "all" ? actionFilter : undefined,
        outcome: outcomeFilter !== "all" ? outcomeFilter : undefined
      });
      if (res?.entries) {
        setLogs(res.entries);
        setTotal(res.total);
      } else if (Array.isArray(res)) {
        setLogs(res);
        setTotal(res.length);
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

      {/* Filter and Search Bar */}
      <div className="flex flex-col md:flex-row gap-3 items-center justify-between">
        <div className="flex flex-1 gap-2 w-full">
          <div className="relative flex-1">
            <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search by actor or reference ID..."
              value={searchActor}
              onChange={(e) => setSearchActor(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && loadLogs()}
              className="w-full bg-white border border-slate-200 rounded-lg pl-9 pr-4 py-1.5 text-xs text-slate-800 placeholder-slate-400 focus:outline-none focus:border-blue-500 transition-colors"
            />
          </div>

          <button
            onClick={loadLogs}
            className="px-3.5 py-1.5 rounded-lg text-xs font-semibold bg-white border border-slate-200 text-slate-700 hover:bg-slate-50 transition-colors shadow-xs"
          >
            Search
          </button>
        </div>

        <div className="flex gap-2 w-full md:w-auto">
          {/* Action Filter */}
          <select
            value={actionFilter}
            onChange={(e) => setActionFilter(e.target.value)}
            className="bg-white border border-slate-200 rounded-lg px-3 py-1.5 text-xs text-slate-700 focus:outline-none focus:border-blue-500 font-medium"
          >
            <option value="all">All Actions</option>
            <option value="VAULT_STORE">VAULT_STORE</option>
            <option value="REVEAL_REQUEST">REVEAL_REQUEST</option>
            <option value="TAMPER_TEST">TAMPER_TEST</option>
          </select>

          {/* Outcome Filter */}
          <select
            value={outcomeFilter}
            onChange={(e) => setOutcomeFilter(e.target.value)}
            className="bg-white border border-slate-200 rounded-lg px-3 py-1.5 text-xs text-slate-700 focus:outline-none focus:border-blue-500 font-medium"
          >
            <option value="all">All Outcomes</option>
            <option value="SUCCESS">SUCCESS</option>
            <option value="DENIED">DENIED</option>
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
                <th className="px-5 py-3">Captured Timestamp</th>
                <th className="px-5 py-3">Actor & Identity</th>
                <th className="px-5 py-3">Action</th>
                <th className="px-5 py-3">Vault Ref ID</th>
                <th className="px-5 py-3">Outcome</th>
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

                  return (
                    <tr 
                      key={log.id} 
                      className={`transition-colors ${
                        isCorrupted 
                          ? "bg-rose-50/80 text-rose-900 border-y border-rose-300 font-bold" 
                          : "hover:bg-slate-50/80 text-slate-700"
                      }`}
                    >
                      <td className="px-5 py-3.5 font-bold text-slate-900">
                        #{log.id}
                        {isCorrupted && (
                          <span className="ml-1.5 px-1.5 py-0.5 rounded bg-rose-600 text-white text-[9px] font-sans font-bold">
                            TAMPERED
                          </span>
                        )}
                      </td>
                      <td className="px-5 py-3.5 text-slate-500 text-[11px] whitespace-nowrap">
                        {dateStr}
                      </td>
                      <td className="px-5 py-3.5">
                        <span className="font-semibold text-slate-900 block font-sans">{log.actor}</span>
                        <span className="text-[10px] text-slate-400 block">{log.client_ip || "127.0.0.1"} • {log.pod_name || "default"}</span>
                      </td>
                      <td className="px-5 py-3.5">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${
                          log.action === "VAULT_STORE"
                            ? "bg-emerald-50 text-emerald-700 border-emerald-200"
                            : log.action === "REVEAL_REQUEST"
                            ? "bg-amber-50 text-amber-700 border-amber-200"
                            : "bg-blue-50 text-blue-700 border-blue-200"
                        }`}>
                          {log.action}
                        </span>
                      </td>
                      <td className="px-5 py-3.5">
                        <span className="font-mono text-blue-700 font-bold">
                          {log.ref_id || "N/A"}
                        </span>
                      </td>
                      <td className="px-5 py-3.5">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                          log.outcome === "SUCCESS"
                            ? "bg-emerald-50 text-emerald-700 border border-emerald-200"
                            : "bg-rose-50 text-rose-700 border border-rose-200"
                        }`}>
                          {log.outcome}
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
