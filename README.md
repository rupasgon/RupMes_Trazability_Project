# RupMes Trazability

Portal MES con backend FastAPI, frontend React/Vite y esquema PostgreSQL para trazabilidad, maestros, seguridad, reporting e ingestión industrial.

## Qué incluye

- Backend API: `src/rupmes/views/`
- Modelos y esquema SQLAlchemy: `src/rupmes/models/`
- Migraciones Alembic: `alembic/`
- Frontend portal: `frontend/`
- Conector industrial externo: `production_connector/`

## Estructura

```text
src/rupmes/
  core/           # Configuración, DB y utilidades base
  models/         # Modelos SQLAlchemy
  repositories/   # Acceso a datos
  controllers/    # Lógica de negocio
  services/       # Seguridad y servicios transversales
  views/          # API y CLI
frontend/         # Portal React/Vite
alembic/          # Migraciones
production_connector/  # Conector SQL/MQTT/OPC UA
```

## Antes de arrancar

Hay 3 preguntas que decidir primero:

1. ¿Vas a usar Python + Vite en local o Docker?
2. ¿La base de datos es interna del `docker compose` o externa?
3. ¿La base externa ya tiene estructura y datos base, o está vacía?

Según eso, usa uno de estos escenarios.

## Escenario 1: desarrollo local sin Docker

Úsalo si quieres trabajar con backend y frontend en modo desarrollo.

### Backend

1. Crea y activa entorno virtual:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e .
```

2. Define `DATABASE_URL`:

```bash
set DATABASE_URL=postgresql+psycopg2://USER:PASS@localhost:5432/mes_db
```

3. Si la base está vacía, crea estructura y datos base:

```bash
alembic upgrade head
python -m rupmes init-db
```

4. Arranca la API:

```bash
uvicorn rupmes.views.api:app --host 0.0.0.0 --port 8011 --reload
```

### Frontend

1. Instala dependencias:

```bash
cd frontend
npm install
copy .env.example .env
```

2. En `frontend/.env` deja como mínimo:

```env
VITE_API_URL=http://localhost:8011
VITE_DEFAULT_LANG=es
VITE_CSRF_COOKIE_NAME=rupmes_csrf
```

3. Arranca Vite:

```bash
npm run dev
```

4. Abre:

- Portal: `http://localhost:5173`
- API: `http://localhost:8011`
- Swagger: `http://localhost:8011/docs`

## Escenario 2: Docker con base interna

Úsalo si quieres levantar todo con `docker compose`, incluida la base PostgreSQL.

### Configuración

1. Copia `.env.example` a `.env`
2. Ajusta solo lo necesario

Configuración mínima típica:

```env
POSTGRES_USER=rupmes
POSTGRES_PASSWORD=rupmes
POSTGRES_DB=mes_db
DATABASE_URL=postgresql+psycopg2://rupmes:rupmes@db:5432/mes_db

DB_PORT=5432
BACKEND_PORT=8011
FRONTEND_PORT=8080
PGADMIN_PORT=5050

VITE_API_URL=http://localhost:8011
FRONTEND_ORIGINS=http://localhost:8080

WAIT_FOR_DB_ON_STARTUP=true
WAIT_FOR_DB_TIMEOUT=60
RUN_DB_MIGRATIONS=true
RUN_DB_SEED=true
```

### Arranque

```bash
docker compose up --build
```

### URLs

- Portal: `http://localhost:8080`
- API: `http://localhost:8011`
- Swagger: `http://localhost:8011/docs`
- pgAdmin: `http://localhost:5050`

## Escenario 3: Docker con base externa ya inicializada

Úsalo si la base PostgreSQL es externa y ya tiene:

- estructura creada
- migraciones aplicadas
- datos base necesarios

### Configuración

Ejemplo:

```env
DATABASE_URL=postgresql+psycopg2://rupmes_user:password@dbserver:5432/mes_db

BACKEND_PORT=8011
FRONTEND_PORT=8080
PGADMIN_PORT=5050

VITE_API_URL=http://localhost:8011
FRONTEND_ORIGINS=http://localhost:8080

WAIT_FOR_DB_ON_STARTUP=true
WAIT_FOR_DB_TIMEOUT=60
RUN_DB_MIGRATIONS=false
RUN_DB_SEED=false
```

### Arranque

```bash
docker compose up --build app frontend
```

No hace falta levantar `db`.

## Escenario 4: Docker con base externa vacía o incompleta

Úsalo si la base PostgreSQL es externa, pero RupMes debe crear estructura o datos base.

### Caso A: base vacía

```env
RUN_DB_MIGRATIONS=true
RUN_DB_SEED=true
```

### Caso B: estructura creada pero faltan datos base

```env
RUN_DB_MIGRATIONS=false
RUN_DB_SEED=true
```

### Caso C: estructura creada, datos creados, pero quieres que RupMes gestione futuras migraciones

```env
RUN_DB_MIGRATIONS=true
RUN_DB_SEED=false
```

### Arranque

```bash
docker compose up --build app frontend
```

## Qué significan las variables importantes

### Base de datos

- `DATABASE_URL`: cadena real de conexión usada por la aplicación
- `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`: útiles sobre todo para la base interna Docker
- `DB_PORT`: puerto publicado de PostgreSQL cuando usas la base interna

### API y portal

- `BACKEND_PORT`: puerto HTTP del backend FastAPI
- `FRONTEND_PORT`: puerto HTTP del portal
- `PGADMIN_PORT`: puerto HTTP de pgAdmin
- `VITE_API_URL`: URL del backend que se incrusta en el build del frontend

Importante:

- `VITE_API_URL` se aplica al compilar el frontend
- si la cambias, debes reconstruir el contenedor frontend

### Arranque automático

- `WAIT_FOR_DB_ON_STARTUP`: espera a que la BD responda antes de arrancar
- `WAIT_FOR_DB_TIMEOUT`: tiempo máximo de espera
- `RUN_DB_MIGRATIONS`: ejecuta `alembic upgrade head`
- `RUN_DB_SEED`: ejecuta `python -m rupmes init-db`

### Cookies y CORS

- `FRONTEND_ORIGINS`: orígenes permitidos por CORS para el navegador
- `COOKIE_SECURE`: usa cookies seguras solo para HTTPS
- `COOKIE_SAMESITE`: política de cookies
- `SESSION_COOKIE_NAME`: nombre de cookie de sesión
- `CSRF_COOKIE_NAME`: nombre de cookie CSRF

## Reglas prácticas para evitar errores comunes

### 1. No mezcles hosts distintos en portal y API

Si abres el portal por:

- `http://localhost:8080`

usa también:

```env
VITE_API_URL=http://localhost:8011
FRONTEND_ORIGINS=http://localhost:8080
```

Si prefieres `127.0.0.1`, usa `127.0.0.1` en ambos.

No mezcles:

- portal con `localhost`
- API con `127.0.0.1`

porque eso suele romper la sesión por cookies.

### 2. Si cambias `VITE_API_URL`, recompila frontend

```bash
docker compose down
docker compose build --no-cache frontend
docker compose up -d app frontend
```

### 3. Si la base externa usa contraseñas con caracteres especiales

Escápalos en `DATABASE_URL`.

Ejemplo:

```env
DATABASE_URL=postgresql+psycopg2://user:MyPass%24word@dbserver:5432/mes_db
```

## Verificación rápida tras arranque

### Backend

Abre:

- `http://localhost:8011/health`
- `http://localhost:8011/docs`

`GET /` devuelve `404` y es normal. No hay home page HTML en la API.

### Frontend

Abre:

- `http://localhost:8080`

### Login por defecto

Si la base fue inicializada con seed:

- Usuario: `admin`
- Contraseña: `admin123`

También existe:

- Usuario: `machine`
- Contraseña: `machine123`

## Datos base que crea el seed

`python -m rupmes init-db` crea o completa:

- tenant `DEFAULT`
- branding básico
- estados base
- grupos
- roles
- permisos
- usuarios `admin` y `machine`

Lógica de seed:

- `src/rupmes/controllers/seed_controller.py`

## API principal

Arranque manual de backend:

```bash
uvicorn rupmes.views.api:app --host 0.0.0.0 --port 8011 --reload
```

Endpoints clave:

- `POST /auth/login`
- `POST /auth/logout`
- `GET /auth/me`
- `GET /health`
- `GET /permissions`
- `GET /roles`
- `GET /users`
- `GET /items`
- `GET /statuses`
- `POST /production-reports`
- `POST /production-reports/ingest`
- `GET /production-ingest-clients`
- `POST /production-ingest-clients`

## Producción e integraciones industriales

### Tabla principal

- `production_report`

### Inserción desde portal o backoffice

- `POST /production-reports`
- requiere sesión + CSRF

### Inserción máquina a máquina

- `POST /production-reports/ingest`
- requiere `X-Client-Id` y `X-API-Key`

### Gestión de credenciales técnicas

Desde el portal:

- `Administración > Integraciones`

Cada cliente de integración puede quedar limitado por:

- `plant_code`
- `line_code`
- `station_code`
- `machine_code`
- `source_system`

Si el payload no coincide con el ámbito del cliente, la API rechaza la inserción.

### Recomendación

Crear un cliente distinto por:

- línea
- PLC
- SCADA
- gateway
- conector SQL/MQTT/OPC UA

## Conector externo

Hay un conector independiente para:

- SQL
- MQTT
- OPC UA

Documentación:

- `production_connector/README.md`

## Alembic

Aplicar migraciones:

```bash
alembic upgrade head
```

Si la base ya existe pero no tiene historial Alembic:

```bash
alembic stamp head
```

Crear una nueva migración:

```bash
alembic revision -m "your message" --autogenerate
```

Rollback:

```bash
alembic downgrade -1
```

## Tests

Instala dependencias dev:

```bash
pip install -e .[dev]
```

Ejecuta:

```bash
pytest
```

## Notas

- La fuente de verdad del esquema es `src/rupmes/models/tables.py`
- Las migraciones viven en `alembic/versions/`
- Los scripts SQL de `Database_Scripts/` son auxiliares o heredados; no son la referencia principal
