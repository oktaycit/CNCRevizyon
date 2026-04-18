#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}"

source "${HOME}/Projeler/CNCRevizyon/.venv/bin/activate"
export PYTHONUNBUFFERED=1
export PATH="${HOME}/.nvm/versions/node/v20.20.2/bin:${PATH}"
export QWEN_BIN="${HOME}/.nvm/versions/node/v20.20.2/bin/qwen"

exec python projeler_ai_worker.py
