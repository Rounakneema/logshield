"use client";

import { useEffect, useState, useMemo } from "react";
import { 
  Network, 
  ServerCrash, 
  Share2, 
  ShieldAlert, 
  ShieldCheck, 
  AlertTriangle, 
  CheckCircle2, 
  Layers, 
  Clock, 
  RefreshCw,
  Hash,
  Activity,
  Zap,
  Search,
  Copy,
  Check,
  ChevronRight,
  Terminal,
  Eye,
  X
} from "lucide-react";
import { fetchSprawl } from "@/lib/api";

interface PropagationStep {
  step: number;
  service: string;
  pod_name: string;
  namespace: string;
  first_seen: number;
  last_seen: number;
  occurrences: number;
  is_origin: boolean;
}

interface LineageRecord {
  fingerprint: string;
  full_fingerprint: string;
  pod_count: number;
  pods: string[];
  services: string[];
  service_count: number;
  origin_service: string;
  origin_pod: string;
  sprawled_to: string[];
  is_sprawled: boolean;
  first_seen: number;
  last_seen: number;
  age_days: number;
  occurrences: number;
  is_registered: boolean;
  risk_score: number;
  severity: "CRITICAL" | "HIGH" | "MEDIUM" | "LOW";
  secret_type: string;
  propagation_path: PropagationStep[];
}

const SERVICE_COORDINATES: Record<string, { x: number; y: number; color: string; label: string }> = {
  "auth-service": { x: 400, y: 70, color: "#2563eb", label: "Auth API" },
  "payment-service": { x: 650, y: 160, color: "#0891b2", label: "Payment API" },
  "inventory-service": { x: 560, y: 300, color: "#7c3aed", label: "Inventory API" },
  "user-service": { x: 240, y: 300, color: "#059669", label: "User API" },
  "notification-service": { x: 150, y: 160, color: "#d97706", label: "Notification API" },
};

export default function SprawlPage() {
  const [reports, setReports] = useState<LineageRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [copiedFp, setCopiedFp] = useState<string | null>(null);
  const [copiedCmd, setCopiedCmd] = useState<string | null>(null);
  const [selectedService, setSelectedService] = useState<string>("all");
  const [selectedFilter, setSelectedFilter] = useState<"all" | "sprawled" | "isolated" | "critical">("all");
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [activeDossier, setActiveDossier] = useState<LineageRecord | null>(null);

  const loadData = async () => {
    try {
      const data = await fetchSprawl();
      const normalized: LineageRecord[] = (Array.isArray(data) ? data : []).map((item: any) => {
        const pods = item.pods || [item.origin_pod || "auth-service-pod"];
        const services = item.services || Array.from(new Set(pods.map((p: string) => {
          if (p.includes("auth")) return "auth-service";
          if (p.includes("payment")) return "payment-service";
          if (p.includes("inventory")) return "inventory-service";
          if (p.includes("user")) return "user-service";
          if (p.includes("notification")) return "notification-service";
          return p.split("-")[0] + "-service";
        })));
        
        const originService = item.origin_service || services[0] || "auth-service";
        const sprawledTo = item.sprawled_to || services.filter((s: string) => s !== originService);
        const serviceCount = services.length;

        return {
          ...item,
          full_fingerprint: item.full_fingerprint || item.fingerprint,
          pods,
          services,
          service_count: serviceCount,
          origin_service: originService,
          origin_pod: item.origin_pod || pods[0] || "unknown-pod",
          sprawled_to: sprawledTo,
          is_sprawled: serviceCount > 1,
          secret_type: item.secret_type || (
            originService.includes("payment") ? "STRIPE_API_KEY" :
            originService.includes("inventory") ? "AWS_ACCESS_KEY" :
            originService.includes("auth") ? "POSTGRES_DB_URI" :
            originService.includes("user") ? "JWT_BEARER_TOKEN" :
            originService.includes("notification") ? "TWILIO_AUTH_TOKEN" : "GENERIC_API_KEY"
          ),
          propagation_path: item.propagation_path || services.map((s: string, idx: number) => ({
            step: idx + 1,
            service: s,
            pod_name: pods[idx] || `${s}-instance`,
            namespace: "logshield-protected",
            first_seen: item.first_seen || Math.floor(Date.now() / 1000) - (services.length - idx) * 10,
            last_seen: item.last_seen || Math.floor(Date.now() / 1000),
            occurrences: Math.round((item.occurrences || 1) / services.length) || 1,
            is_origin: idx === 0
          }))
        };
      });

      setReports(normalized);
    } catch (err) {
      console.error("Failed to load sprawl reports:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 5000);
    return () => clearInterval(interval);
  }, []);

  const copyToClipboard = (text: string, type: "fp" | "cmd") => {
    navigator.clipboard.writeText(text);
    if (type === "fp") {
      setCopiedFp(text);
      setTimeout(() => setCopiedFp(null), 2000);
    } else {
      setCopiedCmd(text);
      setTimeout(() => setCopiedCmd(null), 2000);
    }
  };

  // KPI Calculations
  const totalLineages = reports.length;
  const multiServiceSprawls = reports.filter(r => r.service_count > 1).length;
  const shadowSecrets = reports.filter(r => !r.is_registered).length;
  const criticalCount = reports.filter(r => r.severity === "CRITICAL" || r.risk_score >= 12).length;
  const maxBlastRadius = reports.reduce((acc, r) => Math.max(acc, r.service_count || 1), 0);

  // Filtered List
  const filteredReports = useMemo(() => {
    return reports.filter(report => {
      if (selectedService !== "all" && !report.services.includes(selectedService)) {
        return false;
      }
      if (selectedFilter === "sprawled" && !report.is_sprawled) return false;
      if (selectedFilter === "isolated" && report.is_sprawled) return false;
      if (selectedFilter === "critical" && report.severity !== "CRITICAL") return false;
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase();
        const matchesFp = report.fingerprint.toLowerCase().includes(q) || report.full_fingerprint.toLowerCase().includes(q);
        const matchesType = report.secret_type.toLowerCase().includes(q);
        const matchesPods = report.pods.some(p => p.toLowerCase().includes(q));
        const matchesSvc = report.services.some(s => s.toLowerCase().includes(q));
        if (!matchesFp && !matchesType && !matchesPods && !matchesSvc) return false;
      }
      return true;
    });
  }, [reports, selectedService, selectedFilter, searchQuery]);

  // Topology Edges computation: aggregate cross-service sprawls
  const topologyEdges = useMemo(() => {
    const edgeMap: Record<string, { source: string; target: string; count: number; secrets: string[] }> = {};

    reports.forEach(r => {
      if (!r.is_sprawled) return;
      const origin = r.origin_service;
      r.sprawled_to.forEach(target => {
        if (!SERVICE_COORDINATES[origin] || !SERVICE_COORDINATES[target]) return;
        const key = [origin, target].sort().join("---");
        if (!edgeMap[key]) {
          edgeMap[key] = { source: origin, target, count: 0, secrets: [] };
        }
        edgeMap[key].count += r.occurrences;
        if (!edgeMap[key].secrets.includes(r.fingerprint)) {
          edgeMap[key].secrets.push(r.fingerprint);
        }
      });
    });

    return Object.values(edgeMap);
  }, [reports]);

  // Service stats
  const serviceStats = useMemo(() => {
    const stats: Record<string, { total: number; origin: number; contaminated: number }> = {};
    Object.keys(SERVICE_COORDINATES).forEach(s => {
      stats[s] = { total: 0, origin: 0, contaminated: 0 };
    });

    reports.forEach(r => {
      r.services.forEach(s => {
        if (stats[s]) {
          stats[s].total += 1;
          if (r.origin_service === s) {
            stats[s].origin += 1;
          } else {
            stats[s].contaminated += 1;
          }
        }
      });
    });
    return stats;
  }, [reports]);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 bg-white border border-slate-200 p-5 rounded-xl shadow-xs">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-xl font-bold text-slate-900 tracking-tight flex items-center gap-2.5">
              <Network className="w-5 h-5 text-blue-600" />
              Secret Lineage & Sprawl Topology
            </h1>
            <span className="px-2.5 py-0.5 rounded-full text-[11px] font-mono font-bold uppercase tracking-wider bg-blue-50 text-blue-700 border border-blue-200">
              HMAC-SHA256 Fingerprinted
            </span>
          </div>
          <p className="text-slate-500 text-xs mt-1">
            Tracks secret proliferation across microservices using blind HMAC-SHA256 signatures. Identifies Patient Zero origin services, maps lateral contamination pathways, and isolates shadow credentials.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={loadData}
            className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-blue-600 hover:bg-blue-700 text-white transition-colors flex items-center gap-1.5 shadow-xs"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} />
            Refresh Topology
          </button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        <div className="bg-white border border-slate-200 p-4 rounded-xl shadow-xs">
          <span className="text-slate-500 text-xs font-medium block">Tracked Lineages</span>
          <div className="mt-1 flex items-baseline gap-2">
            <span className="text-2xl font-bold text-slate-900">{totalLineages}</span>
            <span className="text-xs text-blue-600 font-mono">HMAC Blind</span>
          </div>
        </div>

        <div className="bg-white border border-slate-200 p-4 rounded-xl shadow-xs">
          <span className="text-slate-500 text-xs font-medium block">Cross-Pod Sprawls</span>
          <div className="mt-1 flex items-baseline gap-2">
            <span className="text-2xl font-bold text-amber-600">{multiServiceSprawls}</span>
            <span className="text-xs text-amber-700 font-semibold">Multi-Service</span>
          </div>
        </div>

        <div className="bg-white border border-slate-200 p-4 rounded-xl shadow-xs">
          <span className="text-slate-500 text-xs font-medium block">Max Blast Radius</span>
          <div className="mt-1 flex items-baseline gap-2">
            <span className="text-2xl font-bold text-slate-900">{maxBlastRadius} Services</span>
            <span className="text-xs text-slate-500">Cluster Wide</span>
          </div>
        </div>

        <div className="bg-white border border-slate-200 p-4 rounded-xl shadow-xs">
          <span className="text-slate-500 text-xs font-medium block">Shadow Secrets</span>
          <div className="mt-1 flex items-baseline gap-2">
            <span className="text-2xl font-bold text-rose-600">{shadowSecrets}</span>
            <span className="text-xs text-rose-600 font-semibold">Unregistered</span>
          </div>
        </div>

        <div className="bg-white border border-slate-200 p-4 rounded-xl shadow-xs">
          <span className="text-slate-500 text-xs font-medium block">Critical Risk Alerts</span>
          <div className="mt-1 flex items-baseline gap-2">
            <span className="text-2xl font-bold text-rose-700">{criticalCount}</span>
            <span className="text-xs text-rose-600 font-semibold">Risk ≥ 12.0</span>
          </div>
        </div>
      </div>

      {/* Interactive Topology Graph Visualizer */}
      <div className="bg-white border border-slate-200 p-5 rounded-xl shadow-xs space-y-4">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <div>
            <h2 className="text-sm font-bold text-slate-900 uppercase tracking-wider flex items-center gap-2">
              <Activity className="w-4 h-4 text-blue-600" />
              Microservice Mesh Sprawl Topology
            </h2>
            <p className="text-xs text-slate-500 mt-0.5">
              Live inter-service credential propagation vectors. Click any node to filter lineages for that microservice.
            </p>
          </div>

          {selectedService !== "all" && (
            <button
              onClick={() => setSelectedService("all")}
              className="text-xs px-2.5 py-1 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg border border-slate-200 flex items-center gap-1.5 transition-colors font-medium"
            >
              <X className="w-3.5 h-3.5" />
              Reset Service Filter ({selectedService})
            </button>
          )}
        </div>

        {/* SVG Mesh Canvas */}
        <div className="relative w-full bg-slate-50 rounded-xl border border-slate-200 p-4 overflow-hidden">
          <svg viewBox="0 0 800 370" className="w-full h-auto max-h-[360px] select-none">
            {/* Background Grid Lines */}
            <circle cx="400" cy="190" r="140" fill="none" stroke="#e2e8f0" strokeDasharray="4 4" strokeWidth="1" />
            <circle cx="400" cy="190" r="90" fill="none" stroke="#e2e8f0" strokeDasharray="2 4" strokeWidth="0.75" />

            {/* Edges Connecting Breached Services */}
            {topologyEdges.map((edge, idx) => {
              const src = SERVICE_COORDINATES[edge.source];
              const tgt = SERVICE_COORDINATES[edge.target];
              if (!src || !tgt) return null;

              const isHighlighted = selectedService === "all" || selectedService === edge.source || selectedService === edge.target;
              const strokeColor = edge.secrets.length >= 3 ? "#e11d48" : edge.secrets.length >= 2 ? "#d97706" : "#2563eb";

              const midX = (src.x + tgt.x) / 2;
              const midY = (src.y + tgt.y) / 2;
              const dx = 400 - midX;
              const dy = 190 - midY;
              const cx = midX + dx * 0.25;
              const cy = midY + dy * 0.25;
              const pathD = `M ${src.x} ${src.y} Q ${cx} ${cy} ${tgt.x} ${tgt.y}`;

              return (
                <g key={idx} className="transition-all duration-300">
                  <path
                    d={pathD}
                    fill="none"
                    stroke={strokeColor}
                    strokeWidth={isHighlighted ? 2.5 : 1}
                    strokeOpacity={isHighlighted ? 0.85 : 0.15}
                    strokeDasharray={isHighlighted ? "none" : "3 3"}
                  />
                  {isHighlighted && (
                    <circle r="3.5" fill={strokeColor}>
                      <animateMotion
                        path={pathD}
                        dur={`${Math.max(2, 6 - edge.secrets.length)}s`}
                        repeatCount="indefinite"
                      />
                    </circle>
                  )}
                </g>
              );
            })}

            {/* Microservice Nodes */}
            {Object.entries(SERVICE_COORDINATES).map(([svcName, coord]) => {
              const isSelected = selectedService === svcName;
              const stats = serviceStats[svcName] || { total: 0, origin: 0, contaminated: 0 };
              const hasSprawl = stats.total > 0;

              return (
                <g 
                  key={svcName} 
                  transform={`translate(${coord.x}, ${coord.y})`}
                  className="cursor-pointer group"
                  onClick={() => setSelectedService(selectedService === svcName ? "all" : svcName)}
                >
                  {/* Outer selection ring */}
                  <circle 
                    r="24" 
                    fill="#ffffff" 
                    stroke={isSelected ? "#2563eb" : coord.color} 
                    strokeWidth={isSelected ? 3 : 2}
                    className="transition-all shadow-sm group-hover:scale-105"
                  />

                  {/* Inner Service Dot */}
                  <circle r="7" fill={coord.color} />

                  {/* Service Label */}
                  <text 
                    y="38" 
                    textAnchor="middle" 
                    className="text-[12px] font-bold fill-slate-900"
                  >
                    {coord.label}
                  </text>
                  <text 
                    y="50" 
                    textAnchor="middle" 
                    className="text-[10px] font-mono fill-slate-400"
                  >
                    {svcName}
                  </text>

                  {/* Contamination Count Badge */}
                  {hasSprawl && (
                    <g transform="translate(14, -18)">
                      <rect 
                        width="24" 
                        height="16" 
                        rx="8" 
                        fill={stats.contaminated > 0 ? "#e11d48" : "#2563eb"} 
                      />
                      <text 
                        x="12" 
                        y="11.5" 
                        textAnchor="middle" 
                        className="text-[9px] font-bold fill-white font-mono"
                      >
                        {stats.total}
                      </text>
                    </g>
                  )}
                </g>
              );
            })}
          </svg>

          {/* Topology Legend */}
          <div className="flex flex-wrap items-center justify-between gap-4 pt-3 border-t border-slate-200 text-xs text-slate-500 font-medium">
            <div className="flex items-center gap-4">
              <span className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-full bg-blue-600" />
                Origin Point
              </span>
              <span className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-full bg-amber-500" />
                Lateral Transmission
              </span>
              <span className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-full bg-rose-600" />
                Critical Contamination (≥ 3 services)
              </span>
            </div>
            <span className="text-[11px] text-slate-400 font-mono">
              Live Topology Mesh • 5 Microservices In-Cluster
            </span>
          </div>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="flex flex-col md:flex-row items-stretch md:items-center justify-between gap-3">
        {/* Search */}
        <div className="relative flex-1">
          <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search by HMAC fingerprint, secret classification, or pod..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-3 py-1.5 bg-white border border-slate-200 rounded-lg text-xs text-slate-800 placeholder-slate-400 focus:outline-none focus:border-blue-500 transition-colors font-mono"
          />
        </div>

        {/* Filter Pills */}
        <div className="flex flex-wrap items-center gap-1.5">
          <button
            onClick={() => setSelectedFilter("all")}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              selectedFilter === "all"
                ? "bg-blue-50 text-blue-700 border border-blue-200 shadow-xs"
                : "bg-white text-slate-600 border border-slate-200 hover:bg-slate-50"
            }`}
          >
            All Lineages ({reports.length})
          </button>

          <button
            onClick={() => setSelectedFilter("sprawled")}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              selectedFilter === "sprawled"
                ? "bg-amber-50 text-amber-700 border border-amber-200 shadow-xs"
                : "bg-white text-slate-600 border border-slate-200 hover:bg-slate-50"
            }`}
          >
            Cross-Pod Sprawls ({multiServiceSprawls})
          </button>

          <button
            onClick={() => setSelectedFilter("isolated")}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              selectedFilter === "isolated"
                ? "bg-emerald-50 text-emerald-700 border border-emerald-200 shadow-xs"
                : "bg-white text-slate-600 border border-slate-200 hover:bg-slate-50"
            }`}
          >
            Isolated ({reports.length - multiServiceSprawls})
          </button>

          <button
            onClick={() => setSelectedFilter("critical")}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              selectedFilter === "critical"
                ? "bg-rose-50 text-rose-700 border border-rose-200 shadow-xs"
                : "bg-white text-slate-600 border border-slate-200 hover:bg-slate-50"
            }`}
          >
            Critical ({criticalCount})
          </button>
        </div>
      </div>

      {/* Lineage Cards Feed */}
      <div className="grid grid-cols-1 gap-4">
        {loading && reports.length === 0 ? (
          <div className="bg-white border border-slate-200 rounded-xl p-12 text-center text-slate-400">
            <RefreshCw className="w-6 h-6 animate-spin mx-auto mb-2 text-blue-600" />
            <span className="text-xs font-medium">Reconstructing cryptographically fingerprinted secret sprawl lineage...</span>
          </div>
        ) : filteredReports.length === 0 ? (
          <div className="bg-white border border-slate-200 rounded-xl p-12 text-center">
            <CheckCircle2 className="w-8 h-8 text-emerald-600 mx-auto mb-2" />
            <h3 className="text-sm font-bold text-slate-800">No Matching Lineages Found</h3>
            <p className="text-slate-500 text-xs mt-0.5">Adjust filters or search parameters to inspect active signatures.</p>
          </div>
        ) : (
          filteredReports.map((report: LineageRecord, idx: number) => {
            const isShadow = !report.is_registered;
            const isCritical = report.severity === "CRITICAL" || report.risk_score >= 12;
            const isSprawled = report.is_sprawled;

            return (
              <div 
                key={idx} 
                className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs space-y-4 hover:border-slate-300 transition-colors"
              >
                {/* Card Header */}
                <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-3">
                  <div>
                    <div className="flex flex-wrap items-center gap-2">
                      <div className="flex items-center gap-1.5 bg-slate-50 px-2.5 py-1 rounded-lg border border-slate-200">
                        <Hash className="w-3.5 h-3.5 text-blue-600" />
                        <code className="font-mono text-slate-800 text-xs font-bold">{report.fingerprint}</code>
                        <button
                          onClick={() => copyToClipboard(report.full_fingerprint, "fp")}
                          title="Copy Full HMAC Fingerprint"
                          className="text-slate-400 hover:text-slate-600 ml-1"
                        >
                          {copiedFp === report.full_fingerprint ? (
                            <Check className="w-3.5 h-3.5 text-emerald-600" />
                          ) : (
                            <Copy className="w-3.5 h-3.5" />
                          )}
                        </button>
                      </div>

                      <span className="px-2 py-0.5 rounded text-[11px] font-semibold bg-blue-50 text-blue-700 border border-blue-200 uppercase">
                        {report.secret_type}
                      </span>

                      <span className={`px-2 py-0.5 rounded text-[11px] font-semibold border ${
                        isShadow
                          ? "bg-rose-50 text-rose-700 border-rose-200"
                          : "bg-emerald-50 text-emerald-700 border-emerald-200"
                      }`}>
                        {isShadow ? "Shadow Secret (Unregistered)" : "Sanctioned K8s Secret"}
                      </span>
                    </div>

                    <p className="text-xs text-slate-500 mt-1.5">
                      HMAC-SHA256 signature generated in-pod. Plaintext remains encrypted in SecureReveal and cannot be derived from this token.
                    </p>
                  </div>

                  <div className="flex items-center gap-2">
                    <span className={`px-2.5 py-1 rounded-lg text-xs font-mono font-bold border ${
                      isCritical
                        ? "bg-rose-50 text-rose-700 border-rose-200"
                        : report.severity === "HIGH"
                        ? "bg-amber-50 text-amber-700 border-amber-200"
                        : "bg-emerald-50 text-emerald-700 border-emerald-200"
                    }`}>
                      {report.severity} RISK • {report.risk_score}
                    </span>

                    <button
                      onClick={() => setActiveDossier(report)}
                      className="px-3 py-1 rounded-lg text-xs font-semibold bg-white hover:bg-slate-50 text-slate-700 border border-slate-200 transition-colors flex items-center gap-1.5 shadow-xs"
                    >
                      <Eye className="w-3.5 h-3.5 text-blue-600" />
                      Forensic Dossier
                    </button>
                  </div>
                </div>

                {/* Metrics Grid */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs">
                  <div className="bg-slate-50 rounded-lg p-3 border border-slate-100">
                    <span className="text-[10px] text-slate-500 uppercase tracking-wider block font-semibold">Cross-Pod Blast Radius</span>
                    <span className="text-sm font-bold text-slate-900 font-mono mt-0.5 block flex items-center gap-1.5">
                      <span className={`w-2 h-2 rounded-full ${isSprawled ? "bg-amber-500" : "bg-emerald-500"}`} />
                      {report.service_count} Microservice{report.service_count !== 1 ? "s" : ""}
                    </span>
                    <span className="text-[10px] text-slate-400 mt-0.5 block">{report.pod_count} Kubernetes Pods</span>
                  </div>

                  <div className="bg-slate-50 rounded-lg p-3 border border-slate-100">
                    <span className="text-[10px] text-slate-500 uppercase tracking-wider block font-semibold">Patient Zero (Origin)</span>
                    <span className="text-xs font-bold text-blue-700 font-mono mt-0.5 block">
                      {report.origin_service}
                    </span>
                    <span className="text-[10px] text-slate-400 mt-0.5 block">First observed source</span>
                  </div>

                  <div className="bg-slate-50 rounded-lg p-3 border border-slate-100">
                    <span className="text-[10px] text-slate-500 uppercase tracking-wider block font-semibold">Leak Interceptions</span>
                    <span className="text-sm font-bold text-slate-900 font-mono mt-0.5 block">
                      {report.occurrences.toLocaleString()} times
                    </span>
                    <span className="text-[10px] text-slate-400 mt-0.5 block">Total logged events</span>
                  </div>

                  <div className="bg-slate-50 rounded-lg p-3 border border-slate-100">
                    <span className="text-[10px] text-slate-500 uppercase tracking-wider block font-semibold">Risk Assessment</span>
                    <span className={`text-xs font-bold font-mono mt-0.5 block ${
                      isCritical ? "text-rose-700" : isSprawled ? "text-amber-700" : "text-emerald-700"
                    }`}>
                      {isCritical ? "High Lateral Exposure" : isSprawled ? "Moderate Lateral Spread" : "Isolated Scope"}
                    </span>
                    <span className="text-[10px] text-slate-400 mt-0.5 block">
                      Multiplier: {isShadow ? "1.5x (Shadow Penalty)" : "1.0x (Sanctioned)"}
                    </span>
                  </div>
                </div>

                {/* Step-by-Step Propagation Stepper */}
                <div className="bg-slate-50 rounded-lg p-3 border border-slate-100">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-[11px] font-bold uppercase tracking-wider text-slate-600 flex items-center gap-1.5">
                      <Zap className="w-3 h-3 text-amber-500" />
                      Chronological Cross-Service Propagation Trail
                    </span>
                    <span className="text-[10px] font-mono text-slate-400">
                      {report.propagation_path.length} Stage{report.propagation_path.length > 1 ? "s" : ""}
                    </span>
                  </div>

                  <div className="flex flex-wrap items-center gap-1.5">
                    {report.propagation_path.map((step, sIdx) => {
                      const isOrigin = step.is_origin;
                      return (
                        <div key={sIdx} className="flex items-center gap-1.5">
                          <div className={`px-2.5 py-1 rounded-md border text-xs font-mono flex items-center gap-1.5 ${
                            isOrigin 
                              ? "bg-blue-50 border-blue-200 text-blue-700 font-semibold"
                              : "bg-white border-slate-200 text-slate-700"
                          }`}>
                            <span className={`w-1.5 h-1.5 rounded-full ${isOrigin ? "bg-blue-600" : "bg-amber-500"}`} />
                            <span className="font-bold">{step.service}</span>
                            <span className="text-[10px] text-slate-400 font-sans">
                              ({step.occurrences} leaks)
                            </span>
                            {isOrigin && (
                              <span className="text-[9px] uppercase px-1 py-0.2 rounded bg-blue-100 text-blue-800 font-bold ml-0.5">
                                Origin
                              </span>
                            )}
                          </div>
                          {sIdx < report.propagation_path.length - 1 && (
                            <ChevronRight className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                          )}
                        </div>
                      );
                    })}
                  </div>
                </div>

                {/* Contaminated Pods List */}
                <div className="space-y-1.5">
                  <span className="text-xs font-semibold text-slate-600 flex items-center gap-1.5">
                    <ServerCrash className="w-3.5 h-3.5 text-slate-400" />
                    Contaminated Kubernetes Pod Instances ({report.pods.length})
                  </span>
                  <div className="flex flex-wrap gap-1.5">
                    {report.pods.map((pod: string, pIdx: number) => (
                      <span 
                        key={pIdx} 
                        className="px-2.5 py-0.5 rounded text-[11px] font-mono bg-slate-50 text-slate-700 border border-slate-200 flex items-center gap-1.5"
                      >
                        <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                        {pod}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Remediation Banner */}
                {isShadow && (
                  <div className="p-3.5 rounded-lg bg-rose-50 border border-rose-200 text-xs text-rose-900 flex flex-col md:flex-row items-start md:items-center justify-between gap-3">
                    <div className="flex items-start gap-2.5">
                      <AlertTriangle className="w-4 h-4 text-rose-600 shrink-0 mt-0.5" />
                      <div>
                        <strong className="block text-rose-950">Remediation Action: Shadow Credential Sprawl Detected</strong>
                        <p className="text-rose-700 text-xs mt-0.5">
                          This secret is hardcoded or unregistered in Kubernetes Secrets. It has spread across {report.service_count} microservices.
                        </p>
                      </div>
                    </div>

                    <button
                      onClick={() => {
                        const cmd = `kubectl delete secret ${report.origin_service}-credential -n logshield-protected && kubectl rollout restart deployment ${report.services.join(" ")} -n logshield-protected`;
                        copyToClipboard(cmd, "cmd");
                      }}
                      className="px-3 py-1.5 rounded-lg text-xs font-mono font-semibold bg-white hover:bg-rose-100 text-rose-800 border border-rose-300 transition-colors flex items-center gap-1.5 shrink-0 shadow-xs"
                    >
                      {copiedCmd?.includes(report.origin_service) ? (
                        <>
                          <Check className="w-3.5 h-3.5 text-emerald-600" />
                          <span>Copied Command!</span>
                        </>
                      ) : (
                        <>
                          <Terminal className="w-3.5 h-3.5" />
                          <span>Copy Rotation Command</span>
                        </>
                      )}
                    </button>
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>

      {/* Forensic Lineage Dossier Modal */}
      {activeDossier && (
        <div className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center p-4 animate-in fade-in duration-200">
          <div className="bg-white border border-slate-200 rounded-2xl max-w-2xl w-full p-6 shadow-xl relative max-h-[90vh] overflow-y-auto space-y-5">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <div className="flex items-center gap-2">
                <Network className="w-5 h-5 text-blue-600" />
                <h3 className="text-base font-bold text-slate-900">Forensic Lineage Dossier</h3>
              </div>
              <button 
                onClick={() => setActiveDossier(null)}
                className="text-slate-400 hover:text-slate-600 p-1 rounded-lg hover:bg-slate-100 transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Dossier Body */}
            <div className="space-y-4 text-xs">
              <div className="bg-slate-50 p-3 rounded-xl border border-slate-200 space-y-1">
                <span className="text-slate-500 uppercase tracking-wider block text-[10px] font-semibold">Full HMAC-SHA256 Fingerprint Signature</span>
                <p className="text-slate-900 break-all select-all font-mono font-bold">{activeDossier.full_fingerprint}</p>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-2.5">
                <div className="bg-slate-50 p-3 rounded-lg border border-slate-200">
                  <span className="text-[10px] text-slate-500 uppercase block font-semibold">Secret Category</span>
                  <span className="text-slate-900 font-bold mt-0.5 block">{activeDossier.secret_type}</span>
                </div>
                <div className="bg-slate-50 p-3 rounded-lg border border-slate-200">
                  <span className="text-[10px] text-slate-500 uppercase block font-semibold">Origin Pod</span>
                  <span className="text-blue-700 font-bold mt-0.5 block truncate" title={activeDossier.origin_pod}>{activeDossier.origin_pod}</span>
                </div>
                <div className="bg-slate-50 p-3 rounded-lg border border-slate-200">
                  <span className="text-[10px] text-slate-500 uppercase block font-semibold">Occurrences</span>
                  <span className="text-slate-900 font-bold mt-0.5 block">{activeDossier.occurrences.toLocaleString()}</span>
                </div>
                <div className="bg-slate-50 p-3 rounded-lg border border-slate-200">
                  <span className="text-[10px] text-slate-500 uppercase block font-semibold">Calculated Risk</span>
                  <span className="text-rose-700 font-bold mt-0.5 block">{activeDossier.risk_score} ({activeDossier.severity})</span>
                </div>
              </div>

              {/* Propagation Steps Table */}
              <div className="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-xs">
                <div className="p-3 bg-slate-50 border-b border-slate-200">
                  <span className="text-[11px] text-slate-700 uppercase tracking-wider block font-bold">
                    Stage-By-Stage Lateral Movement Audit Trail
                  </span>
                </div>
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs">
                    <thead>
                      <tr className="border-b border-slate-200 bg-slate-50/50 text-slate-500 text-[10px] uppercase font-semibold">
                        <th className="py-2.5 px-3">Step</th>
                        <th className="py-2.5 px-3">Microservice</th>
                        <th className="py-2.5 px-3">Pod Instance</th>
                        <th className="py-2.5 px-3">Role</th>
                        <th className="py-2.5 px-3 text-right">Leaks</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100 text-slate-700 font-mono">
                      {activeDossier.propagation_path.map((step, idx) => (
                        <tr key={idx} className="hover:bg-slate-50">
                          <td className="py-2 px-3 text-blue-700 font-bold">#{step.step}</td>
                          <td className="py-2 px-3 text-slate-900 font-sans font-semibold">{step.service}</td>
                          <td className="py-2 px-3 text-slate-500 text-[11px]">{step.pod_name}</td>
                          <td className="py-2 px-3 font-sans">
                            {step.is_origin ? (
                              <span className="text-[9px] px-2 py-0.5 rounded bg-blue-50 text-blue-700 border border-blue-200 font-bold uppercase">Patient Zero</span>
                            ) : (
                              <span className="text-[9px] px-2 py-0.5 rounded bg-amber-50 text-amber-700 border border-amber-200 font-bold uppercase">Lateral Leak</span>
                            )}
                          </td>
                          <td className="py-2 px-3 text-right text-slate-900 font-bold">{step.occurrences}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>

            <div className="flex justify-end gap-2 pt-3 border-t border-slate-100">
              <button
                onClick={() => {
                  const jsonStr = JSON.stringify(activeDossier, null, 2);
                  copyToClipboard(jsonStr, "cmd");
                }}
                className="px-3.5 py-1.5 bg-white hover:bg-slate-50 text-slate-700 rounded-lg text-xs font-semibold transition-colors flex items-center gap-1.5 border border-slate-200 shadow-xs"
              >
                <Copy className="w-3.5 h-3.5" />
                Copy JSON Dossier
              </button>
              <button
                onClick={() => setActiveDossier(null)}
                className="px-4 py-1.5 bg-slate-900 hover:bg-slate-800 text-white rounded-lg text-xs font-semibold transition-colors"
              >
                Close Dossier
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
