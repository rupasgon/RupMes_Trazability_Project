#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${1:?Usage: install.sh <project-root> <config-path>}"
CONFIG_PATH="${2:?Usage: install.sh <project-root> <config-path>}"

CONNECTOR_ROOT="${PROJECT_ROOT}/production_connector"
VENV_PATH="${CONNECTOR_ROOT}/.venv"
PYTHON_BIN="${VENV_PATH}/bin/python"
SERVICE_NAME="rupmes-production-connector"

python3 -m venv "${VENV_PATH}"
"${PYTHON_BIN}" -m pip install --upgrade pip
"${PYTHON_BIN}" -m pip install -e "${PROJECT_ROOT}[connector]"

sudo cp "${CONNECTOR_ROOT}/linux/${SERVICE_NAME}.service" "/etc/systemd/system/${SERVICE_NAME}.service"
sudo sed -i "s|__PROJECT_ROOT__|${PROJECT_ROOT}|g" "/etc/systemd/system/${SERVICE_NAME}.service"
sudo sed -i "s|__CONFIG_PATH__|${CONFIG_PATH}|g" "/etc/systemd/system/${SERVICE_NAME}.service"

sudo systemctl daemon-reload
sudo systemctl enable "${SERVICE_NAME}"

echo "Installed ${SERVICE_NAME}"
echo "Run manually with:"
echo "\"${PYTHON_BIN}\" -m rupmes_connector run-once --config \"${CONFIG_PATH}\""
