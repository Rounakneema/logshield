"use client";

import { useState } from "react";
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
  RefreshCw
} from "lucide-react";

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
  memory: string;
  cpu: string;
  secretsIntercepted: number;
}

const PODS: PodData[] = [
  {
    id: "auth-1",
    name: "auth-service-79f8c465d8-z9q2w",
    service: "auth-service",
    ready: "2/2",
    status: "Running",
    appContainer: "auth-service:8000 (Python FastAPI)",
    sidecarContainer: "logshield-sidecar:8080 (v4.2.0)",
    sharedVolume: "emptyDir:/shared/app.log",
    latency: "3.8 µs",
    memory: "18.4 MB",
    cpu: "0.02 cores",
    secretsIntercepted: 142
  },
  {
    id: "payment-1",
    name: "payment-service-67b8cfd54-k8m9p",
    service: "payment-service",
    ready: "2/2",
    status: "Running",
    appContainer: "payment-service:8000 (Stripe Gateway)",
    sidecarContainer: "logshield-sidecar:8080 (v4.2.0)",
    sharedVolume: "emptyDir:/shared/app.log",
    latency: "4.1 µs",
    memory: "19.1 MB",
    cpu: "0.03 cores",
    secretsIntercepted: 89
  },
  {
    id: "inventory-1",
    name: "inventory-service-58dc9748b-w4x2z",
    service: "inventory-service",
    ready: "2/2",
    status: "Running",
    appContainer: "inventory-service:8000 (Catalog API)",
    sidecarContainer: "logshield-sidecar:8080 (v4.2.0)",
    sharedVolume: "emptyDir:/shared/app.log",
    latency: "3.6 µs",
    memory: "17.8 MB",
    cpu: "0.01 cores",
    secretsIntercepted: 64
  },
  {
    id: "user-1",
    name: "user-service-45fa8291c-m7j3n",
    service: "user-service",
    ready: "2/2",
    status: "Running",
    appContainer: "user-service:8000 (Profile API)",
    sidecarContainer: "logshield-sidecar:8080 (v4.2.0)",
    sharedVolume: "emptyDir:/shared/app.log",
    latency: "3.9 µs",
    memory: "18.2 MB",
    cpu: "0.02 cores",
    secretsIntercepted: 51
  },
  {
    id: "notification-1",
    name: "notification-service-98bb4120f-h2k6t",
    service: "notification-service",
    ready: "2/2",
    status: "Running",
    appContainer: "notification-service:8000 (Twilio/SES)",
    sidecarContainer: "logshield-sidecar:8080 (v4.2.0)",
    sharedVolume: "emptyDir:/shared/app.log",
    latency: "3.7 µs",
    memory: "17.5 MB",
    cpu: "0.01 cores",
    secretsIntercepted: 38
  }
];

export default function TopologyPage() {
  const [selectedPod, setSelectedPod] = useState<PodData>(PODS[0]);

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
              5/5 Pods Protected
            </span>
          </div>
          <p className="text-slate-500 text-xs mt-1">
            Live Kubernetes deployment topology in namespace <code className="font-mono text-slate-800 font-semibold">logshield-protected</code>. Inspect container pairs, shared emptyDir interception pipes, and sidecar resource metrics.
          </p>
        </div>

        <div className="flex items-center gap-2 text-xs">
          <div className="bg-slate-50 border border-slate-200 px-3 py-1.5 rounded-lg flex items-center gap-2 text-slate-700 font-medium">
            <Server className="w-3.5 h-3.5 text-blue-600" />
            <span>minikube-cluster (v1.30.0)</span>
          </div>
        </div>
      </div>

      {/* 4-Box In-Pod Pipeline Data Flow Diagram */}
      <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-xs space-y-4">
        <div>
          <h2 className="text-sm font-bold text-slate-900 uppercase tracking-wider">
            In-Pod Interception Data Pipeline (Zero Kernel Modification)
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Application writes raw stdout/stderr to an emptyDir volume pipe. The LogShield sidecar processes tokens in &lt; 5 µs before log forwarders can read.
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
              Microservice generates business logs. Emits potential secrets (passwords, tokens, URIs) into shared volume.
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
              Aho-Corasick automaton + Shannon entropy scanner intercepts raw stream. Masks tokens & vaults into AES-256 storage.
            </p>
            <div className="bg-white border border-blue-200 rounded-lg p-2 font-mono text-[11px] text-blue-700 font-semibold">
              3.8 µs latency &bull; Zero regex
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

      {/* Pod Grid */}
      <div className="space-y-3">
        <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 flex items-center gap-2">
          <Server className="w-4 h-4 text-blue-600" />
          Active Microservice Pods ({PODS.length})
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {PODS.map((pod) => {
            const isSelected = selectedPod.id === pod.id;
            return (
              <div
                key={pod.id}
                onClick={() => setSelectedPod(pod)}
                className={`bg-white border rounded-xl p-5 shadow-xs transition-all cursor-pointer space-y-3 ${
                  isSelected 
                    ? "border-blue-500 ring-2 ring-blue-500/10" 
                    : "border-slate-200 hover:border-slate-300"
                }`}
              >
                <div className="flex items-start justify-between">
                  <div>
                    <span className="inline-block px-2 py-0.5 rounded text-[11px] font-semibold bg-blue-50 text-blue-700 border border-blue-200">
                      {pod.service}
                    </span>
                    <h4 className="text-xs font-bold text-slate-900 mt-1 font-mono truncate max-w-[200px]" title={pod.name}>
                      {pod.name}
                    </h4>
                  </div>
                  <span className="flex items-center gap-1 text-[11px] font-semibold text-emerald-700 bg-emerald-50 border border-emerald-200 px-2 py-0.5 rounded-full">
                    <CheckCircle2 className="w-3 h-3 text-emerald-600" />
                    {pod.ready} Ready
                  </span>
                </div>

                <div className="space-y-1.5 text-xs">
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
                    <span className="text-slate-400">Memory / CPU:</span>
                    <span className="font-mono text-[11px]">{pod.memory} / {pod.cpu}</span>
                  </div>
                </div>

                <div className="pt-2 border-t border-slate-100 flex items-center justify-between text-xs">
                  <span className="text-slate-500">
                    Intercepted: <strong className="text-slate-800">{pod.secretsIntercepted}</strong> secrets
                  </span>
                  <Link
                    href={`/logs?service=${pod.service}`}
                    className="text-blue-600 hover:text-blue-700 font-semibold flex items-center gap-1 text-[11px]"
                  >
                    View Logs
                    <ArrowRight className="w-3 h-3" />
                  </Link>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
