// API Client for Influencer Help AI Content Copilot

const API_BASE = '/api';

export const getAuthToken = () => localStorage.getItem('copilot_token');
export const setAuthToken = (token) => localStorage.setItem('copilot_token', token);
export const removeAuthToken = () => localStorage.removeItem('copilot_token');

async function request(endpoint, options = {}) {
  const token = getAuthToken();
  const headers = {
    'Content-Type': 'application/json',
    ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
    ...options.headers,
  };

  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers,
  });

  if (response.status === 204) {
    return null;
  }

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    const errorMsg = data.detail || 'An unexpected server error occurred.';
    throw new Error(errorMsg);
  }

  return data;
}

export const api = {
  // Auth
  register: (payload) => request('/auth/register', { method: 'POST', body: JSON.stringify(payload) }),
  login: (payload) => request('/auth/login', { method: 'POST', body: JSON.stringify(payload) }),
  loginDemo: () => request('/auth/demo', { method: 'POST' }),
  logout: () => request('/auth/logout', { method: 'POST' }),
  getMe: () => request('/auth/me'),

  // Profile
  getProfile: () => request('/profile'),
  updateProfile: (payload) => request('/profile', { method: 'PUT', body: JSON.stringify(payload) }),
  resetDemoProfile: () => request('/profile/reset-demo', { method: 'POST' }),

  // Ideas
  generateIdeas: (payload) => request('/ideas/generate', { method: 'POST', body: JSON.stringify(payload) }),
  listIdeas: (status) => request(`/ideas${status ? `?status_filter=${status}` : ''}`),
  getIdea: (id) => request(`/ideas/${id}`),
  selectIdea: (id) => request(`/ideas/${id}/select`, { method: 'POST' }),
  deleteIdea: (id) => request(`/ideas/${id}`, { method: 'DELETE' }),

  // Briefs
  generateBrief: (payload) => request('/briefs/generate', { method: 'POST', body: JSON.stringify(payload) }),
  listBriefs: (status) => request(`/briefs${status ? `?status_filter=${status}` : ''}`),
  getBrief: (id) => request(`/briefs/${id}`),
  updateBrief: (id, payload) => request(`/briefs/${id}`, { method: 'PUT', body: JSON.stringify(payload) }),
  updateBriefStatus: (id, status) => request(`/briefs/${id}/status`, { method: 'PUT', body: JSON.stringify({ status }) }),
  regenerateHooks: (id) => request(`/briefs/${id}/regenerate-hooks`, { method: 'POST' }),
  deleteBrief: (id) => request(`/briefs/${id}`, { method: 'DELETE' }),

  // Feedback
  submitFeedback: (payload) => request('/feedback', { method: 'POST', body: JSON.stringify(payload) }),
  getFeedback: () => request('/feedback'),

  // Workspace
  getWorkspace: () => request('/workspace'),
  getWorkspaceSummary: () => request('/workspace/summary'),

  // System & Diagnostics
  getHealth: () => request('/health'),
  getAiDiagnostic: () => request('/ai/diagnostic'),
};
