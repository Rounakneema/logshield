"use client";

import { useEffect, useState } from "react";
import { fetchVault, retrieveVault } from "@/lib/api";
import { KeyRound, Shield, AlertTriangle, ShieldCheck, Lock, Eye, EyeOff } from "lucide-react";

export default function VaultPage() {
  const [vaultEntries, setVaultEntries] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [isUnlocked, setIsUnlocked] = useState(false);
  const [pin, setPin] = useState("");
  const [pinError, setPinError] = useState("");
  const [revealedSecrets, setRevealedSecrets] = useState<Record<string, string>>({});
  const [revealing, setRevealing] = useState<Record<string, boolean>>({});

  useEffect(() => {
    if (!isUnlocked) return;
    const loadData = async () => {
      try {
        const data = await fetchVault();
        setVaultEntries(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, [isUnlocked]);

  const handleUnlock = (e: React.FormEvent) => {
    e.preventDefault();
    if (pin === "vault789") {
      setIsUnlocked(true);
      setPinError("");
    } else {
      setPinError("Invalid Vault PIN");
    }
  };

  const handleReveal = async (ref_id: string) => {
    if (revealedSecrets[ref_id]) {
      // Toggle off if already revealed
      const newRevealed = { ...revealedSecrets };
      delete newRevealed[ref_id];
      setRevealedSecrets(newRevealed);
      return;
    }

    setRevealing(prev => ({ ...prev, [ref_id]: true }));
    try {
      const result = await retrieveVault(ref_id, "admin", "Dashboard audit");
      if (result.success) {
        setRevealedSecrets(prev => ({ ...prev, [ref_id]: result.plaintext }));
      } else {
        alert("Reveal failed: " + result.message);
      }
    } catch (err) {
      console.error(err);
      alert("Failed to reveal secret.");
    } finally {
      setRevealing(prev => ({ ...prev, [ref_id]: false }));
    }
  };

  if (!isUnlocked) {
    return (
      <div className="flex flex-col items-center justify-center h-[70vh] animate-in fade-in">
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-8 max-w-md w-full text-center">
          <div className="p-4 bg-amber-500/10 rounded-full inline-block mb-4">
            <Lock className="w-10 h-10 text-amber-500" />
          </div>
          <h2 className="text-2xl font-bold text-white mb-2">SecureReveal Vault</h2>
          <p className="text-slate-400 mb-6">Secondary authentication required to access encrypted secrets.</p>
          
          <form onSubmit={handleUnlock}>
            <input
              type="password"
              placeholder="Enter Vault PIN"
              value={pin}
              onChange={(e) => setPin(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-lg py-3 px-4 text-center text-xl tracking-[0.5em] text-white focus:outline-none focus:border-amber-500 transition-colors mb-4"
              autoFocus
            />
            {pinError && <p className="text-red-500 text-sm mb-4">{pinError}</p>}
            <button
              type="submit"
              className="w-full py-3 bg-amber-600 hover:bg-amber-500 text-white font-semibold rounded-lg transition-colors"
            >
              Unlock Vault
            </button>
          </form>
        </div>
      </div>
    );
  }

  if (loading) return <div className="text-slate-400">Loading vault records...</div>;

  return (
    <div className="space-y-6 animate-in fade-in duration-500">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">SecureReveal Vault</h1>
          <p className="text-slate-400">Encrypted secrets isolated from application log streams.</p>
        </div>
        <div className="flex items-center gap-2 bg-emerald-500/10 text-emerald-500 px-4 py-2 rounded-lg text-sm font-medium border border-emerald-500/20">
          <ShieldCheck className="w-4 h-4" />
          AES-128-CBC Encryption Active
        </div>
      </div>

      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left">
            <thead className="text-xs text-slate-400 uppercase bg-slate-950/50 border-b border-slate-800">
              <tr>
                <th className="px-6 py-4">Reference ID</th>
                <th className="px-6 py-4">Timestamp</th>
                <th className="px-6 py-4">SCS Score</th>
                <th className="px-6 py-4">Pod UID</th>
                <th className="px-6 py-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody>
              {vaultEntries.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-6 py-8 text-center text-slate-500">
                    No secrets currently held in vault.
                  </td>
                </tr>
              ) : (
                vaultEntries.map((entry: any) => (
                  <tr key={entry.ref_id} className="border-b border-slate-800 hover:bg-slate-800/50 transition-colors">
                    <td className="px-6 py-4 font-mono">
                      <div className="text-emerald-400">{entry.ref_id}</div>
                      {revealedSecrets[entry.ref_id] && (
                        <div className="mt-2 p-2 bg-slate-950 rounded border border-emerald-500/30 text-slate-200 text-xs break-all">
                          {revealedSecrets[entry.ref_id]}
                        </div>
                      )}
                    </td>
                    <td className="px-6 py-4 text-slate-300">{new Date(entry.created_at || entry.timestamp).toLocaleString()}</td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2">
                        <div className="w-full bg-slate-800 rounded-full h-2 max-w-[100px]">
                          <div 
                            className={`h-2 rounded-full ${entry.scsc_score || entry.score >= 80 ? 'bg-red-500' : 'bg-amber-500'}`}
                            style={{ width: `${entry.scs_score || entry.score || 0}%` }}
                          />
                        </div>
                        <span className="text-slate-300 font-medium">{entry.scs_score || entry.score}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 font-mono text-xs text-slate-500">{entry.pod_name || entry.pod_uid}</td>
                    <td className="px-6 py-4 text-right">
                      <button 
                        onClick={() => handleReveal(entry.ref_id)}
                        disabled={revealing[entry.ref_id]}
                        className="text-sm px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-white transition-colors flex items-center gap-2 ml-auto disabled:opacity-50"
                      >
                        {revealedSecrets[entry.ref_id] ? (
                          <>
                            <EyeOff className="w-4 h-4" />
                            Hide Secret
                          </>
                        ) : (
                          <>
                            <KeyRound className="w-4 h-4" />
                            {revealing[entry.ref_id] ? "Decrypting..." : "Request Reveal"}
                          </>
                        )}
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
