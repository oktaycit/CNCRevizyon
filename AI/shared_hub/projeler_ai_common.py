#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


PROJELER_ROOT = Path(os.getenv("PROJELER_ROOT", str(Path.home() / "Projeler")))
HUB_ROOT = Path(os.getenv("PROJELER_AI_HUB_ROOT", str(PROJELER_ROOT / ".ai-hub")))
RUNTIME_DIR = HUB_ROOT / "runtime"
RESULTS_DIR = RUNTIME_DIR / "results"
GOALS_FILE = RUNTIME_DIR / "goals.json"

PROJECT_PRESETS: Dict[str, List[Dict[str, str]]] = {
    "default": [
        {
            "id": "summary",
            "label": "Proje Ozeti",
            "title": "Proje ozetini hazirla",
            "prompt": "Bu proje klasorunun amacini, ana bilesenlerini ve dikkat edilmesi gereken riskleri kisa bir raporda ozetle.",
            "run_mode": "report",
        },
        {
            "id": "review",
            "label": "Risk Taramasi",
            "title": "Risk ve teknik borc taramasi",
            "prompt": "Bu projede dikkat edilmesi gereken riskleri, eksik testleri ve teknik borclari listele.",
            "run_mode": "report",
        },
        {
            "id": "test-plan",
            "label": "Test Plani",
            "title": "Test ve dogrulama plani",
            "prompt": "Bu proje icin calistirilabilir test, dogrulama ve smoke test adimlarini cikar.",
            "run_mode": "report",
        },
    ],
    "CNCRevizyon": [
        {
            "id": "cnc-safety",
            "label": "Guvenlik Kontrolu",
            "title": "CNC guvenlik kontrolu",
            "prompt": "CNC, EtherCAT ve simulasyon tarafinda guvenlik risklerini ve insan onayi gerektiren adimlari listele.",
            "run_mode": "report",
        },
    ],
    "irrigation": [
        {
            "id": "build-check",
            "label": "Build Kontrolu",
            "title": "Build ve kod sagligi kontrolu",
            "prompt": "Bu projede build akisini, muhtemel derleme sorunlarini ve hizli duzeltme onceliklerini raporla.",
            "run_mode": "report",
        },
    ],
}


def now_iso() -> str:
    return datetime.now().astimezone().isoformat()


def ensure_layout() -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    if not GOALS_FILE.exists():
        write_json(GOALS_FILE, {"goals": []})


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f"{path.name}.{uuid.uuid4().hex}.tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def load_json(path: Path, default: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    if not path.exists():
        return default or {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return default or {}


def load_goals() -> Dict[str, Any]:
    ensure_layout()
    return load_json(GOALS_FILE, {"goals": []})


def save_goals(payload: Dict[str, Any]) -> None:
    write_json(GOALS_FILE, payload)


def discover_projects() -> List[Dict[str, str]]:
    ensure_layout()
    projects: List[Dict[str, str]] = []
    for entry in sorted(PROJELER_ROOT.iterdir()):
        if not entry.is_dir():
            continue
        if entry.name.startswith(".") or entry.name == ".ai-hub":
            continue
        projects.append({
            "name": entry.name,
            "path": str(entry),
        })
    return projects


def goals_summary(goals: List[Dict[str, Any]]) -> Dict[str, Any]:
    counts = {"pending": 0, "running": 0, "done": 0, "failed": 0}
    for goal in goals:
        status = goal.get("status", "pending")
        counts[status] = counts.get(status, 0) + 1
    return {
        "counts": counts,
        "total": len(goals),
        "projects": len(discover_projects()),
    }


def load_result_for_goal(goal: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    result_path = goal.get("result_path")
    if not result_path:
        return None
    path = Path(result_path)
    return load_json(path, None) if path.exists() else None


def load_result_from_path(result_path: Optional[str]) -> Optional[Dict[str, Any]]:
    if not result_path:
        return None
    path = Path(result_path)
    return load_json(path, None) if path.exists() else None


def presets_for_project(project_name: str) -> List[Dict[str, str]]:
    presets = list(PROJECT_PRESETS.get("default", []))
    if project_name in PROJECT_PRESETS:
        presets.extend(PROJECT_PRESETS[project_name])
    return presets
