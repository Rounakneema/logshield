"use client";

import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import { 
  Search, 
  ChevronDown, 
  ShieldCheck, 
  ShieldAlert, 
  Lock, 
  Unlock, 
  RefreshCw 
} from "lucide-react";
import { Navigation } from "./Navigation";
import { fetchMode, setMode } from "@/lib/api";

export function LayoutWrapper({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const isLoginPage = pathname === "/login";

  const [mode, setModeState] = useState<string>("protected");
  const [toggling, setToggling] = useState<boolean>(false);
  const [cluster, setCluster] = useState<string>("minikube-cluster");
  const [namespace, setNamespace] = useState<string>("logshield-protected");
  const [searchVal, setSearchVal] = useState<string>("");

  useEffect(() => {
    const checkMode = async () => {
      try {
        const res = await fetchMode();
        if (res?.mode) setModeState(res.mode);
      } catch (e) {}
    };
    checkMode();
    const interval = setInterval(checkMode, 3000);
    return () => clearInterval(interval);
  }, []);

  const handleToggle = async () => {
    setToggling(true);
    const nextMode = mode === "protected" ? "bypass" : "protected";
    try {
      await setMode(nextMode);
      setModeState(nextMode);
    } catch (e) {
      console.error(e);
    } finally {
      setToggling(false);
    }
  };

  if (isLoginPage) {
    return <main className="w-full min-h-screen bg-slate-50">{children}</main>;
  }

  const isProtected = mode === "protected";

  return (
    <div className="flex w-full min-h-screen bg-slate-50">
      <Navigation />

      {/* Main Container */}
      <div className="flex-1 ml-60 flex flex-col min-w-0">
        {/* Top Enterprise Navigation Bar */}
        <header className="sticky top-0 z-30 bg-white border-b border-slate-200 px-8 py-3 flex items-center justify-between gap-6 shadow-xs">
          {/* Search Box */}
          <div className="relative flex-1 max-w-md">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search services, logs, patterns..."
              value={searchVal}
              onChange={(e) => setSearchVal(e.target.value)}
              className="w-full bg-slate-50 border border-slate-200 rounded-lg pl-9 pr-8 py-1.5 text-xs text-slate-800 placeholder-slate-400 focus:outline-none focus:border-blue-500 focus:bg-white transition-all"
            />
            <span className="absolute right-2.5 top-1/2 -translate-y-1/2 px-1.5 py-0.5 rounded bg-slate-200 text-[10px] font-mono text-slate-500 font-bold">
              /
            </span>
          </div>

          {/* Right Action Cluster & State Controls */}
          <div className="flex items-center gap-4">
            {/* Cluster Selector */}
            <div className="flex items-center gap-1.5 text-xs">
              <span className="text-slate-400 font-medium">Cluster</span>
              <div className="flex items-center gap-1 font-semibold text-slate-700 bg-slate-50 px-2.5 py-1 rounded-md border border-slate-200">
                <span>{cluster}</span>
                <ChevronDown className="w-3.5 h-3.5 text-slate-400" />
              </div>
            </div>

            {/* Namespace Selector */}
            <div className="flex items-center gap-1.5 text-xs">
              <span className="text-slate-400 font-medium">Namespace</span>
              <div className="flex items-center gap-1 font-semibold text-slate-700 bg-slate-50 px-2.5 py-1 rounded-md border border-slate-200">
                <span>{namespace}</span>
                <ChevronDown className="w-3.5 h-3.5 text-slate-400" />
              </div>
            </div>

            {/* Live Shield Status Badge */}
            <div className="flex items-center gap-2 border-l border-slate-200 pl-4 text-xs">
              <span className="flex h-2.5 w-2.5 relative">
                <span className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${
                  isProtected ? "bg-emerald-400" : "bg-red-400"
                }`} />
                <span className={`relative inline-flex rounded-full h-2.5 w-2.5 ${
                  isProtected ? "bg-emerald-500" : "bg-red-500"
                }`} />
              </span>
              <div>
                <span className="font-bold text-slate-900 block leading-tight">
                  {isProtected ? "Shield Active" : "Shield Bypassed"}
                </span>
                <span className="text-[10px] text-slate-400 block">
                  {isProtected ? "All pods protected" : "Zero redaction active"}
                </span>
              </div>
            </div>

            {/* Mode Toggle Button */}
            <button
              onClick={handleToggle}
              disabled={toggling}
              className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-all shadow-xs active:scale-95 ${
                isProtected
                  ? "bg-white text-red-600 border border-red-300 hover:bg-red-50"
                  : "bg-emerald-600 text-white hover:bg-emerald-700 font-bold"
              }`}
            >
              {isProtected ? (
                <>
                  <Unlock className="w-3.5 h-3.5" />
                  <span>Disable Shield (Bypass)</span>
                </>
              ) : (
                <>
                  <ShieldCheck className="w-3.5 h-3.5" />
                  <span>Enable Shield (Protect)</span>
                </>
              )}
            </button>
          </div>
        </header>

        {/* Page Content Viewport */}
        <main className="p-8 max-w-[1400px] w-full mx-auto">
          {children}
        </main>
      </div>
    </div>
  );
}
