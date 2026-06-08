#!/bin/sh
set -eu

if [ "${WAIT_FOR_DB_ON_STARTUP:-true}" = "true" ]; then
  python - <<'PY'
import os
import sys
import time

from sqlalchemy import create_engine, text

database_url = os.environ["DATABASE_URL"]
timeout = int(os.getenv("WAIT_FOR_DB_TIMEOUT", "60"))
deadline = time.time() + timeout
last_error = None

while time.time() < deadline:
    try:
        engine = create_engine(database_url, pool_pre_ping=True)
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        sys.exit(0)
    except Exception as exc:  # pragma: no cover - container startup path
        last_error = exc
        time.sleep(2)

print(f"Database not available after {timeout}s: {last_error}", file=sys.stderr)
sys.exit(1)
PY
fi

if [ "${RUN_DB_MIGRATIONS:-true}" = "true" ]; then
  python -m alembic upgrade head
fi

if [ "${RUN_DB_SEED:-true}" = "true" ]; then
  python -m rupmes init-db
fi

exec uvicorn rupmes.views.api:app --host 0.0.0.0 --port "${BACKEND_PORT:-8011}"
