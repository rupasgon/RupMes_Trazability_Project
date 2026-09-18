#!/bin/sh
set -eu

export VITE_API_URL="${VITE_API_URL:-http://localhost:8011}"
export VITE_TENANT_ID="${VITE_TENANT_ID:-}"
export VITE_CSRF_COOKIE_NAME="${VITE_CSRF_COOKIE_NAME:-rupmes_csrf}"
export VITE_DEFAULT_LANG="${VITE_DEFAULT_LANG:-es}"
export VITE_APP_VERSION="${VITE_APP_VERSION:-development}"

cat > /usr/share/nginx/html/app-config.js <<EOF
window.__RUPMES_CONFIG__ = {
  VITE_API_URL: "${VITE_API_URL}",
  VITE_TENANT_ID: "${VITE_TENANT_ID}",
  VITE_CSRF_COOKIE_NAME: "${VITE_CSRF_COOKIE_NAME}",
  VITE_DEFAULT_LANG: "${VITE_DEFAULT_LANG}",
  VITE_APP_VERSION: "${VITE_APP_VERSION}"
};
EOF

exec nginx -g 'daemon off;'
