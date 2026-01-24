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
