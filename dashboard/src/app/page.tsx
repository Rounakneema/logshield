"use client";

import { useEffect, useState } from "react";
import { fetchStats } from "@/lib/api";
import { Shield, ShieldAlert, Activity, ArrowUpRight } from "lucide-react";
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

export default function Overview() {
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadStats = async () => {
      try {
        const data = await fetchStats();
        setStats(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    loadStats();
    const interval = setInterval(loadStats, 2000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return <div className="text-slate-400">Loading overview...</div>;
  }

  const timeseriesData = stats?.timeseries || [
    { time: "10:00", lines: 0, secrets: 0 }
  ];

  return (
    <div className="space-y-6 animate-in fade-in duration-500">
      <div>
        <h1 className="text-3xl font-bold text-white mb-2">System Overview</h1>
        <p className="text-slate-400">Real-time secret detection telemetry across your clusters.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
          <div className="flex justify-between items-start mb-4">
            <div>
              <p className="text-slate-400 font-medium text-sm mb-1">Total Lines Scanned</p>
              <h3 className="text-3xl font-bold text-white">{stats?.lines_processed?.toLocaleString() || 0}</h3>
            </div>
            <div className="p-3 bg-emerald-500/10 rounded-lg">
              <Activity className="w-6 h-6 text-emerald-500" />
            </div>
          </div>
          <div className="flex items-center text-sm text-emerald-500 font-medium">
            <ArrowUpRight className="w-4 h-4 mr-1" />
            <span>Active monitoring</span>
          </div>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 relative overflow-hidden group">
          <div className="absolute inset-0 bg-gradient-to-r from-red-500/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
          <div className="flex justify-between items-start mb-4 relative z-10">
            <div>
              <p className="text-slate-400 font-medium text-sm mb-1">Secrets Masked</p>
              <h3 className="text-3xl font-bold text-white">{stats?.secrets_masked?.toLocaleString() || 0}</h3>
            </div>
            <div className="p-3 bg-red-500/10 rounded-lg">
              <ShieldAlert className="w-6 h-6 text-red-500" />
            </div>
          </div>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
          <div className="flex justify-between items-start mb-4">
            <div>
              <p className="text-slate-400 font-medium text-sm mb-1">Lines Flagged (Low Confidence)</p>
              <h3 className="text-3xl font-bold text-white">{stats?.lines_flagged?.toLocaleString() || 0}</h3>
            </div>
            <div className="p-3 bg-amber-500/10 rounded-lg">
              <Shield className="w-6 h-6 text-amber-500" />
            </div>
          </div>
        </div>
      </div>

      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
        <h3 className="text-lg font-bold text-white mb-6">Scanning Volume & Detections</h3>
        <div className="h-[300px] w-full">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={timeseriesData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
              <defs>
                <linearGradient id="colorLines" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#10b981" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                </linearGradient>
                <linearGradient id="colorSecrets" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#ef4444" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#ef4444" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <XAxis dataKey="time" stroke="#475569" tick={{fill: '#94a3b8'}} />
              <YAxis stroke="#475569" tick={{fill: '#94a3b8'}} />
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
              <Tooltip 
                contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', color: '#f8fafc' }}
                itemStyle={{ color: '#f8fafc' }}
              />
              <Area type="monotone" dataKey="lines" stroke="#10b981" fillOpacity={1} fill="url(#colorLines)" name="Lines Scanned" />
              <Area type="monotone" dataKey="secrets" stroke="#ef4444" fillOpacity={1} fill="url(#colorSecrets)" name="Secrets Found" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
