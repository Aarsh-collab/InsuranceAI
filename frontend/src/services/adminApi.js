const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";
const ADMIN_TOKEN_KEY = "admin_token";

export function getAdminToken() {
  return localStorage.getItem(ADMIN_TOKEN_KEY);
}

export function setAdminToken(token) {
  localStorage.setItem(ADMIN_TOKEN_KEY, token);
}

export function clearAdminToken() {
  localStorage.removeItem(ADMIN_TOKEN_KEY);
}

async function requestAdminJson(path) {
  const token = getAdminToken();

  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  let payload = null;
  try {
    payload = await response.json();
  } catch {
    payload = null;
  }

  if (response.status === 401) {
    clearAdminToken();
    const error = new Error("Admin session expired.");
    error.status = 401;
    throw error;
  }

  if (!response.ok) {
    throw new Error(payload?.detail || "Admin request failed.");
  }

  return payload;
}

export function fetchLeads() {
  return requestAdminJson("/admin/leads");
}

export function fetchLeadDetail(sessionId) {
  return requestAdminJson(`/admin/leads/${sessionId}`);
}
