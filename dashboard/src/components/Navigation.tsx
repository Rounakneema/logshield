"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import { 
  Shield, 
  Home, 
  LayoutGrid, 
  Terminal, 
  KeyRound, 
  FileText, 
  FlaskConical, 
  Activity, 
  Network, 
  Settings,
  Lock,
  Unlock,
  CheckCircle2,
  AlertTriangle
} from "lucide-react";
import { fetchMode } from "@/lib/api";

export function Navigation() {
  const pathname = usePathname();
  const [mode, setModeState] = useState<string>("protected");

  useEffect(() => {
    const checkMode = async () => {
      try {
        const res = await fetchMode();
        if (res?.mode) setModeState(res.mode);
      } catch (e) {}
    };
    checkMode();
    const interval = setInterval(checkMode, 4000);
    return () => clearInterval(interval);
  }, []);

  const links = [
    { href: "/", label: "Overview", icon: Home },
    { href: "/topology", label: "Topology", icon: LayoutGrid },
    { href: "/logs", label: "Live Logs", icon: Terminal },
    { href: "/vault", label: "Secret Detection", icon: KeyRound },
    { href: "/policies", label: "Policies", icon: FileText },
    { href: "/simulator", label: "Playground", icon: FlaskConical },
    { href: "/audit", label: "Audit & Reports", icon: Activity },
    { href: "/sprawl", label: "Sprawl Lineage", icon: Network },
    { href: "/settings", label: "Settings", icon: Settings },
  ];

  const isProtected = mode === "protected";

  return (
    <aside className="fixed top-0 left-0 h-screen w-60 bg-white border-r border-slate-200 flex flex-col justify-between z-40 select-none shadow-xs">
      <div>
        {/* Brand Header */}
        <div className="flex items-center gap-3 p-5 border-b border-slate-100">
          <div className="w-9 h-9 rounded-xl bg-blue-600 flex items-center justify-center text-white shadow-sm shadow-blue-500/20">
            <Shield className="w-5 h-5" />
          </div>
          <div>
            <span className="text-lg font-black text-slate-900 tracking-tight block leading-tight">LogShield</span>
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">IN-POD SECURITY</span>
          </div>
        </div>

        {/* Navigation Menu */}
        <nav className="p-3 space-y-1">
          {links.map((link) => {
            const Icon = link.icon;
            const isActive = pathname === link.href || (link.href !== "/" && pathname.startsWith(link.href));
            return (
              <Link
                key={link.href}
                href={link.href}
                className={`flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-xs font-semibold transition-all ${
                  isActive
                    ? "bg-blue-50 text-blue-600 shadow-xs"
                    : "text-slate-600 hover:text-slate-900 hover:bg-slate-50"
                }`}
              >
                <Icon className={`w-4 h-4 ${isActive ? "text-blue-600" : "text-slate-400"}`} />
                <span>{link.label}</span>
              </Link>
            );
          })}
        </nav>
      </div>

      {/* Footer System Status */}
      <div className="p-4 border-t border-slate-100 space-y-3">
        {/* Protection Active Badge */}
        <div className="flex items-center gap-2.5 bg-slate-50 p-2.5 rounded-xl border border-slate-100">
          <span className="flex h-2.5 w-2.5 relative">
            <span className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${
              isProtected ? "bg-emerald-400" : "bg-red-400"
            }`} />
            <span className={`relative inline-flex rounded-full h-2.5 w-2.5 ${
              isProtected ? "bg-emerald-500" : "bg-red-500"
            }`} />
          </span>
          <div>
            <span className="text-xs font-bold text-slate-900 block leading-tight">
              {isProtected ? "Protection Active" : "Shield Bypassed"}
            </span>
            <span className="text-[10px] text-slate-500 block">
              {isProtected ? "Intercepting & Sanitizing" : "Raw Logs Streaming"}
            </span>
          </div>
        </div>

        {/* Engine Version */}
        <div className="px-1 text-[11px] text-slate-400 flex items-center justify-between">
          <span className="font-semibold text-slate-600">LogMask v4.0</span>
          <span>1,361 Patterns</span>
        </div>
      </div>
    </aside>
  );
}
