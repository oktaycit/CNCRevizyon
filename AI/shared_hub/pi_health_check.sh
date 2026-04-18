#!/usr/bin/env bash
set -euo pipefail

RUNTIME_DIR="${HOME}/Projeler/.ai-hub/runtime"
GOALS_FILE="${RUNTIME_DIR}/goals.json"
RESULTS_DIR="${RUNTIME_DIR}/results"

section() {
  printf '\n== %s ==\n' "$1"
}

service_state() {
  local service="$1"
  local scope="${2:-user}"
  if [[ "${scope}" == "user" ]]; then
    systemctl --user is-active "${service}" 2>/dev/null || echo "unknown"
  else
    systemctl is-active "${service}" 2>/dev/null || echo "unknown"
  fi
}

section "SYSTEM"
if date -Is >/dev/null 2>&1; then
  printf 'Time: %s\n' "$(date -Is)"
else
  printf 'Time: %s\n' "$(date '+%Y-%m-%dT%H:%M:%S%z')"
fi
printf 'Host: %s\n' "$(hostname)"
printf 'Load: %s\n' "$(uptime | sed 's/.*load averages\{0,1\}: //')"
if command -v free >/dev/null 2>&1; then
  free -h | awk 'NR==1 || NR==2 {print}'
elif command -v vm_stat >/dev/null 2>&1; then
  vm_stat | sed -n '1,4p'
else
  echo "Memory info command not available"
fi

section "SERVICES"
printf 'projeler-ai-worker: %s\n' "$(service_state projeler-ai-worker.service)"
printf 'projeler-ai-hub: %s\n' "$(service_state projeler-ai-hub.service)"
printf 'cnc-pi-agent: %s\n' "$(service_state cnc-pi-agent.service)"
printf 'glasscutting-web: %s\n' "$(service_state glasscutting-web.service)"
printf 'nginx: %s\n' "$(service_state nginx.service system)"
printf 'docker: %s\n' "$(service_state docker.service system)"
printf 'tailscaled: %s\n' "$(service_state tailscaled.service system)"

section "TOP PROCESSES"
if ps -eo pid,user,%cpu,%mem,stat,comm,args --sort=-%cpu >/tmp/pi_health_ps.$$ 2>/dev/null; then
  head -n 12 /tmp/pi_health_ps.$$
  rm -f /tmp/pi_health_ps.$$
else
  echo "Process list unavailable in this environment"
fi

section "QUEUE"
python3 - <<'PY'
import json
from pathlib import Path

goals_file = Path.home() / "Projeler/.ai-hub/runtime/goals.json"
payload = json.loads(goals_file.read_text()) if goals_file.exists() else {"goals": []}
goals = payload.get("goals", [])
counts = {}
for goal in goals:
    status = goal.get("status", "unknown")
    counts[status] = counts.get(status, 0) + 1

print("Counts:", counts if counts else {"empty": 0})
recent = goals[-5:]
if recent:
    print("Recent goals:")
    for goal in recent:
      print(
          f"- {goal.get('id')} | {goal.get('project_name')} | {goal.get('status')} | "
          f"{goal.get('run_mode')} | {goal.get('title')}"
      )
      if goal.get("last_error"):
          print(f"  last_error: {str(goal['last_error'])[:180]}")
      if goal.get("last_warning"):
          print(f"  last_warning: {str(goal['last_warning'])[:180]}")
else:
    print("Recent goals: none")
PY

section "RESULTS"
if [[ -d "${RESULTS_DIR}" ]]; then
  ls -lt "${RESULTS_DIR}" | head -n 8
else
  echo "results directory missing"
fi

section "STALE CHECK"
python3 - <<'PY'
import json
from datetime import datetime, timezone
from pathlib import Path

goals_file = Path.home() / "Projeler/.ai-hub/runtime/goals.json"
payload = json.loads(goals_file.read_text()) if goals_file.exists() else {"goals": []}
now = datetime.now().astimezone()
stale = []
for goal in payload.get("goals", []):
    if goal.get("status") != "running":
        continue
    started_at = goal.get("started_at")
    if not started_at:
        stale.append((goal.get("id"), "missing started_at"))
        continue
    try:
        started = datetime.fromisoformat(started_at)
    except ValueError:
        stale.append((goal.get("id"), "invalid started_at"))
        continue
    age = (now - started).total_seconds()
    if age > 240:
        stale.append((goal.get("id"), f"{int(age)}s"))

if stale:
    print("Potentially stale running goals:")
    for goal_id, reason in stale:
        print(f"- {goal_id}: {reason}")
else:
    print("No stale running goals detected.")
PY
