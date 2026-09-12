const API_BASE = "/api/v1";

export async function fetchStats() {
  const res = await fetch(`${API_BASE}/stats`, { cache: 'no-store' });
  if (!res.ok) throw new Error("Failed to fetch stats");
  return res.json();
}

export async function fetchVault() {
  const res = await fetch(`${API_BASE}/vault`, { cache: 'no-store' });
  if (!res.ok) throw new Error("Failed to fetch vault");
  return res.json();
}

export async function fetchAuditLogs() {
  const res = await fetch(`${API_BASE}/audit`, { cache: 'no-store' });
  if (!res.ok) throw new Error("Failed to fetch audit logs");
  return res.json();
}

export async function fetchSprawl() {
  const res = await fetch(`${API_BASE}/sprawl`, { cache: 'no-store' });
  if (!res.ok) throw new Error("Failed to fetch sprawl report");
  return res.json();
}

export async function fetchLogs() {
  const res = await fetch(`${API_BASE}/logs`, { cache: 'no-store' });
  if (!res.ok) throw new Error("Failed to fetch logs");
  return res.json();
}

export async function retrieveVault(ref_id: string, actor: string, reason: string) {
  const res = await fetch(`${API_BASE}/vault/retrieve`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ ref_id, actor, reason })
  });
  if (!res.ok) throw new Error("Failed to retrieve secret");
  return res.json();
}
