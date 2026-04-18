#!/usr/bin/env python3
"""
Lightweight goal runner for Raspberry Pi.

Goals are stored in AI/orchestration/runtime/goals.json and processed by a
user-level systemd service. This keeps the first MVP simple and safe:

- AI goals call the existing ai_orchestrator pipeline
- simulator_check goals only run the bundled NC300 simulator
- results are written to AI/orchestration/runtime/results/<goal_id>.json
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import subprocess
import time
import uuid
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from ai_orchestrator import AIOrchestrator, load_config_from_file, resolve_model_indices


ROOT_DIR = Path(__file__).resolve().parents[2]
ORCH_DIR = ROOT_DIR / "AI" / "orchestration"
RUNTIME_DIR = ORCH_DIR / "runtime"
RESULTS_DIR = RUNTIME_DIR / "results"
LOGS_DIR = RUNTIME_DIR / "logs"
GOALS_FILE = RUNTIME_DIR / "goals.json"
DEFAULT_CONFIG_PATH = ORCH_DIR / "orchestrator_config.json"
SIMULATOR_PATH = ROOT_DIR / "Firmware" / "RaspberryPi" / "src" / "nc300_simulator.py"


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat()


def ensure_runtime_layout() -> None:
    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    if not GOALS_FILE.exists():
        atomic_write_json(GOALS_FILE, {"goals": []})


def atomic_write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_name(f"{path.name}.{uuid.uuid4().hex}.tmp")
    temp_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temp_path.replace(path)


def load_goals() -> Dict[str, Any]:
    ensure_runtime_layout()
    try:
        return json.loads(GOALS_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        broken_name = GOALS_FILE.with_suffix(".broken.json")
        GOALS_FILE.replace(broken_name)
        atomic_write_json(GOALS_FILE, {"goals": []})
        return {"goals": []}


def save_goals(payload: Dict[str, Any]) -> None:
    atomic_write_json(GOALS_FILE, payload)


def patch_goal_status(goal: Dict[str, Any], status: str, **extra: Any) -> None:
    goal["status"] = status
    goal["updated_at"] = now_iso()
    for key, value in extra.items():
        goal[key] = value


def load_orchestrator():
    config_path = Path(os.getenv("AI_ORCHESTRATOR_CONFIG", str(DEFAULT_CONFIG_PATH)))
    configs = load_config_from_file(str(config_path))
    env_api_key = os.getenv("DASHSCOPE_API_KEY") or os.getenv("QWEN_API_KEY")
    if env_api_key:
        for config in configs:
            config.api_key = env_api_key
    return AIOrchestrator(configs), configs


async def run_ai_goal(goal: Dict[str, Any]) -> Dict[str, Any]:
    orchestrator, configs = load_orchestrator()
    requested_models = goal.get("models")
    model_indices = None

    if requested_models:
        model_indices = resolve_model_indices(configs, requested_models)

    mode = goal.get("mode", "parallel")
    prompt = goal["prompt"]
    task_type = goal.get("task_type")
    aggregate_method = goal.get("aggregate_method", "compare")

    if task_type and model_indices is None:
        routed = {
            "code": ["qwen3-coder-plus", "qwen3-coder-next"],
            "debug": ["qwen3-coder-plus", "qwen3-max-2026-01-23"],
            "optimize": ["qwen3-coder-plus", "qwen3-max-2026-01-23"],
            "documentation": ["kimi-k2.5", "qwen3.5-plus"],
            "review": ["glm-5", "MiniMax-M2.5"],
        }.get(task_type)
        if routed:
            model_indices = resolve_model_indices(configs, routed)

    if mode == "single":
        response = await orchestrator.run_single_model(prompt, model_indices[0] if model_indices else 0)
        return {"mode": mode, "response": asdict(response)}

    if mode == "voting":
        result = await orchestrator.run_with_voting(prompt, model_indices)
        result["all_responses"] = [asdict(item) for item in result.get("all_responses", [])]
        return {"mode": mode, **result}

    if mode == "aggregate":
        result = await orchestrator.run_with_aggregation(
            prompt,
            model_indices=model_indices,
            aggregation_method=aggregate_method,
        )
        result["all_responses"] = [asdict(item) for item in result.get("all_responses", [])]
        return {"mode": mode, **result}

    responses = await orchestrator.run_parallel(prompt, model_indices)
    return {
        "mode": "parallel",
        "responses": [asdict(item) for item in responses],
    }


def run_simulator_goal(goal: Dict[str, Any]) -> Dict[str, Any]:
    seconds = str(goal.get("seconds", 3))
    result = subprocess.run(
        ["python", str(SIMULATOR_PATH), "--demo", "--seconds", seconds, "--json"],
        cwd=str(ROOT_DIR),
        capture_output=True,
        text=True,
        check=False,
    )
    return {
        "mode": "simulator_check",
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


def execute_goal(goal: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
    goal_kind = goal.get("goal_type", "ai")
    started_at = now_iso()

    try:
        if goal_kind == "simulator_check":
            result = run_simulator_goal(goal)
        else:
            result = asyncio.run(run_ai_goal(goal))

        status = "done"
        if goal_kind == "simulator_check" and result.get("returncode") != 0:
            status = "failed"

        result.update({"started_at": started_at, "finished_at": now_iso()})
        return status, result
    except Exception as exc:  # pragma: no cover - defensive path
        return "failed", {
            "started_at": started_at,
            "finished_at": now_iso(),
            "error": str(exc),
        }


def write_result(goal: Dict[str, Any], status: str, result: Dict[str, Any]) -> Path:
    result_path = RESULTS_DIR / f"{goal['id']}.json"
    payload = {
        "goal": goal,
        "status": status,
        "result": result,
    }
    atomic_write_json(result_path, payload)
    return result_path


def process_next_goal() -> Optional[Dict[str, Any]]:
    payload = load_goals()
    goals: List[Dict[str, Any]] = payload.get("goals", [])

    pending = next((goal for goal in goals if goal.get("status", "pending") == "pending"), None)
    if not pending:
        return None

    patch_goal_status(pending, "running", started_at=now_iso())
    save_goals(payload)

    status, result = execute_goal(pending)
    result_path = write_result(pending, status, result)

    patch_goal_status(
        pending,
        status,
        finished_at=now_iso(),
        result_path=str(result_path),
        last_error=result.get("error"),
    )
    save_goals(payload)
    return pending


def submit_goal(
    title: str,
    prompt: str,
    goal_type: str = "ai",
    mode: str = "parallel",
    task_type: Optional[str] = None,
) -> Dict[str, Any]:
    payload = load_goals()
    goal = {
        "id": uuid.uuid4().hex[:12],
        "title": title,
        "prompt": prompt,
        "goal_type": goal_type,
        "mode": mode,
        "task_type": task_type,
        "status": "pending",
        "created_at": now_iso(),
        "updated_at": now_iso(),
    }
    payload.setdefault("goals", []).append(goal)
    save_goals(payload)
    return goal


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Raspberry Pi goal runner")
    parser.add_argument("--once", action="store_true", help="Tek tur çalış ve çık")
    parser.add_argument("--interval", type=int, default=20, help="Kontrol aralığı (saniye)")
    parser.add_argument("--submit-title", type=str, default=None, help="Yeni hedef başlığı")
    parser.add_argument("--submit-prompt", type=str, default=None, help="Yeni hedef prompt'u")
    parser.add_argument(
        "--submit-goal-type",
        type=str,
        default="ai",
        choices=["ai", "simulator_check"],
        help="Yeni hedef tipi",
    )
    parser.add_argument(
        "--submit-mode",
        type=str,
        default="parallel",
        choices=["single", "parallel", "voting", "aggregate"],
        help="AI hedefi için çalışma modu",
    )
    parser.add_argument("--submit-task-type", type=str, default=None, help="code/debug gibi yönlendirme etiketi")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    ensure_runtime_layout()

    if args.submit_title and args.submit_prompt:
        goal = submit_goal(
            title=args.submit_title,
            prompt=args.submit_prompt,
            goal_type=args.submit_goal_type,
            mode=args.submit_mode,
            task_type=args.submit_task_type,
        )
        print(json.dumps(goal, ensure_ascii=False, indent=2))
        return

    while True:
        processed = process_next_goal()
        if processed:
            print(f"[{now_iso()}] processed goal {processed['id']} -> {processed['status']}")
        elif args.once:
            print(f"[{now_iso()}] no pending goals")
            return
        time.sleep(max(args.interval, 2))


if __name__ == "__main__":
    main()
