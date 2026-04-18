#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

cd "${REPO_ROOT}"
mkdir -p AI/orchestration/runtime/logs AI/orchestration/runtime/results

source "${REPO_ROOT}/.venv/bin/activate"
export PYTHONUNBUFFERED=1
export AI_ORCHESTRATOR_CONFIG="${AI_ORCHESTRATOR_CONFIG:-${REPO_ROOT}/AI/orchestration/orchestrator_config.json}"

exec python AI/orchestration/pi_agent_runner.py --interval "${PI_AGENT_INTERVAL:-20}"
