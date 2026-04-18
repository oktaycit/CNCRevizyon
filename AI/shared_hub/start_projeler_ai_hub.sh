#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}"

source "${HOME}/Projeler/CNCRevizyon/.venv/bin/activate"
export PYTHONUNBUFFERED=1

exec python projeler_ai_hub.py
