"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Shield, LayoutDashboard, KeyRound, Activity, Network } from "lucide-react";

export function Navigation() {
  const pathname = usePathname();

  const links = [
    { href: "/", label: "Overview", icon: LayoutDashboard },
    { href: "/logs", label: "Live Logs", icon: Activity },
    { href: "/vault", label: "SecureReveal Vault", icon: KeyRound },
    { href: "/audit", label: "Audit Logs", icon: Activity },
    { href: "/sprawl", label: "Sprawl Lineage", icon: Network },
  ];

  return (
    <nav className="fixed top-0 left-0 h-screen w-64 bg-slate-900 border-r border-slate-800 p-4">
      <div className="flex items-center gap-3 mb-8 px-2 py-4">
        <Shield className="w-8 h-8 text-emerald-500" />
        <span className="text-xl font-bold text-white tracking-tight">LogShield</span>
      </div>
      
      <div className="space-y-2">
        {links.map((link) => {
          const Icon = link.icon;
          const isActive = pathname === link.href;
          return (
            <Link
              key={link.href}
              href={link.href}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-lg transition-colors ${
                isActive 
                  ? "bg-emerald-500/10 text-emerald-400 font-medium" 
                  : "text-slate-400 hover:text-slate-200 hover:bg-slate-800"
              }`}
            >
              <Icon className="w-5 h-5" />
              {link.label}
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
