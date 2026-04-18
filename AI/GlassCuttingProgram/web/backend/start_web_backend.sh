#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../../../.." && pwd)"

cd "${REPO_ROOT}"
source "${REPO_ROOT}/.venv/bin/activate"

export PYTHONUNBUFFERED=1
export GLASSCUTTING_HOST="${GLASSCUTTING_HOST:-127.0.0.1}"
export GLASSCUTTING_PORT="${GLASSCUTTING_PORT:-5001}"
export GLASSCUTTING_DEBUG="${GLASSCUTTING_DEBUG:-false}"

exec python AI/GlassCuttingProgram/web/backend/app.py
