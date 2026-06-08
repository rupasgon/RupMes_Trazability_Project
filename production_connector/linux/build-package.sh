#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${1:?Usage: build-package.sh <project-root> [config-path] [output-root]}"
CONFIG_PATH="${2:-}"
OUTPUT_ROOT="${3:-}"
BUILD_BUNDLE="${BUILD_BUNDLE:-0}"
ZIP_PACKAGE="${ZIP_PACKAGE:-0}"

CONNECTOR_ROOT="${PROJECT_ROOT}/production_connector"
LINUX_ROOT="${CONNECTOR_ROOT}/linux"
DIST_ROOT="${CONNECTOR_ROOT}/dist/linux"
CLI_BUNDLE_ROOT="${DIST_ROOT}/cli/rupmes-connector"
RELEASE_ROOT="${OUTPUT_ROOT:-${CONNECTOR_ROOT}/release/linux}"
PACKAGE_ROOT="${RELEASE_ROOT}/RupMesProductionConnector"
PACKAGE_CONNECTOR_ROOT="${PACKAGE_ROOT}/production_connector"
PACKAGE_LINUX_ROOT="${PACKAGE_CONNECTOR_ROOT}/linux"
PACKAGE_DIST_ROOT="${PACKAGE_CONNECTOR_ROOT}/dist/linux"
PACKAGE_CLI_ROOT="${PACKAGE_DIST_ROOT}/cli"
PACKAGE_STATE_ROOT="${PACKAGE_CONNECTOR_ROOT}/state"
PACKAGE_LOGS_ROOT="${PACKAGE_CONNECTOR_ROOT}/logs"
PACKAGE_ZIP="${RELEASE_ROOT}/RupMesProductionConnector.tar.gz"
SERVICE_NAME="rupmes-production-connector"

if [[ "${BUILD_BUNDLE}" == "1" ]]; then
  "${LINUX_ROOT}/build-bundle.sh" "${PROJECT_ROOT}"
fi

CLI_EXE="${CLI_BUNDLE_ROOT}/rupmes-connector"
if [[ ! -f "${CLI_EXE}" ]]; then
  echo "Linux bundle not found. Run build-bundle.sh first or set BUILD_BUNDLE=1." >&2
  exit 1
fi

rm -rf "${PACKAGE_ROOT}"
mkdir -p "${PACKAGE_LINUX_ROOT}" "${PACKAGE_CLI_ROOT}" "${PACKAGE_STATE_ROOT}" "${PACKAGE_LOGS_ROOT}"

cp "${LINUX_ROOT}/install.sh" "${PACKAGE_LINUX_ROOT}/"
cp "${LINUX_ROOT}/uninstall.sh" "${PACKAGE_LINUX_ROOT}/"
cp "${LINUX_ROOT}/${SERVICE_NAME}.service" "${PACKAGE_LINUX_ROOT}/${SERVICE_NAME}.service"
cp -r "${CLI_BUNDLE_ROOT}/." "${PACKAGE_CLI_ROOT}/"

if [[ -n "${CONFIG_PATH}" ]]; then
  cp "${CONFIG_PATH}" "${PACKAGE_CONNECTOR_ROOT}/config.json"
else
  cp "${CONNECTOR_ROOT}/config.example.json" "${PACKAGE_CONNECTOR_ROOT}/config.template.json"
fi

cat > "${PACKAGE_ROOT}/README.txt" <<'EOF'
RupMes Production Connector

Recommended installation on client machines:

1. Open a shell with sudo permissions.
2. Edit production_connector/config.json if included, or copy config.template.json to config.json and complete it.
3. Install as systemd service:
   ./production_connector/linux/install.sh "<package-root>" "<package-root>/production_connector/config.json"
EOF

if [[ "${ZIP_PACKAGE}" == "1" ]]; then
  rm -f "${PACKAGE_ZIP}"
  mkdir -p "${RELEASE_ROOT}"
  tar -czf "${PACKAGE_ZIP}" -C "${RELEASE_ROOT}" "RupMesProductionConnector"
fi

echo "Linux client package created in ${PACKAGE_ROOT}"
if [[ "${ZIP_PACKAGE}" == "1" ]]; then
  echo "Compressed package created in ${PACKAGE_ZIP}"
fi
