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

export async function fetchStats(window?: string) {
  const url = window ? `${API_BASE}/stats?window=${encodeURIComponent(window)}` : `${API_BASE}/stats`;
  const res = await fetch(url, { cache: 'no-store' });
  if (!res.ok) throw new Error("Failed to fetch stats");
  return res.json();
}

export async function fetchVault() {
  const res = await fetch(`${API_BASE}/vault`, { cache: 'no-store' });
  if (!res.ok) throw new Error("Failed to fetch vault");
  return res.json();
}

export async function fetchAuditLogs(params?: { limit?: number; offset?: number; actor?: string; action?: string; outcome?: string; ref_id?: string; q?: string }) {
  const query = new URLSearchParams();
  if (params?.limit) query.set("limit", params.limit.toString());
  if (params?.offset) query.set("offset", params.offset.toString());
  if (params?.actor) query.set("actor", params.actor);
  if (params?.action) query.set("action", params.action);
  if (params?.outcome) query.set("outcome", params.outcome);
  if (params?.ref_id) query.set("ref_id", params.ref_id);
  if (params?.q) query.set("q", params.q);

  const res = await fetch(`${API_BASE}/audit?${query.toString()}`, { cache: 'no-store' });
  if (!res.ok) throw new Error("Failed to fetch audit logs");
  return res.json();
}

export async function fetchRecentReveals() {
  try {
    const res = await fetch(`${API_BASE}/audit/recent_reveals`, { cache: 'no-store' });
    if (!res.ok) return [];
    return res.json();
  } catch (e) {
    return [];
  }
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

export async function fetchLogs(service?: string, window?: string) {
  const params = new URLSearchParams();
  if (service && service !== "all") params.set("service", service);
  if (window) params.set("window", window);
  const qs = params.toString();
  const url = qs ? `${API_BASE}/logs?${qs}` : `${API_BASE}/logs`;
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

export async function fetchTopology() {
  const res = await fetch(`${API_BASE}/topology`, { cache: 'no-store' });
  if (!res.ok) throw new Error("Failed to fetch topology");
  return res.json();
}

export async function toggleQuarantine(service: string, quarantine: boolean) {
  const res = await fetch(`${API_BASE}/topology/quarantine`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ service, quarantine })
  });
  if (!res.ok) throw new Error("Failed to toggle quarantine");
  return res.json();
}

export async function fetchPolicies() {
  const res = await fetch(`${API_BASE}/policies`, { cache: 'no-store' });
  if (!res.ok) return null;
  return res.json();
}

export async function deployPolicies(profile: string, rules?: any[]) {
  const res = await fetch(`${API_BASE}/policies`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ profile, rules })
  });
  if (!res.ok) throw new Error("Failed to deploy policies");
  return res.json();
}
