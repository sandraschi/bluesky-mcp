export const API_BASE = "http://127.0.0.1:10760";

export const API = {
  health: `${API_BASE}/api/health`,
  status: `${API_BASE}/api/status`,
  dashboard: `${API_BASE}/api/dashboard`,
  skills: `${API_BASE}/api/skills`,
  tools: `${API_BASE}/api/tools`,
  logs: `${API_BASE}/api/logs`,
  outbox: `${API_BASE}/api/v1/outbox`,
  notifications: `${API_BASE}/api/v1/notifications`,
  timeline: `${API_BASE}/api/v1/timeline`,
  llmChat: `${API_BASE}/api/llm/chat`,
  composeAssist: `${API_BASE}/api/compose/assist`,
} as const;
