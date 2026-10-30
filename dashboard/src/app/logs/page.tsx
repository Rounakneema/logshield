"use client";

import { useEffect, useState, useRef, useMemo } from "react";
import Link from "next/link";
import { 
  Terminal, 
  ShieldCheck, 
  ShieldAlert, 
  AlertTriangle, 
  RefreshCw, 
  Eye, 
  X, 
  ArrowRight, 
  CheckCircle2, 
  Lock, 
  Unlock,
  KeyRound,
  Search, 
  Pause, 
  Play, 
  Download, 
  Copy, 
  Check, 
  Server,
  Clock
} from "lucide-react";
import { fetchLogs, fetchRawLogs, fetchMode, setMode } from "@/lib/api";

interface TokenInspectData {
  sanitizedLine: string;
  service: string;
  refId?: string;
  scsScore?: number;
}

export default function LiveLogs() {
  const [mode, setModeState] = useState<string>("protected");
  const [service, setService] = useState<string>("all");
  const [logs, setLogs] = useState<string[]>([]);
  const [rawLogs, setRawLogs] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [filterQuery, setFilterQuery] = useState("");
  const [levelFilter, setLevelFilter] = useState<string>("ALL");
  const [timeWindow, setTimeWindow] = useState<string>("ALL");
  const [isPaused, setIsPaused] = useState(false);
  const [inspectItem, setInspectItem] = useState<TokenInspectData | null>(null);
  const [autoScroll, setAutoScroll] = useState(true);
  const [copied, setCopied] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  const services = [
    { id: "all", name: "All Services" },
    { id: "auth-service", name: "auth-service" },
    { id: "payment-service", name: "payment-service" },
    { id: "inventory-service", name: "inventory-service" },
    { id: "user-service", name: "user-service" },
    { id: "notification-service", name: "notification-service" },
  ];

  const prevServiceRef = useRef<string>(service);

  const loadLogs = async () => {
    if (isPaused) return;
    try {
      const [modeData, sanitizedData, rawData] = await Promise.all([
        fetchMode(),
        fetchLogs(service, timeWindow === "ALL" ? undefined : timeWindow),
        fetchRawLogs(service)
      ]);
      if (modeData?.mode) setModeState(modeData.mode);
      
      setLogs((prevLogs) => {
        if (prevServiceRef.current !== service) {
          prevServiceRef.current = service;
          return sanitizedData || [];
        }
        if (!sanitizedData || sanitizedData.length === 0) return prevLogs;
        if (prevLogs.length === 0) return sanitizedData;

        const existingSet = new Set(prevLogs);
        const incomingNew = sanitizedData.filter((line: string) => !existingSet.has(line));
        if (incomingNew.length === 0) return prevLogs;

        return [...prevLogs, ...incomingNew].slice(-2000);
      });

      setRawLogs((prevRaw) => {
        if (!rawData || rawData.length === 0) return prevRaw;
        if (prevRaw.length === 0) return rawData;
        const existingSet = new Set(prevRaw);
        const incomingNew = rawData.filter((line: string) => !existingSet.has(line));
        if (incomingNew.length === 0) return prevRaw;
        return [...prevRaw, ...incomingNew].slice(-2000);
      });
    } catch (err) {
      console.error("Error polling logs:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadLogs();
    const interval = setInterval(loadLogs, 800);

    const handleModeEvt = (e: any) => {
      if (e.detail && e.detail !== mode) {
        const nextMode = e.detail;
        setModeState(nextMode);
        const now = new Date();
        const ts = now.toISOString().replace("T", " ").substring(0, 19);
        const marker = `[${ts}] === SHIELD MODE SWITCHED: ${mode.toUpperCase()} ➔ ${nextMode.toUpperCase()} ===`;
        setLogs((prev) => {
          if (prev.length > 0 && prev[prev.length - 1].includes("=== SHIELD MODE")) return prev;
          return [...prev, marker];
        });
        loadLogs();
      }
    };
    window.addEventListener("logshield-mode-change", handleModeEvt);

    return () => {
      clearInterval(interval);
      window.removeEventListener("logshield-mode-change", handleModeEvt);
    };
  }, [service, isPaused, timeWindow, mode]);

  useEffect(() => {
    if (autoScroll && !isPaused && containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, [logs, rawLogs, autoScroll, isPaused]);

  const handleToggleMode = async () => {
    const newMode = mode === "protected" ? "bypass" : "protected";
    setModeState(newMode);
    
    // Inject marker immediately into local history stream
    const now = new Date();
    const ts = now.toISOString().replace("T", " ").substring(0, 19);
    const marker = `[${ts}] === SHIELD MODE SWITCHED: ${mode.toUpperCase()} ➔ ${newMode.toUpperCase()} ===`;
    setLogs((prev) => [...prev, marker]);

    window.dispatchEvent(new CustomEvent("logshield-mode-change", { detail: newMode }));
    try {
      await setMode(newMode);
      await loadLogs();
    } catch (e) {
      console.error(e);
    }
  };

  const isProtected = mode === "protected";
  const displayLogs = logs.length > 0 ? logs : (isProtected ? logs : rawLogs);

  const filteredLogs = useMemo(() => {
    let result = displayLogs.filter((line) => {
      if (filterQuery && !line.toLowerCase().includes(filterQuery.toLowerCase())) {
        return false;
      }
      if (levelFilter === "REDACTED" && !line.includes("[REDACTED")) return false;
      if (levelFilter === "LEAKS" && !(
        line.includes("postgres://") || 
        line.includes("sk_test_") || 
        line.includes("AKIA") || 
        line.includes("eyJhbGci") || 
        line.includes("AWS_SECRET_ACCESS_KEY") ||
        line.includes("ghp_") ||
        line.includes("JWT123")
      )) return false;
      if (levelFilter === "ERROR" && !line.includes("ERROR")) return false;
      if (levelFilter === "WARN" && !line.includes("WARN")) return false;
      if (levelFilter === "INFO" && !line.includes("INFO")) return false;
      return true;
    });

    if (timeWindow !== "ALL" && result.length > 0) {
      const windowMinutesMap: Record<string, number> = { "5m": 5, "30m": 30, "1h": 60, "6h": 360, "24h": 1440 };
      const minutes = windowMinutesMap[timeWindow] || 5;

      const timestamps = result.map(l => {
        const match = l.match(/(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})/);
        return match ? new Date(match[1]).getTime() : NaN;
      }).filter(t => !isNaN(t));

      if (timestamps.length > 0) {
        const latestTime = Math.max(...timestamps);
        const cutoffTime = latestTime - (minutes * 60 * 1000);
        const timeFiltered = result.filter(l => {
          const match = l.match(/(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})/);
          if (!match) return true;
          return new Date(match[1]).getTime() >= cutoffTime;
        });
        if (timeFiltered.length >= 3) {
          result = timeFiltered;
        } else {
          const sliceSizes: Record<string, number> = { "5m": 30, "30m": 75, "1h": 120, "6h": 200, "24h": 300 };
          result = result.slice(-(sliceSizes[timeWindow] || 50));
        }
      } else {
        const sliceSizes: Record<string, number> = { "5m": 30, "30m": 75, "1h": 120, "6h": 200, "24h": 300 };
        result = result.slice(-(sliceSizes[timeWindow] || 50));
      }
    }

    return result;
  }, [displayLogs, filterQuery, levelFilter, timeWindow]);

  const openTokenInspector = (index: number) => {
    const sanitizedLine = filteredLogs[index] || displayLogs[index] || "";
    const match = sanitizedLine.match(/\[REDACTED:([^:]+):SCS=(\d+)\]/);
    const refId = match ? match[1] : undefined;
    const scsScore = match ? parseInt(match[2], 10) : undefined;

    setInspectItem({
      sanitizedLine,
      service,
      refId,
      scsScore
    });
  };

  const handleExport = () => {
    const blob = new Blob([displayLogs.join("\n")], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `logshield-stream-${service}-${Date.now()}.log`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 bg-white border border-slate-200 p-5 rounded-xl shadow-xs">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-xl font-bold text-slate-900 tracking-tight flex items-center gap-2.5">
              <Terminal className="w-5 h-5 text-blue-600" />
              Live Intercepted Log Stream
            </h1>
            <span className={`px-2.5 py-0.5 rounded-full text-[11px] font-mono font-bold uppercase tracking-wider border ${
              isProtected 
                ? 'bg-emerald-50 text-emerald-700 border-emerald-200' 
                : 'bg-rose-50 text-rose-700 border-rose-200 animate-pulse'
            }`}>
              {isProtected ? "Active Protection: Redacted" : "Bypass Mode: Raw Leak"}
            </span>
          </div>
          <p className="text-slate-500 text-xs mt-1">
            {isProtected
              ? "In-pod LogShield sidecars actively intercept application stderr/stdout pipes. Detected credentials are encrypted into SecureReveal and substituted with irreversible reference tokens."
              : "Bypass simulation active. LogShield sidecars are permitting unredacted logs with exposed credentials to stream directly to logging aggregators."}
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => setIsPaused(!isPaused)}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold border flex items-center gap-1.5 transition-colors ${
              isPaused 
                ? "bg-amber-50 text-amber-700 border-amber-200 hover:bg-amber-100" 
                : "bg-white text-slate-700 border-slate-200 hover:bg-slate-50"
            }`}
          >
            {isPaused ? (
              <>
                <Play className="w-3.5 h-3.5 fill-amber-700" />
                Resume Stream
              </>
            ) : (
              <>
                <Pause className="w-3.5 h-3.5" />
                Pause Stream
              </>
            )}
          </button>

          <button
            onClick={handleExport}
            className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-white text-slate-700 border border-slate-200 hover:bg-slate-50 transition-colors flex items-center gap-1.5 shadow-xs"
          >
            <Download className="w-3.5 h-3.5 text-slate-500" />
            Export Log
          </button>

          <button
            onClick={handleToggleMode}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-bold transition-all shadow-xs flex items-center gap-2 border ${
              isProtected
                ? "bg-rose-50 text-rose-700 border-rose-200 hover:bg-rose-100"
                : "bg-emerald-600 text-white border-emerald-500 hover:bg-emerald-700"
            }`}
          >
            {isProtected ? (
              <>
                <ShieldAlert className="w-4 h-4 text-rose-600" />
                Simulate Bypass
              </>
            ) : (
              <>
                <ShieldCheck className="w-4 h-4 text-white" />
                Enable Protection
              </>
            )}
          </button>
        </div>
      </div>

      {/* Service Selector Tabs & Search Filter */}
      <div className="flex flex-col md:flex-row gap-4 items-center justify-between">
        <div className="flex flex-wrap gap-1.5 w-full md:w-auto">
          {services.map((s) => (
            <button
              key={s.id}
              onClick={() => setService(s.id)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                service === s.id
                  ? "bg-blue-50 text-blue-700 border border-blue-200 font-semibold shadow-xs"
                  : "bg-white text-slate-600 hover:text-slate-900 border border-slate-200 hover:bg-slate-50"
              }`}
            >
              {s.name}
            </button>
          ))}
        </div>

        <div className="flex flex-wrap items-center gap-2 w-full md:w-auto">
          {/* Time Window Filter */}
          <div className="flex items-center gap-1 bg-white border border-slate-200 rounded-lg p-0.5 text-xs shadow-xs">
            <span className="text-[10px] uppercase font-bold text-slate-400 px-1.5 flex items-center gap-1">
              <Clock className="w-3 h-3 text-slate-400" />
              Window:
            </span>
            {[
              { id: "5m", label: "5m" },
              { id: "30m", label: "30m" },
              { id: "1h", label: "1h" },
              { id: "6h", label: "6h" },
              { id: "24h", label: "24h" },
              { id: "ALL", label: "All" },
            ].map((tw) => (
              <button
                key={tw.id}
                onClick={() => setTimeWindow(tw.id)}
                className={`px-2 py-1 rounded text-[11px] font-semibold transition-colors cursor-pointer ${
                  timeWindow === tw.id
                    ? "bg-blue-600 text-white shadow-xs"
                    : "text-slate-600 hover:text-slate-900"
                }`}
              >
                {tw.label}
              </button>
            ))}
          </div>

          {/* Level Filter */}
          <div className="flex items-center gap-1 bg-white border border-slate-200 rounded-lg p-0.5 text-xs shadow-xs">
            {["ALL", "REDACTED", "LEAKS", "ERROR", "INFO"].map((lvl) => (
              <button
                key={lvl}
                onClick={() => setLevelFilter(lvl)}
                className={`px-2.5 py-1 rounded text-[11px] font-semibold transition-colors cursor-pointer ${
                  levelFilter === lvl 
                    ? "bg-slate-900 text-white shadow-xs" 
                    : "text-slate-600 hover:text-slate-900"
                }`}
              >
                {lvl}
              </button>
            ))}
          </div>

          {/* Search Box */}
          <div className="relative flex-1 md:w-60">
            <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Filter by keyword / token..."
              value={filterQuery}
              onChange={(e) => setFilterQuery(e.target.value)}
              className="w-full bg-white border border-slate-200 rounded-lg pl-9 pr-3 py-1.5 text-xs text-slate-800 placeholder-slate-400 focus:outline-none focus:border-blue-500 transition-colors"
            />
          </div>

          {/* Auto Scroll */}
          <button
            onClick={() => setAutoScroll(!autoScroll)}
            className={`px-3 py-1.5 rounded-lg text-xs border font-medium transition-colors ${
              autoScroll 
                ? "bg-slate-100 text-slate-800 border-slate-300 font-semibold" 
                : "bg-white text-slate-500 border-slate-200 hover:bg-slate-50"
            }`}
          >
            Auto-scroll: {autoScroll ? "ON" : "OFF"}
          </button>
        </div>
      </div>

      {/* Log Stream Terminal / Card */}
      <div className="bg-white border border-slate-200 rounded-xl shadow-xs overflow-hidden flex flex-col h-[580px]">
        {/* Stream Status Bar */}
        <div className="bg-slate-50 border-b border-slate-200 px-4 py-2.5 flex items-center justify-between text-xs text-slate-500 font-medium">
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-1.5">
              <span className={`w-2 h-2 rounded-full ${
                isPaused 
                  ? "bg-amber-400" 
                  : isProtected 
                    ? "bg-emerald-500 animate-pulse" 
                    : "bg-rose-500 animate-pulse"
              }`} />
              <span className="font-semibold text-slate-700">
                {isPaused ? "STREAM PAUSED" : isProtected ? "LIVE INTERCEPT PIPELINE" : "RAW BYPASS STREAM"}
              </span>
            </div>
            <span>•</span>
            <span>Target: <code className="text-slate-700 font-mono font-semibold">{service}</code></span>
            <span>•</span>
            <span>Showing: <strong className="text-slate-800">{filteredLogs.length}</strong> lines</span>
          </div>

          <div className="flex items-center gap-2 text-[11px] text-slate-400">
            <span>Buffer: 500 lines</span>
            <span>•</span>
            <span>Format: UTF-8 Line-Delimited</span>
          </div>
        </div>

        {/* Log Lines Container */}
        <div ref={containerRef} className="flex-1 overflow-y-auto p-4 font-mono text-xs bg-slate-900 text-slate-200 space-y-1">
          {loading ? (
            <div className="flex items-center justify-center h-full text-slate-400 gap-2 font-sans text-sm">
              <RefreshCw className="w-4 h-4 animate-spin text-blue-400" />
              Connecting to LogShield Sidecar Stream...
            </div>
          ) : filteredLogs.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-slate-400 gap-2 font-sans py-12">
              <Terminal className="w-8 h-8 opacity-40" />
              <p className="text-xs">No log records found matching current criteria.</p>
            </div>
          ) : (
            filteredLogs.map((log, i) => {
              const isModeMarker = log.includes("=== SHIELD MODE");
              const isRedacted = log.includes("[REDACTED");
              const isFlagged = log.includes("[FLAGGED");
              
              const isRawExposedSecret = 
                log.includes("postgres://") || 
                log.includes("sk_test_") || 
                log.includes("AKIA") || 
                log.includes("eyJhbGci") || 
                log.includes("AWS_SECRET_ACCESS_KEY") ||
                log.includes("ghp_") ||
                log.includes("JWT123");

              const isBypass = log.startsWith("[BYPASS]") || (!isProtected && isRawExposedSecret);

              if (isModeMarker) {
                return (
                  <div 
                    key={i} 
                    className="my-3 py-2 px-4 rounded-xl bg-amber-950/90 border-2 border-amber-500 text-amber-300 font-bold text-center text-xs tracking-wide shadow-md flex items-center justify-center gap-2"
                  >
                    <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0" />
                    <span>{log}</span>
                  </div>
                );
              }

              const cleanLog = log.startsWith("[BYPASS] ") ? log.replace("[BYPASS] ", "") : log;

              return (
                <div 
                  key={i} 
                  className={`group flex items-start gap-3 py-1 px-2.5 rounded transition-colors ${
                    isRedacted 
                      ? 'bg-emerald-950/30 hover:bg-emerald-950/50 border-l-2 border-emerald-500' 
                      : isFlagged
                        ? 'bg-amber-950/30 hover:bg-amber-950/50 border-l-2 border-amber-500'
                        : isRawExposedSecret
                          ? 'bg-rose-950/40 hover:bg-rose-950/60 border-l-2 border-rose-500 animate-pulse'
                          : 'hover:bg-slate-800/60'
                  }`}
                >
                  <span className="text-slate-600 select-none text-[11px] w-8 text-right font-mono shrink-0">
                    {i + 1}
                  </span>

                  <div className="flex-1 break-all leading-relaxed">
                    {isRedacted ? (
                      <div>
                        {cleanLog.split(/(\[REDACTED:[^:]+:SCS=\d+\])/).map((part, pIdx) => {
                          if (part.startsWith("[REDACTED:")) {
                            return (
                              <span 
                                key={pIdx} 
                                onClick={() => openTokenInspector(i)}
                                className="inline-flex items-center gap-1 bg-emerald-500/20 text-emerald-400 px-1.5 py-0.5 rounded font-bold border border-emerald-500/40 mx-0.5 text-[11px] cursor-pointer hover:bg-emerald-500/30 transition-all shadow-xs"
                                title="Click to inspect vaulted token"
                              >
                                <Lock className="w-3 h-3 text-emerald-400" />
                                {part}
                              </span>
                            );
                          }
                          return <span key={pIdx}>{part}</span>;
                        })}
                      </div>
                    ) : isRawExposedSecret ? (
                      <div className="text-rose-300 font-mono">
                        <span className="inline-flex items-center gap-1 bg-rose-500/20 text-rose-400 px-1.5 py-0.5 rounded font-bold border border-rose-500/50 mr-1.5 text-[10px]">
                          <Unlock className="w-3 h-3 text-rose-400" />
                          RAW_EXPOSURE
                        </span>
                        {cleanLog}
                      </div>
                    ) : (
                      <span className="text-slate-300 font-mono">{cleanLog}</span>
                    )}
                  </div>

                  {isRedacted && (
                    <button
                      onClick={() => openTokenInspector(i)}
                      className="opacity-0 group-hover:opacity-100 transition-opacity px-2 py-0.5 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 text-[11px] font-sans flex items-center gap-1.5 shrink-0"
                      title="Inspect Token Details"
                    >
                      <Lock className="w-3 h-3 text-emerald-400" />
                      Token Info
                    </button>
                  )}
                </div>
              );
            })
          )}
        </div>
      </div>

      {/* Secure Token & Interception Inspector Modal */}
      {inspectItem && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 backdrop-blur-xs p-4 animate-in fade-in duration-200">
          <div className="bg-white border border-slate-200 rounded-2xl shadow-xl max-w-2xl w-full p-6 space-y-5 relative">
            <div className="flex items-start justify-between">
              <div>
                <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
                  <ShieldCheck className="w-5 h-5 text-emerald-600" />
                  SecureReveal Token & Interception Inspector
                </h3>
                <p className="text-xs text-slate-500 mt-0.5">
                  Deterministic in-pod token mapping and cryptographic vault isolation status.
                </p>
              </div>
              <button 
                onClick={() => setInspectItem(null)}
                className="text-slate-400 hover:text-slate-600 p-1 rounded-lg hover:bg-slate-100 transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Telemetry Metrics Strip */}
            <div className="grid grid-cols-3 gap-3 bg-slate-50 p-3 rounded-xl border border-slate-200 text-xs">
              <div>
                <span className="text-slate-500 block text-[10px] font-semibold uppercase">Token Ref ID</span>
                <span className="font-mono font-bold text-emerald-700">{inspectItem.refId || "N/A"}</span>
              </div>
              <div>
                <span className="text-slate-500 block text-[10px] font-semibold uppercase">SCS Confidence</span>
                <span className="font-semibold text-slate-900">{inspectItem.scsScore ? `${inspectItem.scsScore}% (High)` : "Standard"}</span>
              </div>
              <div>
                <span className="text-slate-500 block text-[10px] font-semibold uppercase">Interception Cost</span>
                <span className="font-mono font-semibold text-blue-700">3.8 µs (0.0038 ms)</span>
              </div>
            </div>

            {/* Protected Sanitized Output */}
            <div className="space-y-1.5">
              <label className="text-xs font-bold text-emerald-700 uppercase tracking-wider flex items-center gap-1.5">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                Sanitized EmptyDir Volume Stream (Protected)
              </label>
              <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-3 font-mono text-xs text-emerald-900 break-all leading-relaxed select-all">
                {inspectItem.sanitizedLine}
              </div>
            </div>

            {/* Zero-Trust Plaintext Security & Audit Guarantee Card */}
            <div className="bg-slate-50 border border-slate-200 rounded-xl p-4 space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Lock className="w-4 h-4 text-blue-600" />
                  <span className="text-xs font-bold text-slate-800">
                    Plaintext Secret Isolated in Vault (AES-256-GCM)
                  </span>
                </div>
                <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">
                  ZERO EXPOSURE
                </span>
              </div>
              
              <p className="text-xs text-slate-500 leading-relaxed">
                To guarantee non-repudiation and prevent unmonitored credential exposure, raw secret plaintext is never rendered in log streams or viewer modals. Plaintext decryption requires secondary role-based authentication and is permanently recorded in the SHA-256 forensic audit ledger.
              </p>

              <div className="pt-2 border-t border-slate-200 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
                <span className="text-[11px] text-slate-400 font-mono">
                  Audit Policy: <strong className="text-slate-700">REVEAL_REQUEST</strong> logged
                </span>

                <Link
                  href="/vault"
                  className="px-3.5 py-1.5 rounded-lg text-xs font-semibold bg-blue-600 hover:bg-blue-700 text-white transition-colors flex items-center gap-1.5 shadow-xs"
                >
                  <KeyRound className="w-3.5 h-3.5" />
                  Authenticate in Vault to Decrypt
                </Link>
              </div>
            </div>

            {/* Modal Actions */}
            <div className="flex items-center justify-between pt-2 border-t border-slate-100">
              <span className="text-xs text-slate-500">
                Token mapped deterministically via in-pod AES-256 key.
              </span>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => copyToClipboard(inspectItem.sanitizedLine)}
                  className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-white border border-slate-200 hover:bg-slate-50 text-slate-700 flex items-center gap-1.5 transition-colors shadow-xs"
                >
                  {copied ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5 text-slate-500" />}
                  {copied ? "Copied" : "Copy Sanitized"}
                </button>
                <button
                  onClick={() => setInspectItem(null)}
                  className="px-4 py-1.5 rounded-lg text-xs font-semibold bg-slate-900 hover:bg-slate-800 text-white transition-colors"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
