const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8011";

export const getCookie = (name) => {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(";").shift();
  return "";
};

export const request = async (path, options = {}) => {
  const { method = "GET", data, tenantId, csrfToken } = options;
  const lang = localStorage.getItem("rupmes_lang") || import.meta.env.VITE_DEFAULT_LANG || "es";
  const headers = {
    "Content-Type": "application/json",
    "Accept-Language": lang,
  };
  if (tenantId) {
    headers["X-Tenant-ID"] = tenantId;
  }
  if (csrfToken && method !== "GET") {
    headers["X-CSRF-Token"] = csrfToken;
  }

  const res = await fetch(`${API_URL}${path}`, {
    method,
    headers,
    credentials: "include",
    body: data ? JSON.stringify(data) : undefined,
  });

  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    let message = "Request failed";
    if (body && body.detail) {
      if (Array.isArray(body.detail)) {
        message = body.detail[0]?.msg || JSON.stringify(body.detail);
      } else {
        message = body.detail;
      }
    }
    throw new Error(message);
  }

  return res.status === 204 ? null : res.json();
};
