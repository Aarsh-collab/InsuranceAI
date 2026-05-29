const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";
const INSURANCE_TYPE = import.meta.env.VITE_CHAT_INSURANCE_TYPE ?? "life";

async function requestJson(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers ?? {}),
    },
    ...options,
  });

  let payload = null;

  try {
    payload = await response.json();
  } catch {
    payload = null;
  }

  if (!response.ok) {
    const message =
      payload?.detail || payload?.message || "Request failed. Please try again.";
    throw new Error(message);
  }

  return payload;
}

async function requestFormJson(path, formData) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: "POST",
    body: formData,
  });

  let payload = null;

  try {
    payload = await response.json();
  } catch {
    payload = null;
  }

  if (!response.ok) {
    const message =
      payload?.detail || payload?.message || "Upload failed. Please try again.";
    throw new Error(message);
  }

  return payload;
}

export async function createChatSession({ siteId = "demo" } = {}) {
  const account = await requestJson("/accounts", {
    method: "POST",
    body: JSON.stringify({
      site_id: siteId,
    }),
  });

  const session = await requestJson(`/accounts/${account.account_id}/sessions`, {
    method: "POST",
    body: JSON.stringify({
      insurance_type: INSURANCE_TYPE,
    }),
  });

  return {
    accountId: account.account_id,
    sessionId: session.session_id,
    siteId: session.site_id || siteId,
  };
}

export async function sendChatMessage({ sessionId, message }) {
  const searchParams = new URLSearchParams({
    session_id: sessionId,
  });

  const payload = await requestJson(`/chat/router?${searchParams.toString()}`, {
    method: "POST",
    body: JSON.stringify({
      message,
    }),
  });

  const responseText = payload?.response || payload?.reply;

  if (typeof responseText !== "string" || responseText.trim() === "") {
    throw new Error("The assistant returned an empty response.");
  }

  return responseText;
}

export async function uploadDecPage({ sessionId, file }) {
  const searchParams = new URLSearchParams({
    session_id: sessionId,
  });
  const formData = new FormData();
  formData.append("file", file);

  return requestFormJson(`/dec-page/upload?${searchParams.toString()}`, formData);
}
