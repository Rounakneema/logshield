const API_BASE = "/api/v1";

export async function fetchMode() {
  try {
    const res = await fetch(`${API_BASE}/mode`, { cache: 'no-store' });
    if (!res.ok) return { mode: "protected" };
    return res.json();
  } catch (err) {
    return { mode: "protected" };
  }
}

export async function setMode(mode: string) {
  const res = await fetch(`${API_BASE}/mode`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ mode })
  });
  if (!res.ok) throw new Error("Failed to set mode");
  return res.json();
}

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

export async function fetchAuditLogs(params?: { limit?: number; offset?: number; actor?: string; action?: string; outcome?: string }) {
  const q = new URLSearchParams();
  if (params?.limit) q.set("limit", params.limit.toString());
  if (params?.offset) q.set("offset", params.offset.toString());
  if (params?.actor) q.set("actor", params.actor);
  if (params?.action) q.set("action", params.action);
  if (params?.outcome) q.set("outcome", params.outcome);

  const res = await fetch(`${API_BASE}/audit?${q.toString()}`, { cache: 'no-store' });
  if (!res.ok) throw new Error("Failed to fetch audit logs");
  return res.json();
}

export async function verifyAudit() {
  const res = await fetch(`${API_BASE}/audit/verify`, { cache: 'no-store' });
  if (!res.ok) throw new Error("Failed to verify audit chain");
  return res.json();
}

export async function simulateTamper(action: "tamper" | "reset", record_id?: number) {
  const res = await fetch(`${API_BASE}/audit/tamper_demo`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ action, record_id })
  });
  if (!res.ok) throw new Error("Failed to run tamper demo");
  return res.json();
}

export async function fetchSprawl() {
  const res = await fetch(`${API_BASE}/lineage`, { cache: 'no-store' });
  if (!res.ok) throw new Error("Failed to fetch sprawl report");
  return res.json();
}

export async function fetchLogs(service?: string) {
  const url = service && service !== "all" 
    ? `${API_BASE}/logs?service=${encodeURIComponent(service)}` 
    : `${API_BASE}/logs`;
  const res = await fetch(url, { cache: 'no-store' });
  if (!res.ok) throw new Error("Failed to fetch logs");
  return res.json();
}

export async function fetchRawLogs(service?: string) {
  const url = service && service !== "all" 
    ? `${API_BASE}/raw_logs?service=${encodeURIComponent(service)}` 
    : `${API_BASE}/raw_logs`;
  const res = await fetch(url, { cache: 'no-store' });
  if (!res.ok) throw new Error("Failed to fetch raw logs");
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

export async function simulatePipeline(line: string) {
  const res = await fetch(`${API_BASE}/simulate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ line })
  });
  if (!res.ok) throw new Error("Failed to run simulation");
  return res.json();
}
