FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    BACKEND_PORT=8011

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src ./src
COPY alembic.ini ./
COPY alembic ./alembic
COPY docker/app-start.sh /app/docker/app-start.sh

RUN pip install --no-cache-dir -e .
RUN chmod +x /app/docker/app-start.sh

EXPOSE 8011

CMD ["/app/docker/app-start.sh"]
