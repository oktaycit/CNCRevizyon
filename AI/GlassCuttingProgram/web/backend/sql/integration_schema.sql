CREATE TABLE IF NOT EXISTS integration_jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id TEXT NOT NULL UNIQUE,
    order_id TEXT NOT NULL,
    order_no TEXT,
    source_system TEXT NOT NULL DEFAULT 'herofis',
    target_system TEXT NOT NULL DEFAULT 'glasscuttingprogram',
    status TEXT NOT NULL,
    triggered_by TEXT,
    force_reoptimize INTEGER NOT NULL DEFAULT 0,
    error_message TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS integration_order_payloads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id TEXT NOT NULL,
    order_id TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY(job_id) REFERENCES integration_jobs(job_id)
);

CREATE TABLE IF NOT EXISTS optimization_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    optimization_run_id TEXT NOT NULL UNIQUE,
    job_id TEXT NOT NULL,
    order_id TEXT NOT NULL,
    status TEXT NOT NULL,
    total_sheets_used REAL,
    total_waste_area REAL,
    efficiency REAL,
    message TEXT,
    optimized_at TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY(job_id) REFERENCES integration_jobs(job_id)
);

CREATE TABLE IF NOT EXISTS optimization_line_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    optimization_run_id TEXT NOT NULL,
    line_id TEXT NOT NULL,
    optimized INTEGER NOT NULL DEFAULT 0,
    assigned_batch_no TEXT,
    sheet_count REAL,
    waste_area REAL,
    efficiency REAL,
    FOREIGN KEY(optimization_run_id) REFERENCES optimization_results(optimization_run_id)
);

CREATE TABLE IF NOT EXISTS optimization_files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    optimization_run_id TEXT NOT NULL,
    file_type TEXT NOT NULL,
    file_name TEXT,
    file_url TEXT NOT NULL,
    FOREIGN KEY(optimization_run_id) REFERENCES optimization_results(optimization_run_id)
);

CREATE TABLE IF NOT EXISTS order_sync_status (
    order_id TEXT PRIMARY KEY,
    latest_optimization_run_id TEXT,
    optimizer_status TEXT,
    marked_in_herofis_at TEXT,
    updated_by TEXT,
    updated_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_integration_jobs_order_id
    ON integration_jobs(order_id);

CREATE INDEX IF NOT EXISTS idx_payloads_order_id
    ON integration_order_payloads(order_id);

CREATE INDEX IF NOT EXISTS idx_results_order_id
    ON optimization_results(order_id);

