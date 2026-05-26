# RupMes Trazability (Python)

This repo provides a Python-driven PostgreSQL schema for a MES trazability database.

## MVC structure

- Models: `src/rupmes/models/`
- Controllers: `src/rupmes/controllers/`
- Views (CLI): `src/rupmes/views/`
- Core utilities: `src/rupmes/core/`
- Services: `src/rupmes/services/`
- Repositories: `src/rupmes/repositories/`

## Project layout

```
src/rupmes/
  core/           # Config and DB session helpers
  models/         # SQLAlchemy models (tables)
  repositories/   # Data access layer
  controllers/    # Business logic
  services/       # Cross-cutting services (security)
  views/          # CLI and API entrypoints
tests/            # Pytest suite
alembic/          # Migration scripts
```

## Quick start

1) Create and activate a virtual environment, then install dependencies:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e .
```

2) Set your connection string:

```bash
set DATABASE_URL=postgresql+psycopg2://USER:PASS@localhost:5432/mes_db
```

3) Create tables and seed defaults:

```bash
python -m rupmes init-db
```

## Frontend (portal)

The frontend lives in `frontend/` and uses Vite + React.

Install dependencies:

```bash
cd frontend
npm install
```

Configure API URL:

```
copy .env.example .env
```

Run dev server:

```bash
npm run dev
```

Open:
- `http://localhost:5173`

Docker (frontend + backend):

```bash
docker compose up --build
```

Open:
- API: `http://localhost:8000`
- Portal: `http://localhost:8080`

## CLI

- Initialize DB: `python -m rupmes init-db`

## API (FastAPI)

Start the API:

```bash
uvicorn rupmes.views.api:app --reload
```

Endpoints:
- `POST /auth/login`
- `POST /auth/logout`
- `GET /auth/me`
- `GET /health`
- `POST /production-reports`
- `POST /production-reports/ingest`
- `GET /production-ingest-clients`
- `GET /production-ingest-clients/{client_id}`
- `POST /production-ingest-clients`
- `PATCH /production-ingest-clients/{client_id}`
- `DELETE /production-ingest-clients/{client_id}`
- `GET /production-reports/{report_id}`
- `GET /production-reports/traceability/{serial_number}`
- `GET /production-reports/analytics/daily-total`
- `GET /production-reports/analytics/by-line`
- `GET /production-reports/analytics/ok-nok-by-shift`
- `GET /production-reports/analytics/ftq-fpy`
- `GET /production-reports/analytics/top-defects`
- `GET /production-reports/analytics/average-cycle-time`
- `GET /statuses`
- `POST /statuses`
- `GET /statuses/{status_id}`
- `PATCH /statuses/{status_id}`
- `DELETE /statuses/{status_id}`
- `GET /items`
- `POST /items`
- `GET /items/{item_id}`
- `PATCH /items/{item_id}`
- `DELETE /items/{item_id}`
- `GET /users`
- `POST /users`
- `GET /users/{id_user}`
- `PATCH /users/{id_user}`
- `DELETE /users/{id_user}`
- `GET /routings`
- `POST /routings`
- `GET /routings/{routing_id}`
- `PATCH /routings/{routing_id}`
- `DELETE /routings/{routing_id}`
- `GET /roles`
- `POST /roles`
- `PATCH /roles/{role_id}`
- `DELETE /roles/{role_id}`
- `GET /roles/{role_id}/permissions`
- `PUT /roles/{role_id}/permissions`
- `GET /permissions`
- `GET /users/{id_user}/roles`
- `PUT /users/{id_user}/roles`

Example requests:

```bash
curl http://localhost:8000/health
curl http://localhost:8000/statuses
curl -X POST http://localhost:8000/statuses -H "Content-Type: application/json" \
  -d "{\"status_id\":\"CUSTOM\",\"description_status\":\"Custom status\"}"
```

## Production reports

The project now supports industrial production reporting in a single PostgreSQL database using dimensional fields such as `plant_code`, `line_code`, `station_code`, and `machine_code`. Lines and plants are not split across separate databases.

Main table:
- `public.production_report`

Main files:
- ORM model: `src/rupmes/models/tables.py`
- Repository/controller/API: `src/rupmes/repositories/production_report_repository.py`, `src/rupmes/controllers/production_report_controller.py`, `src/rupmes/views/api.py`
- Alembic migration: `alembic/versions/b1f302d8a9b1_add_production_report.py`, `alembic/versions/c42d0d7f2a10_add_production_ingest_clients.py`
- SQL scripts: `Database_Scripts/SQL_create_production_report.sql`, `Database_Scripts/SQL_create_production_report_indexes.sql`, `Database_Scripts/SQL_insert_production_report_samples.sql`, `Database_Scripts/SQL_create_production_ingest_clients.sql`

Validation rules:
- `result` only accepts `OK`, `NOK`, `SCRAP`, `REWORK`
- `serial_number` cannot be blank
- `line_code` is required and cannot be blank
- `production_datetime` is required

Example insert through API:

```bash
curl -X POST http://localhost:8000/production-reports \
  -H "Content-Type: application/json" \
  -H "X-CSRF-Token: <csrf_cookie_value>" \
  -d "{\"plant_code\":\"PLANT-ES\",\"line_code\":\"LINE-A\",\"serial_number\":\"SN-000001\",\"result\":\"OK\",\"production_datetime\":\"2026-05-26T06:15:00\",\"cycle_time_seconds\":42.315,\"target_cycle_time_seconds\":45.000,\"source_system\":\"MES\"}"
```

Recommended machine-to-machine ingestion from production lines:

- Preferred model: create one ingest client per line, station, PLC, SCADA, or MES connector.
- Each client has its own `client_id` and `api_key`.
- Authentication is done with headers `X-Client-Id` and `X-API-Key`, so no browser login or CSRF flow is required.
- Keep `plant_code`, `line_code`, `station_code`, and `machine_code` in the payload to identify origin within the same PostgreSQL database.
- You can optionally scope each ingest client to a fixed `plant_code`, `line_code`, `station_code`, `machine_code`, or `source_system`. If the payload does not match its scope, the API rejects the insert.
- `PRODUCTION_INGEST_API_KEY` remains available as a global fallback for backward compatibility, but per-client credentials are the recommended setup.

Create an ingest client as admin:

```bash
curl -X POST http://localhost:8000/production-ingest-clients \
  -H "Content-Type: application/json" \
  -H "X-CSRF-Token: <csrf_cookie_value>" \
  -d "{\"client_id\":\"LINE-A-PLC\",\"description\":\"PLC linea A\",\"api_key\":\"super-secret-line-a\",\"plant_code\":\"PLANT-ES\",\"line_code\":\"LINE-A\",\"source_system\":\"PLC\",\"is_active\":true}"
```

Example line ingestion:

```bash
curl -X POST http://localhost:8000/production-reports/ingest \
  -H "Content-Type: application/json" \
  -H "X-Client-Id: LINE-A-PLC" \
  -H "X-API-Key: super-secret-line-a" \
  -d "{\"plant_code\":\"PLANT-ES\",\"line_code\":\"LINE-A\",\"station_code\":\"ST-10\",\"machine_code\":\"MC-100\",\"shift_code\":\"M1\",\"serial_number\":\"SN-000001\",\"result\":\"OK\",\"production_datetime\":\"2026-05-26T06:15:00\",\"cycle_time_seconds\":42.315,\"target_cycle_time_seconds\":45.000,\"source_system\":\"PLC\"}"
```

Usage model:
- `POST /production-reports/ingest`: for automatic inserts from industrial lines and machines
- `POST /production-ingest-clients`: for provisioning credentials per line/machine from the admin portal or backoffice
- `POST /production-reports`: for authenticated portal or backoffice users
- Analytics endpoints: for reporting and dashboards

Example analytics calls:

```bash
curl "http://localhost:8000/production-reports/analytics/daily-total?date_from=2026-05-01&date_to=2026-05-31"
curl "http://localhost:8000/production-reports/analytics/by-line?date_from=2026-05-01&date_to=2026-05-31&plant_code=PLANT-ES"
curl "http://localhost:8000/production-reports/analytics/ok-nok-by-shift?date_from=2026-05-26&date_to=2026-05-26&line_code=LINE-A"
curl "http://localhost:8000/production-reports/analytics/ftq-fpy?date_from=2026-05-26&date_to=2026-05-26"
curl "http://localhost:8000/production-reports/analytics/top-defects?date_from=2026-05-26&date_to=2026-05-26&limit=10"
curl "http://localhost:8000/production-reports/traceability/SN-000002"
curl "http://localhost:8000/production-reports/analytics/average-cycle-time?date_from=2026-05-01&date_to=2026-05-31"
```

Metric notes:
- FTQ: first recorded attempt per serial, line, and day with result `OK`
- FPY: serials that completed the filtered day and line without any non-`OK` event and without rework

## Auth (local)

Defaults (seeded):
- User `admin` / password `admin123` (role `ADM`)
- User `machine` / password `machine123` (role `USR`)

Login:
```bash
curl -X POST http://localhost:8000/auth/login -H "Content-Type: application/json" \
  -d "{\"id_user\":\"admin\",\"password\":\"admin123\"}"
```

The API sets:
- `SESSION_COOKIE_NAME` (HttpOnly)
- `CSRF_COOKIE_NAME` (readable by frontend)

For state-changing requests (POST/PUT/PATCH/DELETE), send:
- Header: `X-CSRF-Token: <csrf_cookie_value>`

## Auth configuration (.env)

```
FRONTEND_ORIGINS=http://localhost:5173,http://localhost:3000
COOKIE_SECURE=false
COOKIE_SAMESITE=lax
SESSION_TTL_MINUTES=480
SESSION_COOKIE_NAME=rupmes_session
CSRF_COOKIE_NAME=rupmes_csrf
MULTI_TENANT_ENABLED=false
DEFAULT_TENANT_ID=DEFAULT
```

## Tests

Install dev dependencies:

```bash
pip install -e .[dev]
```

Run tests:

```bash
pytest
```

## Alembic migrations

1) Set `DATABASE_URL` and run:

```bash
alembic upgrade head
```

If your DB was created with `create_all` (no Alembic history), stamp it first:

```bash
alembic stamp head
```

Rollback:

```bash
alembic downgrade -1
```

2) To create new migrations after changing models:

```bash
alembic revision -m "your message" --autogenerate
```

## Notes
- The database schema is defined in `src/rupmes/models/tables.py`.
- Default data seeding is in `src/rupmes/controllers/seed_controller.py`.
- SQL scripts in `Database_Scripts/` are legacy; Python is the source of truth.
