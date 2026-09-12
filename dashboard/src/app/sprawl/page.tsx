"use client";

import { useEffect, useState } from "react";
import { fetchSprawl } from "@/lib/api";
import { Network, ServerCrash, Share2 } from "lucide-react";

export default function SprawlPage() {
  const [reports, setReports] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadData = async () => {
      try {
        const data = await fetchSprawl();
        setReports(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, []);

  if (loading) return <div className="text-slate-400">Loading sprawl analytics...</div>;

  return (
    <div className="space-y-6 animate-in fade-in duration-500">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">Sprawl Lineage</h1>
          <p className="text-slate-400">Track cross-pod contamination of leaked secrets via HMAC fingerprinting.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6">
        {reports.length === 0 ? (
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-12 text-center">
            <Network className="w-12 h-12 text-slate-700 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-slate-300">No Sprawl Detected</h3>
            <p className="text-slate-500">No secrets have been seen across multiple pods.</p>
          </div>
        ) : (
          reports.map((report: any) => (
            <div key={report.hmac_hash} className="bg-slate-900 border border-slate-800 rounded-xl p-6 relative overflow-hidden">
              <div className="absolute top-0 left-0 w-1 h-full bg-amber-500" />
              
              <div className="flex justify-between items-start mb-6">
                <div>
                  <h3 className="text-lg font-bold text-white flex items-center gap-2">
                    <Share2 className="w-5 h-5 text-amber-500" />
                    Cross-Pod Leakage Detected
                  </h3>
                  <p className="text-slate-400 text-sm mt-1">
                    Fingerprint: <code className="text-slate-500 bg-slate-950 px-1 rounded">{report.hmac_hash.substring(0, 16)}...</code>
                  </p>
                </div>
                <div className="bg-amber-500/10 text-amber-500 px-3 py-1 rounded-lg text-sm font-bold border border-amber-500/20">
                  {report.occurrences} Occurrences
                </div>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                <div className="bg-slate-950 rounded-lg p-3 border border-slate-800">
                  <p className="text-xs text-slate-500 mb-1">First Seen</p>
                  <p className="text-sm text-slate-300">{new Date(report.first_seen).toLocaleString()}</p>
                </div>
                <div className="bg-slate-950 rounded-lg p-3 border border-slate-800">
                  <p className="text-xs text-slate-500 mb-1">Last Seen</p>
                  <p className="text-sm text-slate-300">{new Date(report.last_seen).toLocaleString()}</p>
                </div>
                <div className="bg-slate-950 rounded-lg p-3 border border-slate-800 col-span-2">
                  <p className="text-xs text-slate-500 mb-1">Impacted Namespaces</p>
                  <div className="flex gap-2 mt-1">
                    {report.namespaces.map((ns: string) => (
                      <span key={ns} className="px-2 py-0.5 rounded text-xs font-medium bg-blue-500/10 text-blue-400 border border-blue-500/20">
                        {ns}
                      </span>
                    ))}
                  </div>
                </div>
              </div>

              <div>
                <p className="text-sm font-medium text-slate-400 mb-3 flex items-center gap-2">
                  <ServerCrash className="w-4 h-4" /> 
                  Affected Pod UIDs
                </p>
                <div className="flex flex-wrap gap-2">
                  {report.pod_uids.map((uid: string) => (
                    <span key={uid} className="px-3 py-1.5 rounded-lg text-xs font-mono bg-slate-800 text-slate-300 border border-slate-700">
                      {uid}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
