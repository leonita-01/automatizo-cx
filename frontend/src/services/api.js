const API_BASE = import.meta.env.VITE_API_URL || "";


async function request(path, options = {}, adminKey = "") {
  const headers = {
    ...options.headers,
  };

  if (!(options.body instanceof FormData)) {
    headers["Content-Type"] = "application/json";
  }

  if (adminKey) {
    headers["X-Admin-Key"] = adminKey;
  }

  const response = await fetch(`${API_BASE}/api${path}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let message = `Request failed with status ${response.status}`;
    try {
      const payload = await response.json();
      message = payload.detail || message;
    } catch {
      // The fallback status message is sufficient for non-JSON errors.
    }
    throw new Error(message);
  }

  if (response.status === 204) {
    return null;
  }

  return response.json();
}


export const api = {
  health: () => request("/health"),
  analytics: () => request("/analytics"),
  sendChat: (payload) =>
    request("/chat", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  assessProcess: (payload) =>
    request("/processes/assess", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  listArticles: (query = "") =>
    request(`/knowledge/articles?q=${encodeURIComponent(query)}`),
  createArticle: (payload, adminKey) =>
    request(
      "/knowledge/articles",
      {
        method: "POST",
        body: JSON.stringify(payload),
      },
      adminKey,
    ),
  updateArticle: (articleId, payload, adminKey) =>
    request(
      `/knowledge/articles/${articleId}`,
      {
        method: "PATCH",
        body: JSON.stringify(payload),
      },
      adminKey,
    ),
  deactivateArticle: (articleId, adminKey) =>
    request(
      `/knowledge/articles/${articleId}`,
      { method: "DELETE" },
      adminKey,
    ),
  importArticles: (file, adminKey) => {
    const form = new FormData();
    form.append("file", file);
    return request(
      "/knowledge/articles/import",
      { method: "POST", body: form },
      adminKey,
    );
  },
  listHandoffs: (adminKey) =>
    request("/handoffs", {}, adminKey),
  listAuditEvents: (adminKey) =>
    request("/audit/events", {}, adminKey),
};
