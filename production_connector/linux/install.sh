#!/usr/bin/env bash
set -euo pipefail

INSTANCE_ID="${1:?Usage: install.sh <instance-id>}"
INSTANCE_ID_PATTERN='^[a-z0-9][a-z0-9-]{1,62}$'
if [[ ! "${INSTANCE_ID}" =~ ${INSTANCE_ID_PATTERN} ]]; then
  echo "Instance ID must use lowercase letters, digits and hyphens." >&2
  exit 2
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
INSTALL_ROOT="/opt/rupmes-connectors"
EXPECTED_ROOT="${INSTALL_ROOT}/${INSTANCE_ID}"
CONFIG_PATH="${PROJECT_ROOT}/production_connector/config.json"

CONNECTOR_ROOT="${PROJECT_ROOT}/production_connector"
DIST_ROOT="${CONNECTOR_ROOT}/dist/linux/cli"
BUNDLE_EXE="${DIST_ROOT}/rupmes-connector/rupmes-connector"
SERVICE_NAME="rupmes-production-connector@${INSTANCE_ID}"
SERVICE_FILE="/etc/systemd/system/rupmes-production-connector@.service"
SERVICE_TEMPLATE="${CONNECTOR_ROOT}/linux/rupmes-production-connector@.service"

if [[ "${PROJECT_ROOT}" != "${EXPECTED_ROOT}" ]]; then
  echo "Install this package at ${EXPECTED_ROOT}; current path is ${PROJECT_ROOT}." >&2
  exit 2
fi
if [[ ! -f "${CONFIG_PATH}" ]]; then
  echo "Missing ${CONFIG_PATH}. Create and configure it before installing." >&2
  exit 2
fi
if [[ ! -f "${CONNECTOR_ROOT}/secrets.env" ]]; then
  echo "Missing ${CONNECTOR_ROOT}/secrets.env. Create it from secrets.env.template before installing." >&2
  exit 2
fi

if [[ -x "${BUNDLE_EXE}" ]]; then
  echo "Using bundled connector executable at ${BUNDLE_EXE}"
else
  echo "Bundled executable not found; this installer requires a Linux bundle." >&2
  exit 1
fi

if ! id -u rupmes >/dev/null 2>&1; then
  sudo useradd --system --home-dir /nonexistent --shell /sbin/nologin rupmes
fi

sudo chown -R root:rupmes "${PROJECT_ROOT}"
sudo find "${PROJECT_ROOT}" -type d -exec chmod 0750 {} +
sudo find "${PROJECT_ROOT}" -type f -exec chmod 0640 {} +
sudo chmod 0750 "${BUNDLE_EXE}" "${CONNECTOR_ROOT}/linux/install.sh" "${CONNECTOR_ROOT}/linux/uninstall.sh"
sudo chmod 0640 "${CONNECTOR_ROOT}/secrets.env"
sudo install -m 0644 "${SERVICE_TEMPLATE}" "${SERVICE_FILE}"

sudo systemctl daemon-reload
sudo systemctl enable --now "${SERVICE_NAME}"

echo "Installed ${SERVICE_NAME}"
echo "Status: sudo systemctl status ${SERVICE_NAME}"
echo "Logs:   sudo journalctl -u ${SERVICE_NAME} -f"
