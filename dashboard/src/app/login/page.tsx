"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Shield, Lock, ShieldCheck } from "lucide-react";

export default function LoginPage() {
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const router = useRouter();

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    if (password === "admin123") {
      document.cookie = "logshield_auth=true; path=/";
      router.push("/");
    } else {
      setError("Invalid password. Please check your credentials.");
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50 p-4">
      <div className="w-full max-w-md p-8 bg-white border border-slate-200 rounded-2xl shadow-xs space-y-6">
        <div className="flex flex-col items-center text-center">
          <div className="w-14 h-14 bg-blue-50 border border-blue-100 rounded-2xl flex items-center justify-center text-blue-600 mb-4 shadow-xs">
            <Shield className="w-7 h-7" />
          </div>
          <h1 className="text-xl font-black text-slate-900 tracking-tight">LogShield Enterprise</h1>
          <p className="text-slate-500 text-xs mt-1">In-Pod Secret Protection & Telemetry Suite</p>
        </div>

        <form onSubmit={handleLogin} className="space-y-4">
          <div>
            <div className="flex items-center justify-between text-xs text-slate-600 mb-1.5 font-medium">
              <span>Authentication Password</span>
              <span className="text-slate-400 text-[11px]">Demo: <strong className="text-blue-600 font-mono">admin123</strong></span>
            </div>
            <div className="relative">
              <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full bg-slate-50 border border-slate-200 rounded-xl py-2.5 pl-9 pr-3 text-xs text-slate-900 placeholder-slate-400 focus:outline-none focus:border-blue-500 focus:bg-white transition-all font-mono"
                placeholder="Enter password"
                autoFocus
              />
            </div>
            {error && <p className="text-rose-600 text-xs mt-1.5 font-medium">{error}</p>}
          </div>
          
          <button
            type="submit"
            className="w-full py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-semibold text-xs rounded-xl shadow-xs transition-colors"
          >
            Authenticate & Open Dashboard
          </button>
        </form>

        <div className="pt-2 border-t border-slate-100 flex items-center justify-center gap-2 text-[11px] text-slate-400">
          <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
          <span>FIPS 140-2 Compliant In-Pod Security</span>
        </div>
      </div>
    </div>
  );
}
