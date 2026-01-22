# RupMes Trazability (Python)

This repo provides a Python-driven PostgreSQL schema for a MES trazability database.

## MVC structure

- Models: `src/rupmes/models/`
- Controllers: `src/rupmes/controllers/`
- Views (CLI): `src/rupmes/views/`
- Core utilities: `src/rupmes/core/`
- Services: `src/rupmes/services/`
- Repositories: `src/rupmes/repositories/`

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

## API (FastAPI)

Start the API:

```bash
uvicorn rupmes.views.api:app --reload
```

Endpoints:
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

## Alembic migrations

1) Set `DATABASE_URL` and run:

```bash
alembic upgrade head
```

2) To create new migrations after changing models:

```bash
alembic revision -m "your message" --autogenerate
```

## Notes
- The database schema is defined in `src/rupmes/models/tables.py`.
- Default data seeding is in `src/rupmes/controllers/seed_controller.py`.
- SQL scripts in `Database_Scripts/` are legacy; Python is the source of truth.
