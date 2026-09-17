const runtimeConfig = window.__RUPMES_CONFIG__ || {};

export const getRuntimeConfig = (key, fallback = "") => runtimeConfig[key] || fallback;
