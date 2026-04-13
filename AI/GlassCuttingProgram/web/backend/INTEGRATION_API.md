# Herofis Integration API

This backend skeleton adds a lightweight MVP flow for:

1. Creating an export job from Herofis/CamCAD.
2. Generating or storing a normalized optimizer payload.
3. Saving optimization results from `glasscuttingprogram`.
4. Marking the original order as optimized.

## Files

- `web/backend/integration_api.py`
  Flask blueprint for integration endpoints.
- `web/backend/integration_store.py`
  SQLite persistence layer for jobs, payloads, and results.
- `web/backend/sql/integration_schema.sql`
  Database schema for the MVP.
- `web/backend/http/integration_api.http`
  Manual API requests for quick testing.

## Endpoints

- `POST /api/orders/export-to-optimizer`
- `GET /api/orders/<order_id>/export-payload`
- `POST /api/optimizations/result`
- `GET /api/optimizations/<optimization_run_id>`
- `POST /api/orders/<order_id>/mark-optimized`
- `GET /api/integration/jobs/<job_id>`
- `POST /api/herofis/import-csv`
- `POST /api/herofis/import-json`
- `POST /api/herofis/fetch-json`
- `POST /api/herofis/fetch-live-order`
- `POST /api/herofis/update-live-status`
- `POST /api/integration/herofis-live-optimize`

## Local Data

The SQLite database is created automatically at:

`AI/GlassCuttingProgram/data/integration/integration.db`

## Notes

- The current implementation uses sample payload generation when a real
  Herofis fetch step is not yet wired in.
- This is intentional for MVP work so the optimizer side can be built and
  tested before the live Herofis connector is finalized.
- Live Herofis/CamCAD fetch is now available through `fetch-live-order`.
- The full live integration flow is available through
  `POST /api/integration/herofis-live-optimize`.
- If `targetStatusId` is omitted in that full live flow, the API defaults to
  status `20`, which corresponds to `Production`.
- `targetStatusId` can still be overridden explicitly when needed.

## Quickstart

1. Start the backend on `localhost:5002`.
2. Call `POST /api/herofis/fetch-live-order` to verify that the target
   Herofis/CamCAD order can be fetched successfully.
3. Call `POST /api/integration/herofis-live-optimize` for the full flow.
4. If you do not pass `targetStatusId`, the order will default to
   `20 / Production` after optimization.
5. Use `GET /api/integration/jobs/<job_id>` and
   `GET /api/optimizations/<optimization_run_id>` to verify the result.

Recommended first live test:

- Use an order that is already in the intended target status, or override
  `targetStatusId` to the current status for a no-risk validation.
- Keep `verifySsl: false` only for local testing environments where the
  certificate chain cannot be validated properly.
