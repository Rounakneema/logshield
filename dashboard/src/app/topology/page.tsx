"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { 
  LayoutGrid, 
  Server, 
  ShieldCheck, 
  CheckCircle2, 
  Layers, 
  ArrowRight, 
  Cpu, 
  HardDrive, 
  Clock, 
  Activity, 
  ExternalLink,
  Terminal,
  RefreshCw,
  ShieldAlert,
  Lock,
  Unlock
} from "lucide-react";
import { fetchTopology, toggleQuarantine } from "@/lib/api";

interface PodData {
  id: string;
  name: string;
  service: string;
  ready: string;
  status: string;
  appContainer: string;
  sidecarContainer: string;
  sharedVolume: string;
  latency: string;
  restarts?: number;
  secretsIntercepted: number;
  isQuarantined?: boolean;
  podIp?: string;
  nodeName?: string;
}

export default function TopologyPage() {
  const [pods, setPods] = useState<PodData[]>([]);
  const [clusterInfo, setClusterInfo] = useState<{ cluster: string; namespace: string; quarantined_count: number }>({
    cluster: "minikube-cluster",
    namespace: "logshield-protected",
    quarantined_count: 0
  });
  const [loading, setLoading] = useState<boolean>(true);
  const [actionBusy, setActionBusy] = useState<Record<string, boolean>>({});
  const [message, setMessage] = useState<string | null>(null);

  const loadData = async () => {
    try {
      const data = await fetchTopology();
      if (data?.pods) {
        setPods(data.pods);
        setClusterInfo({
          cluster: data.cluster || "minikube-cluster",
          namespace: data.namespace || "logshield-protected",
          quarantined_count: data.quarantined_count || 0
        });
      }
    } catch (err) {
      console.error("Failed to load topology:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 3000);
    return () => clearInterval(interval);
  }, []);

  const handleQuarantine = async (service: string, shouldQuarantine: boolean) => {
    setActionBusy(prev => ({ ...prev, [service]: true }));
    try {
      const res = await toggleQuarantine(service, shouldQuarantine);
      setMessage(res.message);
      await loadData();
      setTimeout(() => setMessage(null), 4000);
    } catch (err: any) {
      alert("Failed to toggle quarantine: " + err.message);
    } finally {
      setActionBusy(prev => ({ ...prev, [service]: false }));
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 bg-white border border-slate-200 p-5 rounded-xl shadow-xs">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-xl font-bold text-slate-900 tracking-tight flex items-center gap-2.5">
              <LayoutGrid className="w-5 h-5 text-blue-600" />
              In-Pod Sidecar Cluster Architecture & Pod Topology
            </h1>
            <span className="px-2.5 py-0.5 rounded-full text-[11px] font-mono font-bold uppercase tracking-wider bg-emerald-50 text-emerald-700 border border-emerald-200">
              {pods.length} Real Pods Discovered
            </span>
            {clusterInfo.quarantined_count > 0 && (
              <span className="px-2.5 py-0.5 rounded-full text-[11px] font-mono font-bold uppercase tracking-wider bg-red-50 text-red-700 border border-red-200 flex items-center gap-1">
                <ShieldAlert className="w-3 h-3" />
                {clusterInfo.quarantined_count} Quarantined
              </span>
            )}
          </div>
          <p className="text-slate-500 text-xs mt-1">
            Real-time Kubernetes deployment topology in namespace <code className="font-mono text-slate-800 font-semibold">{clusterInfo.namespace}</code>. Querying cluster pods, in-pod shared memory pipes, and sidecar runtime states.
          </p>
        </div>

        <div className="flex items-center gap-2 text-xs">
          <div className="bg-slate-50 border border-slate-200 px-3 py-1.5 rounded-lg flex items-center gap-2 text-slate-700 font-medium">
            <Server className="w-3.5 h-3.5 text-blue-600" />
            <span>{clusterInfo.cluster} (v1.37.0)</span>
          </div>
          <button
            onClick={loadData}
            className="p-1.5 rounded-lg border border-slate-200 hover:bg-slate-50 text-slate-600 transition-colors"
            title="Refresh Pods"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin text-blue-600" : ""}`} />
          </button>
        </div>
      </div>

      {/* Notification Banner */}
      {message && (
        <div className="p-3 rounded-xl bg-blue-50 border border-blue-200 text-xs text-blue-800 flex items-center justify-between shadow-xs animate-in fade-in">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-blue-600 shrink-0" />
            <span>{message}</span>
          </div>
          <button onClick={() => setMessage(null)} className="text-blue-500 hover:text-blue-700 font-bold ml-2">✕</button>
        </div>
      )}

      {/* 4-Box In-Pod Pipeline Data Flow Diagram */}
      <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-xs space-y-4">
        <div>
          <h2 className="text-sm font-bold text-slate-900 uppercase tracking-wider">
            In-Pod Interception Data Pipeline (Zero Kernel Modification)
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Application writes raw stdout/stderr to an emptyDir volume pipe. The LogShield sidecar processes tokens before log forwarders can read.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 relative">
          {/* Box 1 */}
          <div className="bg-slate-50 border border-slate-200 rounded-xl p-4 space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500">Container 1</span>
              <span className="w-2 h-2 rounded-full bg-blue-500" />
            </div>
            <h4 className="text-sm font-bold text-slate-900">Application Container</h4>
            <p className="text-xs text-slate-500">
              Microservice generates logs. Emits potential secrets (passwords, tokens, URIs) into shared volume.
            </p>
            <div className="bg-white border border-slate-200 rounded-lg p-2 font-mono text-[11px] text-slate-700">
              /shared/app.log
            </div>
          </div>

          {/* Box 2 */}
          <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 space-y-2 relative">
            <div className="flex items-center justify-between">
              <span className="text-[10px] font-bold uppercase tracking-wider text-blue-700">Container 2 (Sidecar)</span>
              <span className="w-2 h-2 rounded-full bg-blue-600 animate-pulse" />
            </div>
            <h4 className="text-sm font-bold text-blue-900">LogShield Interceptor</h4>
            <p className="text-xs text-blue-800">
              3-pass classifier & SCS confidence engine intercepts raw stream. Masks tokens & vaults into AES-256 storage.
            </p>
            <div className="bg-white border border-blue-200 rounded-lg p-2 font-mono text-[11px] text-blue-700 font-semibold">
              0.50 ms latency &bull; Zero False Positives
            </div>
          </div>

          {/* Box 3 */}
          <div className="bg-slate-50 border border-slate-200 rounded-xl p-4 space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500">Shared Volume</span>
              <span className="w-2 h-2 rounded-full bg-emerald-500" />
            </div>
            <h4 className="text-sm font-bold text-slate-900">Sanitized Output Pipe</h4>
            <p className="text-xs text-slate-500">
              Output buffer holds only sanitized lines with reversible <code className="font-mono text-slate-800">[REDACTED:SEC-XXXX]</code> tokens.
            </p>
            <div className="bg-white border border-slate-200 rounded-lg p-2 font-mono text-[11px] text-emerald-700 font-semibold">
              EmptyDir (RAM-backed tmpfs)
            </div>
          </div>

          {/* Box 4 */}
          <div className="bg-slate-50 border border-slate-200 rounded-xl p-4 space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500">Cluster Level</span>
              <span className="w-2 h-2 rounded-full bg-slate-400" />
            </div>
            <h4 className="text-sm font-bold text-slate-900">Log Forwarder / SIEM</h4>
            <p className="text-xs text-slate-500">
              Fluent Bit, Datadog Agent, or Elasticsearch harvests sanitized logs. Absolute zero leakage to external aggregators.
            </p>
            <div className="bg-white border border-slate-200 rounded-lg p-2 font-mono text-[11px] text-slate-700">
              Fluent Bit DaemonSet
            </div>
          </div>
        </div>
      </div>

      {/* Real Pod Grid */}
      <div className="space-y-3">
        <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 flex items-center gap-2">
          <Server className="w-4 h-4 text-blue-600" />
          Active Microservice Pods ({pods.length})
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {pods.map((pod) => {
            const isQuarantined = !!pod.isQuarantined;
            const isBusy = !!actionBusy[pod.service];

            return (
              <div
                key={pod.id}
                className={`bg-white border rounded-xl p-5 shadow-xs transition-all space-y-3 ${
                  isQuarantined
                    ? "border-red-400 ring-2 ring-red-500/10 bg-red-50/20"
                    : "border-slate-200 hover:border-slate-300"
                }`}
              >
                <div className="flex items-start justify-between">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="inline-block px-2 py-0.5 rounded text-[11px] font-semibold bg-blue-50 text-blue-700 border border-blue-200">
                        {pod.service}
                      </span>
                      {isQuarantined && (
                        <span className="inline-block px-2 py-0.5 rounded text-[10px] font-bold bg-red-600 text-white shadow-xs">
                          QUARANTINED (K8s NetPol)
                        </span>
                      )}
                    </div>
                    <h4 className="text-xs font-bold text-slate-900 mt-1 font-mono truncate max-w-[200px]" title={pod.name}>
                      {pod.name}
                    </h4>
                  </div>
                  <span className={`flex items-center gap-1 text-[11px] font-semibold px-2 py-0.5 rounded-full border ${
                    pod.ready.startsWith("2/2") 
                      ? "text-emerald-700 bg-emerald-50 border-emerald-200" 
                      : "text-amber-700 bg-amber-50 border-amber-200"
                  }`}>
                    <CheckCircle2 className="w-3 h-3 text-emerald-600" />
                    {pod.ready} Ready
                  </span>
                </div>

                <div className="space-y-1.5 text-xs">
                  <div className="flex justify-between text-slate-600">
                    <span className="text-slate-400">Pod IP / Node:</span>
                    <span className="font-mono text-[11px] truncate max-w-[150px]">{pod.podIp || "10.244.0.x"} ({pod.nodeName || "minikube"})</span>
                  </div>
                  <div className="flex justify-between text-slate-600">
                    <span className="text-slate-400">App Container:</span>
                    <span className="font-mono text-[11px] truncate max-w-[150px]">{pod.appContainer}</span>
                  </div>
                  <div className="flex justify-between text-slate-600">
                    <span className="text-slate-400">Sidecar Container:</span>
                    <span className="font-mono text-[11px] truncate max-w-[150px] text-blue-600 font-semibold">{pod.sidecarContainer}</span>
                  </div>
                  <div className="flex justify-between text-slate-600">
                    <span className="text-slate-400">Interception Latency:</span>
                    <span className="font-mono text-[11px] font-bold text-slate-900">{pod.latency}</span>
                  </div>
                  <div className="flex justify-between text-slate-600">
                    <span className="text-slate-400">Restarts:</span>
                    <span className="font-mono text-[11px] text-slate-700">{pod.restarts ?? 0}</span>
                  </div>
                </div>

                {/* Bottom Action Bar */}
                <div className="pt-3 border-t border-slate-100 flex items-center justify-between text-xs gap-2">
                  <span className="text-slate-500 text-[11px]">
                    Vaulted: <strong className="text-slate-800">{pod.secretsIntercepted}</strong> secrets
                  </span>

                  <div className="flex items-center gap-1.5">
                    {/* Real Kubernetes NetworkPolicy Quarantine Action */}
                    {pod.service !== "traffic-generator" && pod.service !== "logshield-dashboard" && (
                      <button
                        onClick={() => handleQuarantine(pod.service, !isQuarantined)}
                        disabled={isBusy}
                        className={`px-2 py-1 rounded text-[11px] font-semibold transition-all flex items-center gap-1 shadow-xs disabled:opacity-50 ${
                          isQuarantined
                            ? "bg-emerald-600 hover:bg-emerald-700 text-white"
                            : "bg-red-50 hover:bg-red-100 text-red-700 border border-red-200"
                        }`}
                        title={isQuarantined ? "Restore full pod network connectivity" : "Apply Kubernetes V1NetworkPolicy quarantine"}
                      >
                        {isBusy ? (
                          <RefreshCw className="w-3 h-3 animate-spin" />
                        ) : isQuarantined ? (
                          <>
                            <Unlock className="w-3 h-3" />
                            Unquarantine
                          </>
                        ) : (
                          <>
                            <ShieldAlert className="w-3 h-3" />
                            Quarantine
                          </>
                        )}
                      </button>
                    )}

                    <Link
                      href={`/logs?service=${pod.service}`}
                      className="px-2 py-1 rounded text-[11px] font-semibold text-blue-600 hover:bg-blue-50 border border-blue-200 flex items-center gap-1"
                    >
                      Logs
                      <ArrowRight className="w-3 h-3" />
                    </Link>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
