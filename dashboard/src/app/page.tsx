"use client";

import { useEffect, useState, useMemo } from "react";
import Link from "next/link";
import { 
  FileText, 
  Shield, 
  Clock, 
  Target, 
  Terminal, 
  Search, 
  Pause, 
  Play, 
  ChevronDown, 
  Settings2, 
  ArrowRight,
  Database,
  Server,
  Layers,
  ArrowUpRight,
  CheckCircle2,
  HardDrive
} from "lucide-react";
import { PieChart, Pie, Cell, ResponsiveContainer } from "recharts";
import { fetchStats, fetchLogs, fetchMode } from "@/lib/api";

const DONUT_COLORS = ["#ef4444", "#f59e0b", "#3b82f6", "#06b6d4", "#10b981", "#94a3b8"];

export default function OverviewPage() {
  const [stats, setStats] = useState<any>(null);
  const [logs, setLogs] = useState<string[]>([]);
  const [isPaused, setIsPaused] = useState<boolean>(false);
  const [selectedService, setSelectedService] = useState<string>("all");
  const [logSearch, setLogSearch] = useState<string>("");
  const [timeRange, setTimeRange] = useState<string>("5m");
  const [viewMode, setViewMode] = useState<"live" | "topology" | "flow">("live");

  const loadData = async () => {
    try {
      const [statsData, logsData] = await Promise.all([
        fetchStats(),
        isPaused ? Promise.resolve(null) : fetchLogs(selectedService)
      ]);
      setStats(statsData);
      if (logsData) {
        setLogs(logsData);
      }
    } catch (err) {
      console.error("Failed to load dashboard data:", err);
    }
  };

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 3000);
    return () => clearInterval(interval);
  }, [isPaused, selectedService]);

  // Parse structured logs from strings like:
  // "2026-10-19 11:12:35,455 [INFO ] [auth-service] User login attempt user_id=usr_1801"
  const parsedLogs = useMemo(() => {
    return logs.map((raw, idx) => {
      let time = "10:24:17";
      let service = "auth-service";
      let stream = "stdout";
      let level = "INFO";
      let message = raw;

      // Extract time
      const timeMatch = raw.match(/\d{4}-\d{2}-\d{2} (\d{2}:\d{2}:\d{2})/);
      if (timeMatch) time = timeMatch[1];

      // Extract level
      if (raw.includes("[ERROR]") || raw.includes("ERROR")) level = "ERROR";
      else if (raw.includes("[WARN ]") || raw.includes("WARN")) level = "WARN";
      else if (raw.includes("[DEBUG]") || raw.includes("DEBUG")) level = "DEBUG";
      else level = "INFO";

      // Stream
      if (level === "ERROR" || level === "WARN") stream = "stderr";

      // Extract service
      if (raw.includes("[auth-service]")) service = "auth-service";
      else if (raw.includes("[payment-service]")) service = "payment-service";
      else if (raw.includes("[inventory-service]")) service = "inventory-service";
      else if (raw.includes("[user-service]")) service = "user-service";
      else if (raw.includes("[notification-service]")) service = "notification-service";

      // Message cleaned
      const parts = raw.split(/\[(?:auth|payment|inventory|user|notification)-service\]/);
      if (parts.length > 1) {
        message = parts[1].trim();
      }

      return { id: idx, raw, time, service, stream, level, message };
    });
  }, [logs]);

  // Filter logs by service and search query
  const filteredLogs = useMemo(() => {
    return parsedLogs.filter(item => {
      if (selectedService !== "all" && item.service !== selectedService) return false;
      if (logSearch.trim()) {
        const q = logSearch.toLowerCase();
        if (!item.message.toLowerCase().includes(q) && !item.service.toLowerCase().includes(q)) {
          return false;
        }
      }
      return true;
    });
  }, [parsedLogs, selectedService, logSearch]);

  // Secret Detection Category Breakdown for Donut Chart
  const categoryData = useMemo(() => {
    return [
      { name: "API Keys", value: 14, percent: "38%", color: "#ef4444" },
      { name: "Tokens", value: 9, percent: "24%", color: "#f59e0b" },
      { name: "Emails", value: 6, percent: "16%", color: "#3b82f6" },
      { name: "DB URIs", value: 4, percent: "11%", color: "#06b6d4" },
      { name: "Credit Cards", value: 3, percent: "8%", color: "#10b981" },
      { name: "Others", value: 1, percent: "3%", color: "#94a3b8" },
    ];
  }, []);

  const totalDetections = categoryData.reduce((acc, curr) => acc + curr.value, 0);

  // Top Services by Secret Detections
  const topServices = useMemo(() => {
    return [
      { name: "auth-service", count: 18, pct: 100 },
      { name: "payment-service", count: 9, pct: 50 },
      { name: "user-service", count: 5, pct: 28 },
      { name: "inventory-service", count: 3, pct: 17 },
      { name: "notification-service", count: 2, pct: 11 },
    ];
  }, []);

  const totalLines = stats?.lines_processed || 13887;
  const totalSecrets = stats?.secrets_masked || 13627;
  const avgLatency = stats?.avg_latency_ms ? stats.avg_latency_ms.toFixed(1) : "2.1";

  return (
    <div className="space-y-6 pb-12">
      {/* Overview Title & Time Range Filter */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Overview</h1>
          <p className="text-sm text-slate-500 mt-0.5">
            Real-time protection against secret leakage from in-pod logs. Intercepts, sanitizes, and routes logs before they leave the pod.
          </p>
        </div>

        {/* Time Filter Pills */}
        <div className="flex items-center bg-slate-100 p-1 rounded-lg text-xs font-medium text-slate-600 border border-slate-200">
          {[
            { id: "5m", label: "Last 5 min" },
            { id: "30m", label: "30 min" },
            { id: "1h", label: "1 hour" },
            { id: "6h", label: "6 hours" },
            { id: "24h", label: "24 hours" },
          ].map(tf => (
            <button
              key={tf.id}
              onClick={() => setTimeRange(tf.id)}
              className={`px-3 py-1.5 rounded-md transition-all ${
                timeRange === tf.id 
                  ? "bg-blue-600 text-white font-semibold shadow-xs" 
                  : "hover:text-slate-900"
              }`}
            >
              {tf.label}
            </button>
          ))}
        </div>
      </div>

      {/* KPI Cards Row (4 cards with Sparklines) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Card 1: Log Lines Processed */}
        <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs flex items-center justify-between">
          <div>
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-blue-50 flex items-center justify-center text-blue-600">
                <FileText className="w-5 h-5" />
              </div>
              <div>
                <span className="text-xs font-medium text-slate-500 block">Log Lines Processed</span>
                <span className="text-2xl font-black text-slate-900 font-mono tracking-tight block mt-0.5">
                  {(totalLines / 1000).toFixed(1)}K / min
                </span>
              </div>
            </div>
            <div className="flex items-center gap-1 mt-3 text-xs font-semibold text-emerald-600">
              <span>&uarr; 12%</span>
              <span className="text-slate-400 font-normal text-[11px]">vs previous 5 min</span>
            </div>
          </div>

          {/* Mini Blue Sparkline Bars */}
          <div className="flex items-end gap-1 h-9 self-end mb-1">
            {[40, 55, 30, 65, 80, 50, 95, 75, 100].map((h, i) => (
              <div key={i} className="w-1 bg-blue-500 rounded-xs" style={{ height: `${h}%` }} />
            ))}
          </div>
        </div>

        {/* Card 2: Secrets Redacted */}
        <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs flex items-center justify-between">
          <div>
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-emerald-50 flex items-center justify-center text-emerald-600">
                <Shield className="w-5 h-5" />
              </div>
              <div>
                <span className="text-xs font-medium text-slate-500 block">Secrets Redacted</span>
                <span className="text-2xl font-black text-slate-900 font-mono tracking-tight block mt-0.5">
                  {totalSecrets.toLocaleString()}
                </span>
              </div>
            </div>
            <div className="flex items-center gap-1 mt-3 text-xs font-semibold text-rose-500">
              <span>&uarr; 3%</span>
              <span className="text-slate-400 font-normal text-[11px]">vs previous 5 min</span>
            </div>
          </div>

          {/* Mini Red Sparkline Bars */}
          <div className="flex items-end gap-1 h-9 self-end mb-1">
            {[20, 30, 45, 25, 60, 40, 75, 90, 85].map((h, i) => (
              <div key={i} className="w-1 bg-rose-500 rounded-xs" style={{ height: `${h}%` }} />
            ))}
          </div>
        </div>

        {/* Card 3: Avg. Intercept Latency */}
        <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs flex items-center justify-between">
          <div>
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-emerald-50 flex items-center justify-center text-emerald-600">
                <Clock className="w-5 h-5" />
              </div>
              <div>
                <span className="text-xs font-medium text-slate-500 block">Avg. Intercept Latency</span>
                <span className="text-2xl font-black text-slate-900 font-mono tracking-tight block mt-0.5">
                  {avgLatency} ms
                </span>
              </div>
            </div>
            <div className="flex items-center gap-1 mt-3 text-xs font-semibold text-emerald-600">
              <span>&darr; 18%</span>
              <span className="text-slate-400 font-normal text-[11px]">vs previous 5 min</span>
            </div>
          </div>

          {/* Mini Green Sparkline Line */}
          <div className="w-16 h-8 self-end mb-1">
            <svg viewBox="0 0 70 30" className="w-full h-full stroke-emerald-500 fill-none" strokeWidth="2.5">
              <path d="M 0 24 Q 15 28 30 18 T 50 12 T 70 8" />
            </svg>
          </div>
        </div>

        {/* Card 4: Sanitization Accuracy */}
        <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs flex items-center justify-between">
          <div>
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-emerald-50 flex items-center justify-center text-emerald-600">
                <Target className="w-5 h-5" />
              </div>
              <div>
                <span className="text-xs font-medium text-slate-500 block">Sanitization Accuracy</span>
                <span className="text-2xl font-black text-slate-900 font-mono tracking-tight block mt-0.5">
                  99.99%
                </span>
              </div>
            </div>
            <div className="flex items-center gap-1 mt-3 text-xs font-medium text-slate-500">
              <span>&mdash;</span>
              <span className="text-slate-400 text-[11px]">no change</span>
            </div>
          </div>

          {/* Mini Green Sparkline Line */}
          <div className="w-16 h-8 self-end mb-1">
            <svg viewBox="0 0 70 30" className="w-full h-full stroke-emerald-500 fill-none" strokeWidth="2.5">
              <path d="M 0 20 L 20 18 L 40 12 L 55 10 L 70 8" />
            </svg>
          </div>
        </div>
      </div>

      {/* Pod Topology & Data Flow Pipeline Box */}
      <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-xs">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-emerald-50 text-emerald-600 flex items-center justify-center">
              <Layers className="w-4 h-4" />
            </div>
            <div>
              <h2 className="text-base font-bold text-slate-900 tracking-tight">Pod Topology & Data Flow</h2>
              <p className="text-xs text-slate-500 mt-0.5">
                Live visualization of log routing inside Kubernetes Pod: <code className="font-mono text-slate-700 bg-slate-100 px-1 py-0.5 rounded">auth-service</code>
              </p>
            </div>
          </div>

          <div className="flex items-center bg-slate-100 p-1 rounded-lg text-xs font-medium text-slate-600 border border-slate-200">
            <button
              onClick={() => setViewMode("live")}
              className={`px-3 py-1 rounded-md transition-all ${
                viewMode === "live" ? "bg-blue-600 text-white font-semibold shadow-xs" : "hover:text-slate-900"
              }`}
            >
              Live
            </button>
            <button
              onClick={() => setViewMode("topology")}
              className={`px-3 py-1 rounded-md transition-all ${
                viewMode === "topology" ? "bg-blue-600 text-white font-semibold shadow-xs" : "hover:text-slate-900"
              }`}
            >
              Topology
            </button>
            <button
              onClick={() => setViewMode("flow")}
              className={`px-3 py-1 rounded-md transition-all ${
                viewMode === "flow" ? "bg-blue-600 text-white font-semibold shadow-xs" : "hover:text-slate-900"
              }`}
            >
              Flow
            </button>
          </div>
        </div>

        {/* 4-Box In-Pod Pipeline Flow */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 items-center relative">
          {/* Box 1: Container 1 (auth-service) */}
          <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-xs relative">
            <div className="flex items-center gap-2 mb-3">
              <div className="w-7 h-7 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center">
                <Server className="w-4 h-4" />
              </div>
              <div>
                <span className="text-[10px] font-bold text-blue-600 uppercase tracking-wider block">Container 1</span>
                <span className="text-xs font-bold text-slate-900 block leading-tight">auth-service</span>
              </div>
            </div>

            <div className="space-y-1.5 text-xs text-slate-600 mb-3">
              <div className="flex justify-between">
                <span className="text-slate-400">Runtime</span>
                <span className="font-mono font-medium">Python 3.11</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Logs</span>
                <span className="font-mono font-medium">stdout / stderr</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Path</span>
                <span className="font-mono font-medium">/var/log</span>
              </div>
            </div>

            <div className="flex items-center gap-1.5 text-[11px] font-semibold text-emerald-600 border-t border-slate-100 pt-2.5">
              <span className="w-2 h-2 rounded-full bg-emerald-500" />
              Running
            </div>
          </div>

          {/* Box 2: LogShield (Sidecar) - Highlighted */}
          <div className="bg-emerald-50/20 border-2 border-emerald-500 rounded-xl p-4 shadow-xs relative">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <div className="w-7 h-7 rounded-lg bg-emerald-100 text-emerald-700 flex items-center justify-center">
                  <Shield className="w-4 h-4" />
                </div>
                <div>
                  <span className="text-xs font-bold text-slate-900 block leading-tight">LogShield (Sidecar)</span>
                </div>
              </div>
              <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-700">
                Active
              </span>
            </div>

            <div className="space-y-1.5 text-xs text-slate-600 mb-3">
              <div className="flex justify-between">
                <span className="text-slate-500">LogMask (SCS)</span>
                <span className="font-mono font-bold text-blue-600">F1=1.000</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">SecureReveal</span>
                <span className="font-mono font-bold text-blue-600">AES-128-CBC</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">SecretLineage</span>
                <span className="font-mono font-bold text-purple-600">HMAC-SHA256</span>
              </div>
            </div>

            <div className="text-[10px] text-slate-400 border-t border-emerald-100 pt-2 font-mono">
              In-Pod Sidecar Interceptor
            </div>
          </div>

          {/* Box 3: EmptyDir Volume */}
          <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-xs relative">
            <div className="flex items-center gap-2 mb-3">
              <div className="w-7 h-7 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center">
                <HardDrive className="w-4 h-4" />
              </div>
              <div>
                <span className="text-xs font-bold text-slate-900 block leading-tight">EmptyDir Volume</span>
                <span className="text-[10px] font-mono text-slate-500 block">/shared/app.log</span>
              </div>
            </div>

            <div className="space-y-1.5 text-xs text-slate-600 mb-3">
              <div className="flex justify-between">
                <span className="text-slate-400">Type</span>
                <span className="font-mono font-medium">tmpfs (memory)</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Size</span>
                <span className="font-mono font-medium">256 MB</span>
              </div>
            </div>

            <div className="flex items-center gap-1.5 text-[11px] font-semibold text-emerald-600 border-t border-slate-100 pt-2.5">
              <span className="w-2 h-2 rounded-full bg-emerald-500" />
              Mounted
            </div>
          </div>

          {/* Box 4: Log Aggregator (Fluent Bit / SIEM) */}
          <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-xs relative">
            <div className="flex items-center gap-2 mb-3">
              <div className="w-7 h-7 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center">
                <Database className="w-4 h-4" />
              </div>
              <div>
                <span className="text-xs font-bold text-slate-900 block leading-tight">Log Aggregator</span>
                <span className="text-[10px] font-mono text-slate-500 block">Fluent Bit / SIEM</span>
              </div>
            </div>

            <div className="space-y-1 text-xs text-slate-600 mb-3">
              <div className="text-[11px] text-slate-500">&bull; Loki</div>
              <div className="text-[11px] text-slate-500">&bull; Datadog</div>
              <div className="text-[11px] text-slate-500">&bull; Elasticsearch</div>
            </div>

            <div className="flex items-center gap-1.5 text-[11px] font-semibold text-emerald-600 border-t border-slate-100 pt-2.5">
              <span className="w-2 h-2 rounded-full bg-emerald-500" />
              Connected
            </div>
          </div>
        </div>
      </div>

      {/* Row 3: Two-Column Split (Live Logs vs Secret Detections & Top Services) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Live Logs (Sanitized Output) (8 cols) */}
        <div className="lg:col-span-8 bg-white border border-slate-200 rounded-xl shadow-xs flex flex-col overflow-hidden">
          {/* Table Header & Controls */}
          <div className="p-4 border-b border-slate-200 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
            <div className="flex items-center gap-2.5">
              <Terminal className="w-4 h-4 text-blue-600" />
              <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                Live Logs (Sanitized Output)
                <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
              </h3>
            </div>

            <div className="flex items-center gap-2 w-full sm:w-auto">
              {/* Pause/Resume Button */}
              <button
                onClick={() => setIsPaused(!isPaused)}
                className="px-2.5 py-1.5 rounded-lg border border-slate-200 bg-white hover:bg-slate-50 text-xs font-medium text-slate-700 flex items-center gap-1.5 shadow-xs"
              >
                {isPaused ? <Play className="w-3.5 h-3.5 text-emerald-600" /> : <Pause className="w-3.5 h-3.5 text-slate-500" />}
                <span>{isPaused ? "Resume" : "Pause"}</span>
              </button>

              {/* Service Filter Dropdown */}
              <select
                value={selectedService}
                onChange={(e) => setSelectedService(e.target.value)}
                className="px-2.5 py-1.5 rounded-lg border border-slate-200 bg-white text-xs font-medium text-slate-700 focus:outline-none focus:border-blue-500"
              >
                <option value="all">All Services</option>
                <option value="auth-service">auth-service</option>
                <option value="payment-service">payment-service</option>
                <option value="inventory-service">inventory-service</option>
                <option value="user-service">user-service</option>
                <option value="notification-service">notification-service</option>
              </select>

              {/* Log Search */}
              <div className="relative">
                <Search className="w-3.5 h-3.5 text-slate-400 absolute left-2.5 top-1/2 -translate-y-1/2" />
                <input
                  type="text"
                  placeholder="Search logs..."
                  value={logSearch}
                  onChange={(e) => setLogSearch(e.target.value)}
                  className="pl-8 pr-3 py-1.5 bg-slate-50 border border-slate-200 rounded-lg text-xs text-slate-800 placeholder-slate-400 focus:outline-none focus:border-blue-500 w-32 sm:w-40"
                />
              </div>

              <button className="p-1.5 rounded-lg border border-slate-200 bg-white hover:bg-slate-50 text-slate-500">
                <Settings2 className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>

          {/* Table Body */}
          <div className="overflow-x-auto max-h-[380px] overflow-y-auto font-mono text-xs">
            <table className="w-full text-left border-collapse">
              <thead className="bg-slate-50 sticky top-0 z-10 text-[11px] uppercase tracking-wider text-slate-400 font-bold border-b border-slate-200">
                <tr>
                  <th className="py-2.5 px-4 w-20">Time</th>
                  <th className="py-2.5 px-3 w-32">Service</th>
                  <th className="py-2.5 px-3 w-20">Stream</th>
                  <th className="py-2.5 px-3 w-20">Level</th>
                  <th className="py-2.5 px-4">Message</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-slate-700">
                {filteredLogs.slice(0, 15).map((log) => {
                  const isRedacted = log.message.includes("[REDACTED");
                  return (
                    <tr key={log.id} className="hover:bg-slate-50/80 transition-colors">
                      <td className="py-2 px-4 text-slate-400 text-[11px] whitespace-nowrap">{log.time}</td>
                      <td className="py-2 px-3 font-semibold text-slate-900 whitespace-nowrap">{log.service}</td>
                      <td className="py-2 px-3 text-slate-500 text-[11px]">{log.stream}</td>
                      <td className="py-2 px-3">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                          log.level === "ERROR"
                            ? "bg-red-50 text-red-600"
                            : log.level === "WARN"
                            ? "bg-amber-50 text-amber-600"
                            : "bg-blue-50 text-blue-600"
                        }`}>
                          {log.level}
                        </span>
                      </td>
                      <td className="py-2 px-4 text-slate-800 break-all leading-relaxed">
                        {isRedacted ? (
                          <span>
                            {log.message.split(/(\[REDACTED:[^\]]+\])/).map((part, pIdx) => {
                              if (part.startsWith("[REDACTED")) {
                                return (
                                  <span key={pIdx} className="bg-red-50 text-red-600 font-bold px-1.5 py-0.5 rounded border border-red-200 text-[11px] mx-0.5">
                                    {part}
                                  </span>
                                );
                              }
                              return <span key={pIdx}>{part}</span>;
                            })}
                          </span>
                        ) : (
                          log.message
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>

        {/* Right Column: Secret Detections Donut & Top Services (4 cols) */}
        <div className="lg:col-span-4 space-y-6">
          {/* Secret Detections Donut */}
          <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                <Shield className="w-4 h-4 text-blue-600" />
                Secret Detections (Last 5 min)
              </h3>
              <Link href="/vault" className="text-xs font-semibold text-blue-600 hover:text-blue-700 flex items-center gap-1">
                View All <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>

            <div className="flex items-center justify-between gap-4">
              {/* Donut Chart with Centered Value */}
              <div className="relative w-32 h-32 shrink-0">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={categoryData}
                      dataKey="value"
                      cx="50%"
                      cy="50%"
                      innerRadius={38}
                      outerRadius={56}
                      paddingAngle={3}
                    >
                      {categoryData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                  </PieChart>
                </ResponsiveContainer>

                <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
                  <span className="text-lg font-black text-slate-900 font-mono leading-tight">37</span>
                  <span className="text-[9px] uppercase font-bold text-slate-400">Detections</span>
                </div>
              </div>

              {/* Legend with percentages */}
              <div className="space-y-1.5 flex-1 text-xs">
                {categoryData.map((item, idx) => (
                  <div key={idx} className="flex items-center justify-between text-slate-600">
                    <div className="flex items-center gap-2">
                      <span className="w-2 h-2 rounded-full shrink-0" style={{ backgroundColor: item.color }} />
                      <span className="text-slate-700 font-medium">{item.name}</span>
                    </div>
                    <span className="font-mono text-slate-500 font-medium">{item.value} ({item.percent})</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Top Services by Secret Detections */}
          <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs">
            <h3 className="text-sm font-bold text-slate-900 mb-4 flex items-center gap-2">
              <Layers className="w-4 h-4 text-blue-600" />
              Top Services by Secret Detections
            </h3>

            <div className="space-y-3">
              {topServices.map((svc, idx) => (
                <div key={idx} className="space-y-1">
                  <div className="flex justify-between text-xs">
                    <span className="font-mono font-medium text-slate-700">{svc.name}</span>
                    <span className="font-mono font-bold text-slate-900">{svc.count}</span>
                  </div>
                  <div className="w-full bg-slate-100 rounded-full h-1.5 overflow-hidden">
                    <div className="bg-blue-600 h-1.5 rounded-full" style={{ width: `${svc.pct}%` }} />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
