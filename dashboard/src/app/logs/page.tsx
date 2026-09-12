"use client";

import { useEffect, useState, useRef } from "react";
import { fetchLogs } from "@/lib/api";
import { Terminal } from "lucide-react";

export default function LiveLogs() {
  const [logs, setLogs] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const loadLogs = async () => {
      try {
        const data = await fetchLogs();
        setLogs(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    loadLogs();
    const interval = setInterval(loadLogs, 1000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    // Auto-scroll to bottom
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [logs]);

  return (
    <div className="space-y-6 animate-in fade-in duration-500 h-[calc(100vh-80px)] flex flex-col">
      <div>
        <h1 className="text-3xl font-bold text-white mb-2 flex items-center gap-3">
          <Terminal className="w-8 h-8 text-emerald-500" />
          Live Logs Stream
        </h1>
        <p className="text-slate-400">Real-time view of sanitized application logs across all microservices.</p>
      </div>

      <div className="flex-1 bg-[#0c0c0c] border border-slate-800 rounded-xl overflow-y-auto p-4 font-mono text-sm shadow-inner relative">
        {loading ? (
          <div className="text-slate-500 animate-pulse">Connecting to stream...</div>
        ) : logs.length === 0 ? (
          <div className="text-slate-600 italic">No recent logs found. Generate some traffic to see logs here.</div>
        ) : (
          <div className="space-y-1">
            {logs.map((log, i) => {
              // Simple syntax highlighting for LogShield tags
              const isRedacted = log.includes("[REDACTED");
              const isFlagged = log.includes("[FLAGGED");
              
              return (
                <div key={i} className={`whitespace-pre-wrap break-all ${isRedacted ? 'text-emerald-400 font-bold' : isFlagged ? 'text-amber-400 font-bold' : 'text-slate-300'}`}>
                  {log}
                </div>
              );
            })}
            <div ref={bottomRef} />
          </div>
        )}
      </div>
    </div>
  );
}
