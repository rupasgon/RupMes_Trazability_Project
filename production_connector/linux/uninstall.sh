#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${1:?Usage: uninstall.sh <project-root>}"
SERVICE_NAME="rupmes-production-connector"

if systemctl list-unit-files | grep -q "^${SERVICE_NAME}\.service"; then
  sudo systemctl stop "${SERVICE_NAME}" || true
  sudo systemctl disable "${SERVICE_NAME}" || true
  sudo rm -f "/etc/systemd/system/${SERVICE_NAME}.service"
  sudo systemctl daemon-reload
  echo "Uninstalled ${SERVICE_NAME}"
else
  echo "Service ${SERVICE_NAME} not found"
fi
