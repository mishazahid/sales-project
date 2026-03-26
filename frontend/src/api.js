const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "";

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(`API ${response.status}: ${text}`);
  }
  return response.json();
}

export const api = {
  baseUrl: API_BASE_URL,
  health: () => request("/api/health"),
  getLeads: (limit = 5000) => request(`/api/data/leads?limit=${limit}`),
  getEmailEngagement: (limit = 50000) =>
    request(`/api/data/email-engagement?limit=${limit}`),
  getCallTranscripts: (limit = 5000) =>
    request(`/api/data/call-transcripts?limit=${limit}`),
  getRevenueHistory: (limit = 120) =>
    request(`/api/data/revenue-history?limit=${limit}`),
  trainModel: () => request("/api/leads/train", { method: "POST" }),
  topLeads: (limit = 20) => request(`/api/leads/top?limit=${limit}`),
  scoreLead: (leadId) =>
    request("/api/leads/score", {
      method: "POST",
      body: JSON.stringify({ lead_ids: [leadId] })
    }),
  generateEmail: (leadId, variant) =>
    request("/api/emails/generate", {
      method: "POST",
      body: JSON.stringify({ lead_id: leadId, variant })
    }),
  generateAB: (leadId) =>
    request("/api/emails/generate-ab", {
      method: "POST",
      body: JSON.stringify({ lead_id: leadId })
    }),
  riskReport: (limit = 50) => request(`/api/calls/risk-report?limit=${limit}`),
  analyzeCall: (callIdNumber) =>
    request("/api/calls/analyze", {
      method: "POST",
      body: JSON.stringify({ call_id: callIdNumber })
    }),
  copilotSuggestions: (limit = 10) =>
    request(`/api/copilot/daily-suggestions?limit=${limit}`),
  simulateFollowup: (leadId, days, steps) =>
    request("/api/copilot/simulate-followup", {
      method: "POST",
      body: JSON.stringify({ lead_id: leadId, days, steps })
    })
};

