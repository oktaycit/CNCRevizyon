#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Persistence helpers for the Herofis -> optimizer integration MVP.

The store is intentionally lightweight and SQLite-based so it can run
without extra infrastructure during early integration work.
"""

from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


def utc_now_iso() -> str:
    """Return a UTC ISO-8601 timestamp."""
    return datetime.now(timezone.utc).isoformat()


def _read_schema(schema_path: Path) -> str:
    with open(schema_path, "r", encoding="utf-8") as handle:
        return handle.read()


class IntegrationStore:
    """Simple SQLite repository for integration jobs and optimization results."""

    def __init__(self, base_dir: Path):
        self.base_dir = Path(base_dir)
        self.db_dir = self.base_dir / "data" / "integration"
        self.db_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = self.db_dir / "integration.db"
        self.schema_path = self.base_dir / "web" / "backend" / "sql" / "integration_schema.sql"
        self._initialize()

    @contextmanager
    def connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def _initialize(self) -> None:
        with self.connect() as conn:
            conn.executescript(_read_schema(self.schema_path))

    def create_job(
        self,
        job_id: str,
        order_id: str,
        order_no: str,
        triggered_by: str,
        force_reoptimize: bool,
        status: str,
        source_system: str = "herofis",
        target_system: str = "glasscuttingprogram",
    ) -> None:
        now = utc_now_iso()
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO integration_jobs (
                    job_id, order_id, order_no, source_system, target_system,
                    status, triggered_by, force_reoptimize, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    job_id,
                    order_id,
                    order_no,
                    source_system,
                    target_system,
                    status,
                    triggered_by,
                    int(force_reoptimize),
                    now,
                    now,
                ),
            )

    def update_job_status(self, job_id: str, status: str, error_message: Optional[str] = None) -> None:
        with self.connect() as conn:
            conn.execute(
                """
                UPDATE integration_jobs
                SET status = ?, error_message = ?, updated_at = ?
                WHERE job_id = ?
                """,
                (status, error_message, utc_now_iso(), job_id),
            )

    def save_payload(self, job_id: str, order_id: str, payload: Dict[str, Any]) -> None:
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO integration_order_payloads (job_id, order_id, payload_json, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (job_id, order_id, json.dumps(payload, ensure_ascii=False), utc_now_iso()),
            )

    def get_latest_payload(self, order_id: str) -> Optional[Dict[str, Any]]:
        with self.connect() as conn:
            row = conn.execute(
                """
                SELECT payload_json
                FROM integration_order_payloads
                WHERE order_id = ?
                ORDER BY id DESC
                LIMIT 1
                """,
                (order_id,),
            ).fetchone()
        if not row:
            return None
        return json.loads(row["payload_json"])

    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        with self.connect() as conn:
            row = conn.execute(
                "SELECT * FROM integration_jobs WHERE job_id = ?",
                (job_id,),
            ).fetchone()
        return dict(row) if row else None

    def get_latest_job_for_order(self, order_id: str) -> Optional[Dict[str, Any]]:
        with self.connect() as conn:
            row = conn.execute(
                """
                SELECT *
                FROM integration_jobs
                WHERE order_id = ?
                ORDER BY id DESC
                LIMIT 1
                """,
                (order_id,),
            ).fetchone()
        return dict(row) if row else None

    def save_optimization_result(self, data: Dict[str, Any]) -> None:
        line_results = data.get("lineResults", [])
        files = data.get("files", [])
        summary = data.get("summary", {})
        optimized_at = data.get("optimizedAt") or utc_now_iso()

        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO optimization_results (
                    optimization_run_id, job_id, order_id, status,
                    total_sheets_used, total_waste_area, efficiency,
                    message, optimized_at, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(optimization_run_id) DO UPDATE SET
                    status = excluded.status,
                    total_sheets_used = excluded.total_sheets_used,
                    total_waste_area = excluded.total_waste_area,
                    efficiency = excluded.efficiency,
                    message = excluded.message,
                    optimized_at = excluded.optimized_at
                """,
                (
                    data["optimizationRunId"],
                    data["jobId"],
                    str(data["orderId"]),
                    data["status"],
                    summary.get("totalSheetsUsed"),
                    summary.get("totalWasteArea"),
                    summary.get("efficiency"),
                    data.get("message"),
                    optimized_at,
                    utc_now_iso(),
                ),
            )

            conn.execute(
                "DELETE FROM optimization_line_results WHERE optimization_run_id = ?",
                (data["optimizationRunId"],),
            )
            conn.execute(
                "DELETE FROM optimization_files WHERE optimization_run_id = ?",
                (data["optimizationRunId"],),
            )

            for line in line_results:
                conn.execute(
                    """
                    INSERT INTO optimization_line_results (
                        optimization_run_id, line_id, optimized, assigned_batch_no,
                        sheet_count, waste_area, efficiency
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        data["optimizationRunId"],
                        str(line["lineId"]),
                        int(bool(line.get("optimized", False))),
                        line.get("assignedBatchNo"),
                        line.get("sheetCount"),
                        line.get("wasteArea"),
                        line.get("efficiency"),
                    ),
                )

            for item in files:
                conn.execute(
                    """
                    INSERT INTO optimization_files (
                        optimization_run_id, file_type, file_name, file_url
                    )
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        data["optimizationRunId"],
                        item.get("type"),
                        item.get("name"),
                        item.get("url"),
                    ),
                )

        self.update_job_status(data["jobId"], "result_saved")

    def get_optimization_result(self, optimization_run_id: str) -> Optional[Dict[str, Any]]:
        with self.connect() as conn:
            result = conn.execute(
                "SELECT * FROM optimization_results WHERE optimization_run_id = ?",
                (optimization_run_id,),
            ).fetchone()
            if not result:
                return None

            line_rows = conn.execute(
                """
                SELECT line_id, optimized, assigned_batch_no, sheet_count, waste_area, efficiency
                FROM optimization_line_results
                WHERE optimization_run_id = ?
                ORDER BY id
                """,
                (optimization_run_id,),
            ).fetchall()
            file_rows = conn.execute(
                """
                SELECT file_type, file_name, file_url
                FROM optimization_files
                WHERE optimization_run_id = ?
                ORDER BY id
                """,
                (optimization_run_id,),
            ).fetchall()

        return {
            "optimizationRunId": result["optimization_run_id"],
            "jobId": result["job_id"],
            "orderId": result["order_id"],
            "status": result["status"],
            "summary": {
                "totalSheetsUsed": result["total_sheets_used"],
                "totalWasteArea": result["total_waste_area"],
                "efficiency": result["efficiency"],
            },
            "lineResults": [
                {
                    "lineId": row["line_id"],
                    "optimized": bool(row["optimized"]),
                    "assignedBatchNo": row["assigned_batch_no"],
                    "sheetCount": row["sheet_count"],
                    "wasteArea": row["waste_area"],
                    "efficiency": row["efficiency"],
                }
                for row in line_rows
            ],
            "files": [
                {
                    "type": row["file_type"],
                    "name": row["file_name"],
                    "url": row["file_url"],
                }
                for row in file_rows
            ],
            "message": result["message"],
            "optimizedAt": result["optimized_at"],
        }

    def mark_order_optimized(self, order_id: str, optimization_run_id: str, updated_by: str) -> None:
        now = utc_now_iso()
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO order_sync_status (
                    order_id, latest_optimization_run_id, optimizer_status,
                    marked_in_herofis_at, updated_by, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(order_id) DO UPDATE SET
                    latest_optimization_run_id = excluded.latest_optimization_run_id,
                    optimizer_status = excluded.optimizer_status,
                    marked_in_herofis_at = excluded.marked_in_herofis_at,
                    updated_by = excluded.updated_by,
                    updated_at = excluded.updated_at
                """,
                (order_id, optimization_run_id, "marked_in_herofis", now, updated_by, now),
            )
            conn.execute(
                """
                UPDATE integration_jobs
                SET status = ?, updated_at = ?
                WHERE id = (
                    SELECT id
                    FROM integration_jobs
                    WHERE order_id = ?
                    ORDER BY id DESC
                    LIMIT 1
                )
                """,
                ("marked_in_herofis", now, order_id),
            )
