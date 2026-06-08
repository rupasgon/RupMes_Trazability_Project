#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${1:?Usage: install.sh <project-root> <config-path>}"
CONFIG_PATH="${2:?Usage: install.sh <project-root> <config-path>}"

CONNECTOR_ROOT="${PROJECT_ROOT}/production_connector"
DIST_ROOT="${CONNECTOR_ROOT}/dist/linux/cli"
BUNDLE_EXE="${DIST_ROOT}/rupmes-connector/rupmes-connector"
VENV_PATH="${CONNECTOR_ROOT}/.venv"
PYTHON_BIN="${VENV_PATH}/bin/python"
SERVICE_NAME="rupmes-production-connector"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"
SERVICE_TEMPLATE="${CONNECTOR_ROOT}/linux/${SERVICE_NAME}.service"
EXEC_START=""

if [[ -x "${BUNDLE_EXE}" ]]; then
  echo "Using bundled connector executable at ${BUNDLE_EXE}"
  EXEC_START="${BUNDLE_EXE} run --config ${CONFIG_PATH}"
else
  echo "Bundled executable not found. Falling back to Python-based install."
  python3 -m venv "${VENV_PATH}"
  "${PYTHON_BIN}" -m pip install --upgrade pip
  "${PYTHON_BIN}" -m pip install -e "${PROJECT_ROOT}[connector]"
  EXEC_START="${PYTHON_BIN} -m rupmes_connector run --config ${CONFIG_PATH}"
fi

sudo cp "${SERVICE_TEMPLATE}" "${SERVICE_FILE}"
sudo sed -i "s|__PROJECT_ROOT__|${PROJECT_ROOT}|g" "${SERVICE_FILE}"
sudo sed -i "s|__EXEC_START__|${EXEC_START}|g" "${SERVICE_FILE}"

sudo systemctl daemon-reload
sudo systemctl enable "${SERVICE_NAME}"
sudo systemctl restart "${SERVICE_NAME}"

echo "Installed ${SERVICE_NAME}"
echo "Run manually with:"
if [[ -x "${BUNDLE_EXE}" ]]; then
  echo "\"${BUNDLE_EXE}\" run-once --config \"${CONFIG_PATH}\""
else
  echo "\"${PYTHON_BIN}\" -m rupmes_connector run-once --config \"${CONFIG_PATH}\""
fi
