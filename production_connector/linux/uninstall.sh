#!/usr/bin/env bash
set -euo pipefail

INSTANCE_ID="${1:?Usage: uninstall.sh <instance-id>}"
INSTANCE_ID_PATTERN='^[a-z0-9][a-z0-9-]{1,62}$'
if [[ ! "${INSTANCE_ID}" =~ ${INSTANCE_ID_PATTERN} ]]; then
  echo "Instance ID must use lowercase letters, digits and hyphens." >&2
  exit 2
fi
SERVICE_NAME="rupmes-production-connector@${INSTANCE_ID}"

if systemctl list-unit-files | grep -q "^rupmes-production-connector@\.service"; then
  sudo systemctl stop "${SERVICE_NAME}" || true
  sudo systemctl disable "${SERVICE_NAME}" || true
  sudo systemctl daemon-reload
  echo "Stopped ${SERVICE_NAME}. Package files and configuration were preserved."
else
  echo "Service template rupmes-production-connector@.service not found"
fi
