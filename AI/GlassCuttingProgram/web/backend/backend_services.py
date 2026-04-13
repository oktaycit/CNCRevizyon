#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Shared backend services for persisted settings, reports and imports."""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


SIZE_PATTERN = re.compile(r"(?P<width>\d+(?:\.\d+)?)x(?P<height>\d+(?:\.\d+)?)")


def load_json_file(path: Path, default):
    """Load a JSON file or return the provided default value."""
    if not path.exists():
        return default

    with open(path, "r", encoding="utf-8") as file_handle:
        return json.load(file_handle)


def save_json_file(path: Path, data) -> None:
    """Persist JSON data to disk."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as file_handle:
        json.dump(data, file_handle, indent=2)


def parse_iso_date(date_value: Optional[str]) -> Optional[datetime]:
    """Parse an ISO date or datetime string if present."""
    if not date_value:
        return None

    try:
        return datetime.fromisoformat(date_value)
    except ValueError:
        return None


def _parse_size(size_value: str) -> Dict[str, float]:
    """Extract width and height from serialized size text."""
    match = SIZE_PATTERN.search(size_value or "")
    if not match:
        return {"width": 0.0, "height": 0.0}

    return {
        "width": float(match.group("width")),
        "height": float(match.group("height")),
    }


def _parse_percent(percent_text: str) -> float:
    """Convert percentage text such as '87.00%' into a ratio."""
    if isinstance(percent_text, (int, float)):
        return float(percent_text)

    cleaned = str(percent_text).replace("%", "").strip()
    if not cleaned:
        return 0.0
    return float(cleaned) / 100.0


def _parse_area(area_text: str) -> float:
    """Convert area text such as '2.50 m²' into mm²."""
    if isinstance(area_text, (int, float)):
        return float(area_text)

    cleaned = str(area_text).replace("m²", "").strip()
    if not cleaned:
        return 0.0
    return float(cleaned) * 1_000_000


def load_optimization_reports(reports_dir: Path) -> List[Dict]:
    """Load persisted optimization reports from disk."""
    documents = []
    for file_path in sorted(reports_dir.glob("report_*.json")):
        payload = load_json_file(file_path, {})
        timestamp = parse_iso_date(payload.get("timestamp")) or datetime.fromtimestamp(file_path.stat().st_mtime)
        documents.append({
            "filename": file_path.name,
            "created_at": timestamp,
            "payload": payload,
            "size": file_path.stat().st_size,
        })

    return documents


def build_cutting_history(reports_dir: Path) -> List[Dict]:
    """Normalize optimization reports into analytics-friendly history records."""
    history = []
    for document in load_optimization_reports(reports_dir):
        optimization_result = document["payload"].get("optimization_result", {})
        history.append({
            "created_at": document["created_at"].isoformat(),
            "utilization": _parse_percent(optimization_result.get("utilization", 0)),
            "waste_area": _parse_area(optimization_result.get("waste_area", 0)),
            "total_cuts": int(optimization_result.get("parts_placed", 0) or 0),
            "cutting_time": float(optimization_result.get("estimated_time", 0) or 0),
            "filename": document["filename"],
        })

    return history


def build_report_dataset(
    reports_dir: Path,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
) -> Dict:
    """Aggregate persisted optimization reports into a report-ready dataset."""
    documents = load_optimization_reports(reports_dir)
    filtered = []

    for document in documents:
        created_at = document["created_at"]
        if start_date and created_at < start_date:
            continue
        if end_date and created_at > end_date:
            continue
        filtered.append(document)

    orders = []
    total_cuts = 0
    total_waste = 0.0
    total_time = 0.0
    utilizations = []

    for document in filtered:
        payload = document["payload"]
        optimization_result = payload.get("optimization_result", {})
        utilization = _parse_percent(optimization_result.get("utilization", 0))
        waste_area = _parse_area(optimization_result.get("waste_area", 0))
        parts_placed = int(optimization_result.get("parts_placed", 0) or 0)
        total_cuts += parts_placed
        total_waste += waste_area
        total_time += float(optimization_result.get("estimated_time", 0) or 0)
        utilizations.append(utilization)

        for order in payload.get("orders", []):
            size_info = _parse_size(order.get("size", ""))
            orders.append({
                "order_id": order.get("order_id", ""),
                "glass_type": order.get("glass_type", ""),
                "width": size_info["width"],
                "height": size_info["height"],
                "utilization": utilization,
                "status": "completed",
                "quantity": int(order.get("quantity", 0) or 0),
                "created_at": document["created_at"].isoformat(),
            })

    total_orders = len(orders)
    avg_utilization = sum(utilizations) / len(utilizations) if utilizations else 0.0

    return {
        "total_orders": total_orders,
        "completed_orders": total_orders,
        "total_cuts": total_cuts,
        "avg_utilization": avg_utilization,
        "total_waste": total_waste,
        "total_time": total_time,
        "orders": orders,
        "report_count": len(filtered),
        "utilization_trend": [
            {
                "timestamp": document["created_at"].isoformat(),
                "utilization": _parse_percent(document["payload"].get("optimization_result", {}).get("utilization", 0)),
            }
            for document in filtered
        ],
    }


def build_report_history(reports_dir: Path) -> List[Dict]:
    """Create lightweight report history entries for the frontend."""
    history = []
    for document in reversed(load_optimization_reports(reports_dir)):
        payload = document["payload"]
        optimization_result = payload.get("optimization_result", {})
        history.append({
            "filename": document["filename"],
            "created": document["created_at"].isoformat(),
            "title": f"Optimizasyon Raporu - {document['created_at'].strftime('%d.%m.%Y %H:%M')}",
            "utilization": _parse_percent(optimization_result.get("utilization", 0)),
            "parts_placed": int(optimization_result.get("parts_placed", 0) or 0),
            "size": document["size"],
        })
    return history


def persist_imported_shapes(data_dir: Path, shapes: List[Dict], metadata: Optional[Dict] = None) -> Dict:
    """Persist imported DXF shapes for later use."""
    shape_store = data_dir / "dxf_imported_shapes.json"
    existing = load_json_file(shape_store, {"imports": []})
    import_record = {
        "imported_at": datetime.now().isoformat(),
        "count": len(shapes),
        "metadata": metadata or {},
        "shapes": shapes,
    }
    existing.setdefault("imports", []).append(import_record)
    save_json_file(shape_store, existing)
    return import_record

