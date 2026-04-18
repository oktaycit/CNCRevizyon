#!/usr/bin/env python3
from __future__ import annotations

import asyncio
import os
import shlex
import subprocess
import sys
import time
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, Optional
import re

from projeler_ai_common import RESULTS_DIR, load_goals, now_iso, save_goals, write_json


TIMEOUT_SECONDS = 180
MAX_RETRIES = 2
QWEN_BIN = os.getenv("QWEN_BIN", str(Path.home() / ".nvm" / "versions" / "node" / "v20.20.2" / "bin" / "qwen"))
PROJELER_ROOT = Path(os.getenv("PROJELER_ROOT", str(Path.home() / "Projeler")))
CNCREVIZYON_ROOT = Path(os.getenv("CNCREVIZYON_ROOT", str(PROJELER_ROOT / "CNCRevizyon")))
ORCHESTRATION_DIR = CNCREVIZYON_ROOT / "AI" / "orchestration"
CONTEXT_FILE_CANDIDATES = (
    "README.md",
    "README",
    "pyproject.toml",
    "package.json",
    "requirements.txt",
    "Makefile",
    "docker-compose.yml",
    "docker-compose.yaml",
    ".env.example",
)
CONTEXT_EXCLUDED_DIRS = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    "dist",
    "build",
    ".next",
    ".idea",
    ".vscode",
}
MAX_TREE_ENTRIES = 80
MAX_FILE_SNIPPET_CHARS = 2500
MAX_SOURCE_SNIPPETS = 6
MAX_GIT_STATUS_CHARS = 1500
MAX_MATCH_LINES = 40
STALE_RUNNING_SECONDS = TIMEOUT_SECONDS + 30
MAX_EXPLICIT_PATH_SNIPPETS = 8

if str(ORCHESTRATION_DIR) not in sys.path:
    sys.path.insert(0, str(ORCHESTRATION_DIR))

try:
    from ai_orchestrator import AIOrchestrator, load_config_from_file
    ORCHESTRATOR_AVAILABLE = True
except Exception:
    ORCHESTRATOR_AVAILABLE = False


def next_pending_goal(payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    return next((goal for goal in payload.get("goals", []) if goal.get("status") == "pending"), None)


def set_status(goal: Dict[str, Any], status: str, **extra: Any) -> None:
    goal["status"] = status
    goal["updated_at"] = now_iso()
    for key, value in extra.items():
        goal[key] = value


def parse_iso(value: Any) -> Optional[datetime]:
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value))
    except ValueError:
        return None


def reconcile_stale_goals(payload: Dict[str, Any]) -> bool:
    now = datetime.now().astimezone()
    changed = False
    for goal in payload.get("goals", []):
        if goal.get("status") != "running":
            continue

        started_at = parse_iso(goal.get("started_at"))
        finished_at = parse_iso(goal.get("finished_at"))
        stale = started_at and (now - started_at).total_seconds() > STALE_RUNNING_SECONDS
        inconsistent = finished_at is not None
        if not stale and not inconsistent:
            continue

        goal["updated_at"] = now_iso()
        goal["finished_at"] = goal.get("finished_at") or now_iso()
        if goal.get("cancel_requested"):
            goal["status"] = "canceled"
            goal["last_warning"] = "Takilan calisma iptal edilmis olarak kapatildi."
            goal["last_error"] = None
            goal["cancel_requested"] = False
        else:
            goal["status"] = "failed"
            goal["last_error"] = "Takilan running kaydi otomatik kapatildi."
        changed = True
    return changed


def build_prompt(goal: Dict[str, Any]) -> str:
    base = [
        f"Project path: {goal['project_path']}",
        f"Project name: {goal['project_name']}",
        "Work only within the current project directory.",
    ]
    if goal.get("run_mode") == "auto_edit":
        base.append("If code edits are needed, make them carefully and summarize the changes.")
    else:
        base.append("Prefer analysis, diagnosis, or a concrete plan. Avoid destructive actions.")
    base.append("Do not ask the user to share files, open files, or paste code. You already have repository context below.")
    base.append("If the requested files exist in the provided context, work from them directly.")
    base.append("If context is still insufficient, state the exact missing path or symbol and propose the smallest concrete next change anyway.")
    base.append("Use the repository context below as real project evidence. Do not claim you cannot access the project.")
    base.append(build_project_context(Path(goal["project_path"]), goal))
    base.append("Conversation history:")
    base.append(format_conversation(goal))
    base.append(f"Current user request: {goal['prompt']}")
    base.append(
        "At the very end of your response, append this exact machine-readable summary block and fill it honestly.\n"
        "Do not skip it.\n"
        "=== AGENT SUMMARY START ===\n"
        "REQUEST_STATUS: applied | not_applied | analysis_only | uncertain\n"
        "EVIDENCE: short concrete sentence\n"
        "CHANGED_FILES: comma-separated paths or none\n"
        "=== AGENT SUMMARY END ==="
    )
    return "\n".join(base)


def format_conversation(goal: Dict[str, Any]) -> str:
    messages = goal.get("messages") or []
    if not messages:
        return f"user: {goal.get('prompt', '')}"

    formatted = []
    for message in messages[-12:]:
        role = message.get("role", "user")
        content = str(message.get("content", "")).strip()
        if not content:
            continue
        formatted.append(f"{role}: {content}")
    return "\n".join(formatted) if formatted else f"user: {goal.get('prompt', '')}"


def run_command(command: list[str], cwd: Path) -> str:
    try:
        result = subprocess.run(
            command,
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )
    except Exception:
        return ""
    output = (result.stdout or "").strip()
    if not output:
        output = (result.stderr or "").strip()
    return output


def get_git_status_lines(project_path: Path) -> list[str]:
    output = run_command(["git", "status", "--short"], project_path)
    return [line.strip() for line in output.splitlines() if line.strip()]


def parse_agent_summary(stdout: str) -> Dict[str, Any]:
    text = stdout or ""
    start_marker = "=== AGENT SUMMARY START ==="
    end_marker = "=== AGENT SUMMARY END ==="
    start = text.rfind(start_marker)
    end = text.rfind(end_marker)
    parsed: Dict[str, Any] = {}
    if start == -1 or end == -1 or end <= start:
        return parsed

    block = text[start + len(start_marker):end].strip()
    for line in block.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        parsed[key.strip().lower()] = value.strip()
    return parsed


def infer_keywords(goal: Dict[str, Any]) -> list[str]:
    text = f"{goal.get('title', '')} {goal.get('prompt', '')}".lower()
    keyword_pairs = [
        ("risk", ["risk", "teknik", "borc", "test", "safety", "interlock", "alarm"]),
        ("build", ["build", "derle", "compile", "make", "cmake"]),
        ("gpio", ["gpio", "sensor", "i2c", "serial", "modbus", "scd", "dht"]),
        ("web", ["web", "flask", "socket", "api", "frontend", "kiosk"]),
        ("cad", ["freecad", "cad", "bom", "macro", "schedule"]),
    ]
    matched = []
    for label, aliases in keyword_pairs:
        if any(alias in text for alias in aliases):
            matched.extend(aliases[:4])
    return list(dict.fromkeys(matched))[:8]


def extract_explicit_paths(goal: Dict[str, Any]) -> list[str]:
    text = f"{goal.get('title', '')}\n{goal.get('prompt', '')}"
    matches = re.findall(r"([A-Za-z0-9_./-]+\.[A-Za-z0-9_]+)", text)
    cleaned = []
    for item in matches:
        normalized = item.strip().strip("`'\"")
        if "/" in normalized or "." in normalized:
            cleaned.append(normalized)
    return list(dict.fromkeys(cleaned))[:MAX_EXPLICIT_PATH_SNIPPETS]


def collect_explicit_path_snippets(project_path: Path, goal: Dict[str, Any]) -> list[str]:
    snippets: list[str] = []
    requested = extract_explicit_paths(goal)
    if not requested:
        return snippets

    all_files = [path for path in project_path.rglob("*") if path.is_file()]
    for requested_path in requested:
        normalized = requested_path.lstrip("./")
        direct = project_path / normalized
        matched_path: Optional[Path] = direct if direct.exists() and direct.is_file() else None
        if matched_path is None:
            target_name = Path(normalized).name
            matched_path = next((path for path in all_files if path.name == target_name), None)
        if matched_path is None:
            continue
        try:
            content = matched_path.read_text(encoding="utf-8", errors="ignore").strip()
        except OSError:
            continue
        if not content:
            continue
        relative = matched_path.relative_to(project_path)
        snippets.append(f"Explicit target file: {relative}\n{content[:MAX_FILE_SNIPPET_CHARS]}")
        if len(snippets) >= MAX_EXPLICIT_PATH_SNIPPETS:
            break
    return snippets


def collect_source_snippets(project_path: Path, keywords: list[str]) -> list[str]:
    snippets: list[str] = []
    candidates: list[Path] = []
    allowed_suffixes = {".py", ".js", ".ts", ".tsx", ".jsx", ".c", ".cpp", ".h", ".hpp", ".md", ".txt", ".yml", ".yaml", ".toml", ".mk"}

    for entry in sorted(project_path.rglob("*")):
        try:
            relative = entry.relative_to(project_path)
        except ValueError:
            continue
        if any(part in CONTEXT_EXCLUDED_DIRS for part in relative.parts):
            continue
        if not entry.is_file() or entry.suffix.lower() not in allowed_suffixes:
            continue
        candidates.append(entry)
        if len(candidates) >= 120:
            break

    for path in candidates:
        if len(snippets) >= MAX_SOURCE_SNIPPETS:
            break
        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        lowered = content.lower()
        if keywords and not any(keyword in lowered or keyword in path.name.lower() for keyword in keywords):
            continue
        snippet = content[:MAX_FILE_SNIPPET_CHARS].strip()
        if not snippet:
            continue
        relative = path.relative_to(project_path)
        snippets.append(f"Source file: {relative}\n{snippet}")
    return snippets


def collect_keyword_matches(project_path: Path, keywords: list[str]) -> str:
    if not keywords:
        return ""
    lines: list[str] = []
    for path in sorted(project_path.rglob("*")):
        try:
            relative = path.relative_to(project_path)
        except ValueError:
            continue
        if any(part in CONTEXT_EXCLUDED_DIRS for part in relative.parts):
            continue
        if not path.is_file():
            continue
        try:
            content = path.read_text(encoding="utf-8", errors="ignore").splitlines()
        except OSError:
            continue
        for index, line in enumerate(content, start=1):
            lowered = line.lower()
            if any(keyword in lowered for keyword in keywords):
                lines.append(f"{relative}:{index}: {line.strip()[:180]}")
                if len(lines) >= MAX_MATCH_LINES:
                    return "\n".join(lines)
    return "\n".join(lines)


def build_project_context(project_path: Path, goal: Dict[str, Any]) -> str:
    sections = []

    tree_lines = []
    for entry in sorted(project_path.rglob("*")):
        try:
            relative = entry.relative_to(project_path)
        except ValueError:
            continue
        parts = relative.parts
        if any(part in CONTEXT_EXCLUDED_DIRS for part in parts):
            continue
        if len(tree_lines) >= MAX_TREE_ENTRIES:
            break
        if entry.is_dir():
            tree_lines.append(f"{relative}/")
        elif entry.is_file():
            tree_lines.append(str(relative))
    if tree_lines:
        sections.append("Project tree sample:\n" + "\n".join(f"- {line}" for line in tree_lines))

    git_status = run_command(["git", "status", "--short"], project_path)
    if git_status:
        sections.append("Git status summary:\n" + git_status[:MAX_GIT_STATUS_CHARS])

    snippets = []
    for candidate in CONTEXT_FILE_CANDIDATES:
        path = project_path / candidate
        if not path.exists() or not path.is_file():
            continue
        try:
            content = path.read_text(encoding="utf-8", errors="ignore").strip()
        except OSError:
            continue
        if not content:
            continue
        snippets.append(
            f"File: {candidate}\n{content[:MAX_FILE_SNIPPET_CHARS]}"
        )
    if snippets:
        sections.append("Important file excerpts:\n" + "\n\n".join(snippets))

    explicit_snippets = collect_explicit_path_snippets(project_path, goal)
    if explicit_snippets:
        sections.append("Requested target file excerpts:\n" + "\n\n".join(explicit_snippets))

    keywords = infer_keywords(goal)
    if keywords:
        sections.append("Keyword hints:\n" + ", ".join(keywords))

    source_snippets = collect_source_snippets(project_path, keywords)
    if source_snippets:
        sections.append("Relevant source excerpts:\n" + "\n\n".join(source_snippets))

    matches = collect_keyword_matches(project_path, keywords)
    if matches:
        sections.append("Keyword matches:\n" + matches)

    return "\n\n".join(sections) if sections else "Repository context unavailable."


def run_orchestrator(goal: Dict[str, Any]) -> Dict[str, Any]:
    if not ORCHESTRATOR_AVAILABLE:
        raise RuntimeError("ai_orchestrator import edilemedi")

    config_path = ORCHESTRATION_DIR / "orchestrator_config.json"
    if not config_path.exists():
        raise RuntimeError(f"orchestrator config bulunamadi: {config_path}")

    prompt = build_prompt(goal)
    started_at = now_iso()
    configs = load_config_from_file(str(config_path))
    orchestrator = AIOrchestrator(configs)
    response = asyncio.run(orchestrator.run_single_model(prompt, 0))

    return {
        "started_at": started_at,
        "finished_at": now_iso(),
        "backend": "ai_orchestrator",
        "model_id": response.model_id,
        "status": response.status,
        "latency_ms": response.latency_ms,
        "returncode": 0 if response.status == "success" else 1,
        "stdout": response.content,
        "stderr": response.error or "",
    }


def run_qwen(goal: Dict[str, Any]) -> Dict[str, Any]:
    prompt = build_prompt(goal)
    approval_mode = "auto-edit" if goal.get("run_mode") == "auto_edit" else "default"
    command = [
        QWEN_BIN,
        "--approval-mode",
        approval_mode,
        "-o",
        "text",
        prompt,
    ]
    started_at = now_iso()
    result = subprocess.run(
        command,
        cwd=goal["project_path"],
        capture_output=True,
        text=True,
        timeout=TIMEOUT_SECONDS,
        check=False,
    )
    return {
        "started_at": started_at,
        "finished_at": now_iso(),
        "backend": "qwen_cli",
        "command": shlex.join(command),
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


def run_goal(goal: Dict[str, Any]) -> Dict[str, Any]:
    try:
        return run_orchestrator(goal)
    except Exception as exc:
        fallback = run_qwen(goal)
        fallback["fallback_error"] = str(exc)
        return fallback


def process_one() -> bool:
    payload = load_goals()
    if reconcile_stale_goals(payload):
        save_goals(payload)
    goal = next_pending_goal(payload)
    if not goal:
        return False

    set_status(goal, "running", started_at=now_iso())
    save_goals(payload)
    git_status_before = get_git_status_lines(Path(goal["project_path"]))

    try:
        result = run_goal(goal)
        status = "done" if result.get("returncode") == 0 else "failed"
    except subprocess.TimeoutExpired as exc:
        result = {
            "started_at": goal.get("started_at"),
            "finished_at": now_iso(),
            "error": f"timeout after {TIMEOUT_SECONDS}s",
            "stdout": exc.stdout,
            "stderr": exc.stderr,
        }
        status = "failed"
    except Exception as exc:  # pragma: no cover
        result = {"started_at": goal.get("started_at"), "finished_at": now_iso(), "error": str(exc)}
        status = "failed"

    git_status_after = get_git_status_lines(Path(goal["project_path"]))
    changed_files = sorted(set(git_status_after) - set(git_status_before))
    agent_summary = parse_agent_summary(result.get("stdout", ""))
    agent_request_status = agent_summary.get("request_status")
    agent_evidence = agent_summary.get("evidence")
    agent_changed_files = agent_summary.get("changed_files")
    if goal.get("run_mode") == "auto_edit":
        implementation_state = "implemented" if changed_files else "not_applied"
    else:
        implementation_state = "analysis_only"
    result["implementation_state"] = implementation_state
    result["system_assessment"] = implementation_state
    result["agent_request_status"] = agent_request_status or "missing"
    result["agent_evidence"] = agent_evidence or ""
    result["agent_changed_files"] = agent_changed_files or ""
    result["changed_files"] = changed_files
    result["git_status_before"] = git_status_before[:50]
    result["git_status_after"] = git_status_after[:50]

    result_path = RESULTS_DIR / f"{goal['id']}.json"
    write_json(result_path, {"goal": goal, "status": status, "result": result})

    retry_count = int(goal.get("retry_count", 0) or 0)
    cancel_requested = bool(goal.get("cancel_requested"))
    if cancel_requested:
        status = "canceled"
    retryable = status == "failed" and retry_count < MAX_RETRIES
    final_status = "pending" if retryable else status
    error_text = result.get("error") or (result.get("stderr") if status == "failed" else "")
    warning_text = result.get("stderr") if status == "done" else ""
    if status == "canceled":
        error_text = None
        warning_text = "Kullanici iptal talebi gonderdi."
    updates = {
        "finished_at": now_iso(),
        "result_path": str(result_path),
        "last_error": error_text or None,
        "last_warning": warning_text or None,
        "retry_count": retry_count + 1 if retryable else retry_count,
        "cancel_requested": False,
    }
    if final_status in {"done", "failed", "canceled"}:
        messages = goal.setdefault("messages", [])
        assistant_content = result.get("stdout") or result.get("error") or result.get("stderr") or ""
        if assistant_content:
            messages.append({
                "role": "assistant",
                "content": assistant_content,
                "created_at": now_iso(),
                "attempt_status": final_status,
            })
    if final_status == "done":
        updates["last_success_result_path"] = str(result_path)
        updates["last_success_finished_at"] = now_iso()
        updates["last_success_status"] = "done"
    if retryable:
        updates["last_retry_at"] = now_iso()
    set_status(goal, final_status, **updates)
    save_goals(payload)
    print(f"[{now_iso()}] processed {goal['id']} -> {final_status}")
    return True


def main() -> None:
    while True:
        processed = process_one()
        time.sleep(8 if processed else 15)


if __name__ == "__main__":
    main()
