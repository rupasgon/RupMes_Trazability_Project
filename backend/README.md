# MES Traceability System - Backend API

Sistema de Trazabilidad para Manufactura (MES) desarrollado con FastAPI y PostgreSQL.

## Características

- **Autenticación JWT**: Sistema de autenticación seguro con tokens JWT
- **Gestión de Usuarios**: CRUD completo de usuarios con roles (Admin/User)
- **Trazabilidad de Items**: Seguimiento completo del ciclo de vida de productos
- **Historial Completo**: Registro automático de cambios en items
- **Gestión de Manufactura**: Administración de modelos, líneas, celdas y ruteos
- **Relaciones Flexibles**: Sistema de ruteos con ubicaciones y relaciones entre entidades
- **Documentación Automática**: Swagger UI y ReDoc incluidos
- **Seguridad**: Contraseñas hasheadas con bcrypt
- **Validación**: Validación automática de datos con Pydantic

## Estructura del Proyecto

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # Aplicación principal FastAPI
│   ├── config.py            # Configuración y variables de entorno
│   ├── database.py          # Configuración de base de datos
│   ├── models/              # Modelos SQLAlchemy (ORM)
│   │   ├── user.py
│   │   ├── item.py
│   │   ├── manufacturing.py
│   │   └── relationships.py
│   ├── schemas/             # Schemas Pydantic (validación)
│   │   ├── auth.py
│   │   ├── user.py
│   │   ├── item.py
│   │   └── manufacturing.py
│   ├── routes/              # Endpoints de la API
│   │   ├── auth.py
│   │   ├── users.py
│   │   ├── items.py
│   │   ├── manufacturing.py
│   │   └── routings.py
│   ├── services/            # Lógica de negocio
│   └── utils/               # Utilidades
│       ├── security.py      # JWT y hashing
│       └── dependencies.py  # Dependencias de autenticación
├── requirements.txt
├── .env.example
└── README.md
```

## Requisitos

- Python 3.8+
- PostgreSQL 12+
- pip

## Instalación

### 1. Clonar el repositorio

```bash
cd RupMes_Trazability_Project/backend
```

### 2. Crear entorno virtual

```bash
python -m venv venv

# En Linux/Mac:
source venv/bin/activate

# En Windows:
venv\Scripts\activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

Copiar el archivo `.env.example` a `.env` y configurar:

```bash
cp .env.example .env
```

Editar el archivo `.env`:

```env
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=mes_db
DB_USER=rupasgon
DB_PASSWORD=tu_password_aqui

# JWT Configuration
SECRET_KEY=genera-una-clave-secreta-segura-aqui
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# API Configuration
DEBUG=True
```

**Importante**: Generar una SECRET_KEY segura:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 5. Verificar base de datos

Asegúrate de que la base de datos PostgreSQL esté corriendo y las tablas estén creadas:

```bash
# Ejecutar los scripts SQL desde el directorio raíz
psql -U rupasgon -d mes_db -f Database_Scripts/SQL_create_database_mes_db.sql
psql -U rupasgon -d mes_db -f Database_Scripts/SQL_create_user_tables.sql
psql -U rupasgon -d mes_db -f Database_Scripts/SQL_create_items_tables.sql
```

### 6. Actualizar contraseñas por defecto

Las contraseñas en la base de datos están en texto plano. Ejecutar script para hashearlas:

```python
# crear script: update_passwords.py
from app.database import SessionLocal
from app.models.user import User
from app.utils.security import get_password_hash

db = SessionLocal()

# Hashear contraseñas de usuarios por defecto
users = db.query(User).all()
for user in users:
    if len(user.pass_user) < 20:  # Si no está hasheada
        user.pass_user = get_password_hash(user.pass_user)

db.commit()
db.close()
print("Contraseñas actualizadas correctamente")
```

```bash
python update_passwords.py
```

## Ejecutar la Aplicación

### Modo desarrollo

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

O directamente:

```bash
python -m app.main
```

### Modo producción

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

La API estará disponible en:
- **Aplicación**: http://localhost:8000
- **Documentación Swagger**: http://localhost:8000/docs
- **Documentación ReDoc**: http://localhost:8000/redoc

## Endpoints Principales

### Autenticación

- `POST /api/v1/auth/login` - Login y obtener token JWT
- `POST /api/v1/auth/refresh` - Refrescar token

### Usuarios

- `GET /api/v1/users/me` - Obtener usuario actual
- `GET /api/v1/users/` - Listar todos los usuarios (Admin)
- `GET /api/v1/users/{user_id}` - Obtener usuario por ID
- `POST /api/v1/users/` - Crear usuario (Admin)
- `PUT /api/v1/users/{user_id}` - Actualizar usuario (Admin)
- `DELETE /api/v1/users/{user_id}` - Eliminar usuario (Admin)
- `GET /api/v1/users/groups/all` - Listar grupos
- `GET /api/v1/users/status/all` - Listar estados de usuario

### Items (Trazabilidad)

- `GET /api/v1/items/` - Listar items (con filtros)
- `GET /api/v1/items/{item_id}` - Obtener item por ID
- `GET /api/v1/items/{item_id}/history` - Obtener historial de item
- `POST /api/v1/items/` - Crear item
- `PUT /api/v1/items/{item_id}` - Actualizar item (crea historial)
- `DELETE /api/v1/items/{item_id}` - Eliminar item
- `GET /api/v1/items/status/all` - Listar estados de items
- `GET /api/v1/items/stats/by-status` - Estadísticas por estado
- `GET /api/v1/items/stats/by-model` - Estadísticas por modelo

### Manufactura

**Líneas**
- `GET /api/v1/lines` - Listar líneas
- `GET /api/v1/lines/{line_id}` - Obtener línea
- `POST /api/v1/lines` - Crear línea (Admin)
- `PUT /api/v1/lines/{line_id}` - Actualizar línea (Admin)
- `DELETE /api/v1/lines/{line_id}` - Eliminar línea (Admin)

**Celdas**
- `GET /api/v1/cells` - Listar celdas
- `GET /api/v1/cells/{cell_id}` - Obtener celda
- `POST /api/v1/cells` - Crear celda (Admin)
- `PUT /api/v1/cells/{cell_id}` - Actualizar celda (Admin)
- `DELETE /api/v1/cells/{cell_id}` - Eliminar celda (Admin)

**Modelos**
- `GET /api/v1/models` - Listar modelos
- `GET /api/v1/models/{model_id}` - Obtener modelo
- `POST /api/v1/models` - Crear modelo (Admin)
- `PUT /api/v1/models/{model_id}` - Actualizar modelo (Admin)
- `DELETE /api/v1/models/{model_id}` - Eliminar modelo (Admin)

### Ruteos

- `GET /api/v1/routings/` - Listar ruteos
- `GET /api/v1/routings/{routing_id}` - Obtener ruteo
- `POST /api/v1/routings/` - Crear ruteo (Admin)
- `PUT /api/v1/routings/{routing_id}` - Actualizar ruteo (Admin)
- `DELETE /api/v1/routings/{routing_id}` - Eliminar ruteo (Admin)

**Relaciones**
- `POST /api/v1/routings/cell-line` - Crear relación celda-línea
- `GET /api/v1/routings/cell-line/{line_id}` - Obtener celdas por línea
- `POST /api/v1/routings/routing-cell` - Crear relación ruteo-celda
- `GET /api/v1/routings/routing-cell/{routing_id}` - Obtener celdas por ruteo
- `POST /api/v1/routings/routing-model` - Crear relación ruteo-modelo
- `GET /api/v1/routings/routing-model/{model_id}` - Obtener ruteos por modelo

## Ejemplo de Uso

### 1. Login

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin"
```

Respuesta:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 2. Obtener usuario actual

```bash
curl -X GET "http://localhost:8000/api/v1/users/me" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### 3. Crear un item

```bash
curl -X POST "http://localhost:8000/api/v1/items/" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "item_id": "ITEM001",
    "model_id": "MODEL_A",
    "line_id": "LINE_1",
    "location_id": 1,
    "cell_id": "CELL_01",
    "status_id": "PASS",
    "id_user": "admin"
  }'
```

### 4. Obtener historial de item

```bash
curl -X GET "http://localhost:8000/api/v1/items/ITEM001/history" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## Usuarios por Defecto

Después de ejecutar los scripts SQL:

| Usuario | Contraseña | Grupo | Estado |
|---------|-----------|-------|--------|
| admin | admin | ADM | ENB |
| machine | machine | USR | ENB |

**Importante**: Cambiar estas contraseñas en producción.

## Seguridad

- Las contraseñas se hashean con bcrypt
- Autenticación mediante JWT tokens
- Tokens expiran después de 30 minutos (configurable)
- Endpoints protegidos requieren autenticación
- Algunos endpoints requieren rol de administrador
- CORS configurado (ajustar en producción)

## Testing

Para probar la API, usar la documentación interactiva en:
- http://localhost:8000/docs (Swagger UI)

O usar herramientas como:
- Postman
- Insomnia
- curl
- httpie

## Tecnologías Utilizadas

- **FastAPI**: Framework web moderno y rápido
- **SQLAlchemy**: ORM para PostgreSQL
- **Pydantic**: Validación de datos
- **Python-Jose**: Manejo de JWT
- **Passlib**: Hashing de contraseñas
- **Uvicorn**: Servidor ASGI
- **PostgreSQL**: Base de datos relacional

## Próximos Pasos

- [ ] Implementar tests unitarios
- [ ] Agregar logging estructurado
- [ ] Implementar caché con Redis
- [ ] Agregar rate limiting
- [ ] Dockerizar la aplicación
- [ ] Implementar CI/CD
- [ ] Agregar más endpoints de reportes
- [ ] Implementar WebSockets para notificaciones en tiempo real

## Licencia

Este proyecto es privado y confidencial.
