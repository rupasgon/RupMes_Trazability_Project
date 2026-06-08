#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${1:?Usage: build-bundle.sh <project-root> [python-executable]}"
PYTHON_EXE="${2:-python3}"

CONNECTOR_ROOT="${PROJECT_ROOT}/production_connector"
LINUX_ROOT="${CONNECTOR_ROOT}/linux"
BUILD_VENV_PATH="${CONNECTOR_ROOT}/.build-venv"
PYTHON_BUILD="${BUILD_VENV_PATH}/bin/python"
PYINSTALLER_EXE="${BUILD_VENV_PATH}/bin/pyinstaller"
DIST_ROOT="${CONNECTOR_ROOT}/dist/linux"
BUILD_ROOT="${CONNECTOR_ROOT}/build/linux"
SPEC_ROOT="${BUILD_ROOT}/spec"
CLI_DIST="${DIST_ROOT}/cli"
CLI_WORK="${BUILD_ROOT}/cli"

echo "Creating build virtual environment in ${BUILD_VENV_PATH}"
"${PYTHON_EXE}" -m venv "${BUILD_VENV_PATH}"
"${PYTHON_BUILD}" -m pip install --upgrade pip
"${PYTHON_BUILD}" -m pip install -e "${PROJECT_ROOT}[connector,connector-build]"

mkdir -p "${CLI_DIST}" "${CLI_WORK}" "${SPEC_ROOT}"

echo "Building Linux CLI bundle"
"${PYINSTALLER_EXE}" --noconfirm --clean --onedir --contents-directory . --name rupmes-connector --distpath "${CLI_DIST}" --workpath "${CLI_WORK}" --specpath "${SPEC_ROOT}" "${LINUX_ROOT}/entry_cli.py"

echo "Bundle created in ${DIST_ROOT}"
