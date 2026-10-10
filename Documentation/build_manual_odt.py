"""Build the editable RupMes operating manual as a native OpenDocument file.

This deliberately uses only the Python standard library so the document can be
recreated on an engineering workstation without a document-generation runtime.
"""

from __future__ import annotations

import html
import zipfile
from pathlib import Path


OUT = Path(__file__).with_name("Manual_Operacion_RupMes.odt")


def esc(value: object) -> str:
    return html.escape(str(value), quote=False)


def paragraph(text: str = "", style: str = "Body") -> str:
    return f'<text:p text:style-name="{style}">{esc(text)}</text:p>'


def title(text: str) -> str:
    return f'<text:p text:style-name="Title">{esc(text)}</text:p>'


def subtitle(text: str) -> str:
    return f'<text:p text:style-name="Subtitle">{esc(text)}</text:p>'


def heading(text: str, level: int, page_break: bool = False) -> str:
    style = f"H{level}" + ("Break" if page_break else "")
    return f'<text:h text:style-name="{style}" text:outline-level="{level}">{esc(text)}</text:h>'


def code(text: str) -> str:
    return f'<text:p text:style-name="Code">{esc(text)}</text:p>'


def note(text: str, label: str = "Nota") -> str:
    return f'<text:p text:style-name="Note"><text:span text:style-name="NoteLabel">{esc(label)}: </text:span>{esc(text)}</text:p>'


def bullets(items: list[str]) -> str:
    body = []
    for item in items:
        body.append(f'<text:list-item>{paragraph(item, "List")}</text:list-item>')
    return '<text:list text:style-name="BulletList">' + ''.join(body) + '</text:list>'


def numbered(items: list[str]) -> str:
    body = []
    for item in items:
        body.append(f'<text:list-item>{paragraph(item, "List")}</text:list-item>')
    return '<text:list text:style-name="NumberList">' + ''.join(body) + '</text:list>'


def table(headers: list[str], rows: list[list[str]], name: str) -> str:
    column_xml = ''.join('<table:table-column table:style-name="TableColumn"/>' for _ in headers)
    header_xml = ''.join(
        f'<table:table-cell table:style-name="TableHeaderCell" office:value-type="string">{paragraph(value, "TableHeader")}</table:table-cell>'
        for value in headers
    )
    row_xml = []
    for row in rows:
        cells = ''.join(
            f'<table:table-cell table:style-name="TableCell" office:value-type="string">{paragraph(value, "TableText")}</table:table-cell>'
            for value in row
        )
        row_xml.append(f'<table:table-row>{cells}</table:table-row>')
    return (
        f'<table:table table:name="{esc(name)}" table:style-name="Table">{column_xml}'
        f'<table:table-header-rows><table:table-row>{header_xml}</table:table-row></table:table-header-rows>'
        + ''.join(row_xml)
        + '</table:table>'
    )


def build_content() -> str:
    parts: list[str] = []
    parts += [
        title("RupMes"),
        subtitle("Manual de configuracion, operacion y despliegue"),
        paragraph("Version de referencia: 1.0.0"),
        paragraph("Documento tecnico-operativo para administradores, IT/OT, responsables de planta e integradores."),
        note("Los ejemplos usan nombres y secretos ficticios. Sustituya siempre usuarios, claves, dominios e identificadores por los aprobados para cada entorno.", "Seguridad"),
        heading("Como usar este manual", 1),
        paragraph("El manual esta organizado por tarea. Los capitulos 1 a 4 explican el modelo funcional. Los capitulos 5 a 9 cubren la instalacion y configuracion. Los capitulos 10 a 13 describen integraciones industriales y la operacion diaria."),
        table(["Necesidad", "Capitulo"], [
            ["Arrancar el portal en un equipo de desarrollo", "5. Desarrollo local"],
            ["Levantar el sistema con Docker", "6. Docker y base de datos"],
            ["Administrar tenants, usuarios y accesos", "3. Seguridad y multi-tenant"],
            ["Enviar trazabilidad desde SQL, MQTT, OPC UA, TCP, Modbus o S7", "10. Integracion industrial"],
            ["Publicar una version en Kubernetes", "12. Kubernetes y Helm"],
            ["Investigar errores habituales", "14. Diagnostico y mantenimiento"],
        ], "ComoUsar"),
        heading("1. Alcance y arquitectura", 1, True),
        paragraph("RupMes es un portal MES de trazabilidad. Centraliza maestros de fabricacion, produccion, consulta de historico, indicadores y recepcion de eventos procedentes de equipos industriales."),
        table(["Componente", "Responsabilidad", "Tecnologia"], [
            ["Portal", "Interfaz de usuarios, administracion, produccion y reports", "React / Vite"],
            ["API", "Reglas de negocio, autenticacion, autorizacion y endpoints", "FastAPI"],
            ["Base de datos", "Datos de negocio, sesiones, configuracion y trazabilidad", "PostgreSQL"],
            ["Conector industrial", "Lee SQL, MQTT, OPC UA, TCP, Modbus o S7 y entrega eventos normalizados", "Servicio Windows/Linux/ARM64"],
            ["Despliegue", "Contenedores, Helm e Ingress", "Docker / Kubernetes"],
        ], "Arquitectura"),
        paragraph("Flujo principal: el portal y los conectores consumen la API. La API aplica autenticacion, comprueba el tenant y persiste en PostgreSQL. La base de datos origen de una linea nunca es la base de datos RupMes; el conector lee del origen y publica en la API."),
        note("No configure triggers SQL que llamen directamente a la API. El conector mantiene un checkpoint y permite reintentos controlados.", "Recomendacion"),
        heading("2. Conceptos funcionales", 1, True),
        heading("2.1 Tenant", 2),
        paragraph("Un tenant representa una unidad aislada de negocio: planta, cliente, empresa o entorno operativo. Los maestros, la produccion, los reports, la configuracion del portal y los clientes de integracion se consultan en el contexto del tenant activo."),
        bullets([
            "Debe existir al menos un tenant activo marcado como predeterminado.",
            "Solo los tenants activos aparecen como seleccionables en el portal.",
            "Un usuario estandar solo visualiza los tenants que se le asignen.",
            "Los administradores tienen acceso a todos los tenants activos.",
            "Cambiar de tenant actualiza el contexto de Dashboard, Produccion, Reports, maestros y administracion.",
        ]),
        heading("2.2 Maestros", 2),
        paragraph("Los maestros son la base de la operacion. Antes de registrar produccion, cree y mantenga las lineas, celdas, modelos y estados necesarios para el tenant. En Produccion los selectores de linea, modelo y celda utilizan esos datos."),
        table(["Maestro", "Uso habitual"], [
            ["Lines", "Identifica la linea o area de produccion."],
            ["Cells", "Identifica la celda, estacion o puesto."],
            ["Models", "Identifica el producto, referencia o variante."],
            ["Status", "Catalogo de estados aplicables a la operacion."],
        ], "Maestros"),
        heading("2.3 Produccion y reports", 2),
        paragraph("Cada evento de trazabilidad se guarda en production_report. Los campos funcionales minimos son line_code, serial_number, result y production_datetime. El resultado debe estar normalizado a OK, NOK, SCRAP o REWORK."),
        bullets([
            "Produccion permite filtrar, consultar y crear registros desde el portal.",
            "Reports calcula volumen, rendimiento, defectos, ciclos y trazabilidad por numero de serie.",
            "El export CSV o Excel refleja el conjunto de datos filtrado en pantalla.",
        ]),
        heading("3. Seguridad, usuarios y permisos", 1, True),
        heading("3.1 Acceso al portal", 2),
        paragraph("El login crea una sesion HTTP protegida mediante cookie. Las operaciones que modifican datos requieren tambien la proteccion CSRF. En una base inicializada con datos seed existen los usuarios admin/admin123 y machine/machine123; cambie esas contrasenas antes de un uso real."),
        note("En produccion use HTTPS y COOKIE_SECURE=true. Nunca utilice las credenciales seed como credenciales definitivas.", "Seguridad"),
        heading("3.2 Roles y usuarios", 2),
        numbered([
            "Entre con una cuenta administradora y abra Administracion > Users.",
            "Cree el usuario y complete su identificador, nombre, correo, estado y contrasena inicial.",
            "Asigne uno o varios roles desde la ficha del usuario.",
            "Para un usuario no administrador, asigne los tenants permitidos. Para un administrador no es necesario limitar tenants.",
            "Compruebe el acceso iniciando sesion con el usuario creado y validando el selector de tenant.",
        ]),
        heading("3.3 Integraciones tecnicas", 2),
        paragraph("Administracion > Integraciones crea credenciales de maquina para PLC, SCADA, gateway y conectores. Cada cliente dispone de client_id y API key. La clave se muestra al crear o regenerar: guardela en el gestor de secretos del equipo, porque no debe exponerse en capturas ni documentacion."),
        table(["Control", "Finalidad"], [
            ["client_id + API key", "Autentica el origen tecnico en POST /production-reports/ingest."],
            ["Activo", "Revoca temporalmente el acceso sin borrar el cliente."],
            ["Ambito de planta/linea/estacion/maquina", "Limita los eventos que el cliente puede insertar."],
            ["source_system", "Permite identificar el origen logico del dato."],
        ], "CredencialesTecnicas"),
        heading("4. Requisitos previos", 1, True),
        table(["Escenario", "Requisitos"], [
            ["Desarrollo local", "Python 3.10+, Node.js 20+ y PostgreSQL accesible."],
            ["Docker", "Docker Desktop o Docker Engine con Compose."],
            ["Kubernetes", "kubectl configurado, Helm, acceso al registry e Ingress."],
            ["Conector Windows", "Paquete RupMesProductionConnector; no requiere Python en destino."],
            ["Conector Linux", "Paquete RupMesProductionConnector y systemd."],
        ], "Requisitos"),
        paragraph("PostgreSQL es el motor soportado para la base de datos RupMes. Las fuentes del conector pueden ser MySQL, PostgreSQL, Microsoft SQL Server, MQTT, OPC UA, TCP JSON, Modbus TCP/RTU o Siemens S7."),
        heading("5. Desarrollo local sin Docker", 1, True),
        paragraph("Use este modo para desarrollar o depurar codigo. El backend y el frontend se ejecutan por separado."),
        heading("5.1 Backend", 2),
        code("python -m venv .venv"),
        code(".venv\\Scripts\\activate"),
        code("pip install -e ."),
        paragraph("Defina DATABASE_URL en la sesion o en el entorno. Ejemplo:"),
        code("$env:DATABASE_URL='postgresql+psycopg2://rupmes_user:SU_PASSWORD@127.0.0.1:5432/mes_db'"),
        paragraph("Si la base esta vacia, aplique la estructura y los datos de inicio:"),
        code("alembic upgrade head"),
        code("python -m rupmes init-db"),
        code("uvicorn rupmes.views.api:app --host 0.0.0.0 --port 8011 --reload"),
        heading("5.2 Frontend", 2),
        code("cd frontend"),
        code("npm install"),
        code("Copy-Item .env.example .env"),
        code("npm run dev"),
        table(["Servicio", "Direccion local"], [
            ["Portal Vite", "http://localhost:5173"],
            ["API", "http://localhost:8011"],
            ["Swagger", "http://localhost:8011/docs"],
            ["Health", "http://localhost:8011/health"],
        ], "URLsDesarrollo"),
        note("Use el mismo host para portal y API siempre que sea posible. Mezclar localhost y 127.0.0.1 puede impedir que el navegador envie la cookie de sesion correctamente.", "Cookies"),
        heading("6. Docker y base de datos", 1, True),
        heading("6.1 Base de datos interna", 2),
        paragraph("Copie .env.example a .env. Para un laboratorio con PostgreSQL gestionado por Docker Compose, utilice una URL que apunte al servicio db:"),
        code("DATABASE_URL=postgresql+psycopg2://rupmes:rupmes@db:5432/mes_db"),
        code("RUN_DB_MIGRATIONS=true"),
        code("RUN_DB_SEED=true"),
        code("docker compose up --build"),
        paragraph("El portal queda disponible en http://localhost:8080, la API en http://localhost:8011 y pgAdmin en http://localhost:5050."),
        heading("6.2 Base de datos externa", 2),
        paragraph("Para una base externa, DATABASE_URL debe contener el host real de PostgreSQL. No es necesario levantar el servicio db local; arranque solo app y frontend."),
        code("docker compose up --build app frontend"),
        table(["Estado de la base externa", "RUN_DB_MIGRATIONS", "RUN_DB_SEED"], [
            ["Vacia", "true", "true"],
            ["Estructura creada, sin datos seed", "false", "true"],
            ["Estructura y datos preparados", "false", "false"],
            ["Gestionar nuevas migraciones desde el arranque", "true", "false"],
        ], "BaseExterna"),
        note("La cuenta de base de datos usada por migraciones necesita CREATE y USAGE sobre el esquema public, ademas de permisos sobre tablas y secuencias. Si aparece permission denied for schema public, conceda esos permisos o use una cuenta de despliegue con privilegios suficientes.", "PostgreSQL"),
        heading("7. Variables de configuracion", 1, True),
        table(["Variable", "Uso", "Ejemplo seguro"], [
            ["DATABASE_URL", "Conexion efectiva de la API a PostgreSQL.", "postgresql+psycopg2://user:password@db:5432/mes_db"],
            ["BACKEND_PORT", "Puerto HTTP de la API.", "8011"],
            ["FRONTEND_PORT", "Puerto expuesto para el portal Docker.", "8080"],
            ["VITE_API_URL", "URL publica que usa el navegador para llamar a la API.", "https://api-rupmes.example.local"],
            ["FRONTEND_ORIGINS", "Orígenes permitidos por CORS, separados por comas.", "https://rupmes.example.local"],
            ["RUN_DB_MIGRATIONS", "Ejecuta Alembic al arrancar el backend.", "false en produccion Kubernetes"],
            ["RUN_DB_SEED", "Crea datos base idempotentes.", "true solo en inicializacion"],
            ["COOKIE_SECURE", "Exige HTTPS para la cookie de sesion.", "true en produccion"],
            ["COOKIE_SAMESITE", "Politica de envio de cookie.", "lax"],
            ["MULTI_TENANT_ENABLED", "Activa el contexto multi-tenant.", "true"],
            ["DEFAULT_TENANT_ID", "Tenant usado si no se especifica otro.", "DEFAULT"],
            ["PRODUCTION_INGEST_API_KEY", "Clave global heredada de ingest. Prefiera clientes por integracion.", "secreto gestionado"],
        ], "Variables"),
        heading("7.1 CORS y URL publica", 2),
        paragraph("FRONTEND_ORIGINS define desde que URLs el navegador puede invocar la API. Debe contener exactamente la URL del portal. VITE_API_URL debe ser accesible desde el navegador del usuario, no desde el contenedor. Si el portal abre por HTTPS, configure tambien la API por HTTPS para evitar bloqueo de contenido mixto."),
        heading("8. Base de datos y migraciones", 1, True),
        heading("8.1 Inicializacion", 2),
        numbered([
            "Cree una base PostgreSQL vacia y un usuario dedicado para la aplicacion.",
            "Conceda acceso al esquema public y privilegios de creacion para la cuenta que aplicara las migraciones.",
            "Configure DATABASE_URL sin exponer la clave en repositorios.",
            "Ejecute alembic upgrade head.",
            "Ejecute python -m rupmes init-db una sola vez para crear el tenant DEFAULT y datos base.",
        ]),
        heading("8.2 Mantenimiento de esquema", 2),
        table(["Accion", "Comando", "Uso"], [
            ["Aplicar cambios", "alembic upgrade head", "Lleva la base a la revision mas reciente."],
            ["Marcar esquema existente", "alembic stamp head", "Solo si la estructura ya coincide y no hay historial Alembic."],
            ["Crear migracion", "alembic revision -m 'descripcion' --autogenerate", "Desarrollo de cambios de modelo."],
            ["Revertir ultima migracion", "alembic downgrade -1", "Solo con copia de seguridad y plan de reversión."],
        ], "Migraciones"),
        note("No use alembic stamp head como solucion para una base incompleta. Ese comando no crea tablas; solo registra una revision.", "Importante"),
        heading("9. Uso del portal", 1, True),
        heading("9.1 Dashboard", 2),
        paragraph("El Dashboard muestra el contexto del tenant seleccionado y los indicadores disponibles. Si un cambio de tenant no se refleja, compruebe que el selector, la sesion y la URL de la API apuntan al mismo entorno."),
        heading("9.2 Produccion", 2),
        numbered([
            "Seleccione el tenant correcto en el panel lateral.",
            "Use filtros de estado, linea, modelo, celda, usuario y fechas.",
            "Pulse Apply para consultar y Reload para refrescar el conjunto de datos.",
            "Seleccione un registro para editarlo o pulse New item para crear uno.",
            "Use Export CSV o Export Excel para descargar la vista filtrada.",
        ]),
        heading("9.3 Reports", 2),
        paragraph("Reports usa production_report del tenant activo para calcular volumen diario, produccion por linea, OK/NOK por turno, FTQ/FPY, defectos, trazabilidad y ciclo medio. Si los reports no muestran datos, valide primero que la produccion se insertó con tenant, fecha, linea y resultado correctos."),
        heading("9.4 Administracion", 2),
        bullets([
            "Users: alta, estado, roles y tenants permitidos de cada usuario.",
            "Roles: conjunto de permisos de aplicacion.",
            "Tenants: alta, activacion, tenant predeterminado y aislamiento de datos.",
            "Portal settings: titulo y configuracion visual por tenant, incluido logo si se ha configurado.",
            "Integraciones: clientes tecnicos y limites de contexto para ingest industrial.",
        ]),
        heading("10. API e integracion industrial", 1, True),
        heading("10.1 API de trazabilidad", 2),
        table(["Endpoint", "Autenticacion", "Finalidad"], [
            ["POST /auth/login", "Credenciales de usuario", "Inicia sesion del portal."],
            ["GET /health", "No", "Verificacion tecnica de disponibilidad."],
            ["POST /production-reports", "Sesion + CSRF", "Crea produccion desde portal o backoffice."],
            ["POST /production-reports/ingest", "X-Client-Id + X-API-Key", "Recibe eventos desde integracion industrial."],
            ["GET /production-reports/traceability/{serial}", "Sesion autorizada", "Consulta el historico de un numero de serie."],
            ["GET/POST/PATCH /production-ingest-clients", "Administrador", "Gestion de clientes tecnicos."],
        ], "API"),
        paragraph("La especificacion interactiva se publica en /docs. Use ese recurso para revisar el contrato exacto y probar en un entorno seguro."),
        heading("10.2 Conector RupMes Production Connector", 2),
        paragraph("El conector se instala cerca del origen OT. Lee datos de una base SQL, MQTT, OPC UA, TCP JSON, Modbus o Siemens S7, los transforma mediante mappings y llama a POST /production-reports/ingest. Puede procesar una configuracion o un directorio de configuraciones."),
        table(["Fuente", "Como detecta nuevos datos"], [
            ["SQL", "Consulta incremental desde date_field y, opcionalmente, id_field."],
            ["MQTT", "Suscripcion a un topic; el broker entrega los mensajes."],
            ["OPC UA", "Cambio de trigger_node o sondeo del valor configurado."],
            ["TCP JSON", "Conexion del conector a la maquina o escucha de un evento enviado por la maquina."],
            ["Modbus TCP/RTU", "Sondeo de registros, coils o entradas de PLC/equipo en modo lectura."],
            ["Siemens S7", "Lectura de variables de un bloque de datos (DB) mediante IP, rack y slot."],
        ], "FuentesConector"),
        heading("10.3 Checkpoint", 2),
        paragraph("El checkpoint guarda el ultimo timestamp transferido y, si existe, el ultimo id. En el ciclo siguiente se solicitan registros posteriores. Configure un checkpoint_file exclusivo por pipeline en almacenamiento persistente. El id_field evita duplicados u omisiones cuando varios eventos tienen la misma fecha."),
        paragraph("Para PLCs y sockets que no aportan una fecha de evento fiable, utilice checkpoint_mode=sequence con un id_field o contador de secuencia creciente. El conector guarda la fecha UTC de recepcion y solo transfiere secuencias nuevas."),
        heading("10.4 Configuracion SQL", 2),
        code('"connection_url": "mysql+pymysql://usuario:password@127.0.0.1:3306/base_origen"'),
        code('"table": "production_events"'),
        code('"date_field": "event_ts"'),
        code('"id_field": "id"'),
        paragraph("Para una consulta compleja use source.query con los parametros :since_ts, :last_id y :limit. Ordene siempre por fecha ascendente e id ascendente."),
        heading("10.5 TCP, Modbus y S7", 2),
        paragraph("Las plantillas production_connector/templates/tcp-client.json, tcp-listener.json, modbus-tcp.json, modbus-rtu.json y s7.json reducen la configuracion a los datos propios de cada maquina. Copie la plantilla adecuada a config.json y complete IP, puerto, DB o registros, mapeos y checkpoint."),
        bullets([
            "TCP JSON: use framing newline para un objeto JSON UTF-8 por linea, o length_prefix_be para una longitud de cuatro bytes seguida del JSON. En listener, la maquina abre una conexion y envia un evento.",
            "Modbus: defina modbus_registers con direccion, area (holding, input, coil o discrete) y tipo. Confirme siempre si la documentacion de la maquina usa offsets desde cero o notacion 40001.",
            "S7: cree un DB dedicado de solo lectura para secuencia, serie, resultado y flag de datos listos. No lea ni escriba variables de seguridad o control.",
        ]),
        heading("10.6 Secretos locales", 2),
        paragraph("Las plantillas usan ${ENV:RUPMES_CLIENT_ID} y ${ENV:RUPMES_API_KEY}. Copie secrets.env.template a secrets.env en la carpeta production_connector y guarde alli los valores emitidos en Administracion > Integraciones. El servicio lee ese fichero automaticamente; no lo incluya en Git ni en paquetes compartidos."),
        heading("10.5 Mapeo de campos", 2),
        table(["Campo RupMes", "Requerido", "Ejemplo de origen"], [
            ["line_code", "Si", "line_name"],
            ["serial_number", "Si", "serial_no"],
            ["result", "Si", "status_code convertido a OK/NOK/SCRAP/REWORK"],
            ["production_datetime", "Si", "event_ts"],
            ["station_code", "No", "station_name"],
            ["machine_code", "No", "machine_name"],
            ["cycle_time_seconds", "No", "cycle_seconds"],
            ["error_code / error_description", "No", "defect_code / defect_text"],
            ["source_system", "No", "Constante, por ejemplo MYSQL-BRIDGE"],
        ], "Mapeo"),
        heading("11. Instalacion del conector", 1, True),
        heading("11.1 Windows", 2),
        numbered([
            "En la maquina de desarrollo genere el paquete con production_connector\\windows\\build-package.ps1 -ProjectRoot 'C:\\ruta\\proyecto' -BuildBundle -ZipPackage.",
            "Copie la carpeta RupMesProductionConnector o su ZIP al equipo cliente. No copie el repositorio completo.",
            "Copie una plantilla desde production_connector\\templates a production_connector\\config.json y complete los datos del origen.",
            "Copie secrets.env.template a secrets.env y guarde el client_id y API key generados en el portal.",
            "Ejecute rupmes-connector.exe validate-config y despues run-once con dry_run=true.",
            "Abra PowerShell como administrador y ejecute production_connector\\windows\\install-service.ps1 con ProjectRoot y ConfigPath.",
            "Compruebe el servicio RupMesProductionConnectorService y el archivo de log creado por la instalacion.",
        ]),
        code('.\\production_connector\\windows\\uninstall-service.ps1 -ProjectRoot "C:\\RupMesProductionConnector"'),
        paragraph("El paquete de Windows incluye ejecutables empaquetados; el equipo cliente no necesita Python preinstalado. Para SQL Server se requiere el controlador ODBC de Microsoft correspondiente."),
        heading("11.2 Linux", 2),
        numbered([
            "Genere el paquete con BUILD_BUNDLE=1 ZIP_PACKAGE=1 ./production_connector/linux/build-package.sh /ruta/proyecto.",
            "Copie y extraiga RupMesProductionConnector en el servidor de la linea.",
            "Edite production_connector/config.json con valores reales.",
            "Ejecute ./production_connector/linux/install.sh /ruta/RupMesProductionConnector /ruta/RupMesProductionConnector/production_connector/config.json.",
            "Compruebe systemctl status rupmes-production-connector y los logs del servicio.",
        ]),
        code('./production_connector/linux/uninstall.sh /ruta/RupMesProductionConnector'),
        paragraph("Para Raspberry Pi, genere el paquete Linux desde una Raspberry o compilador ARM64. Un bundle Linux x86_64 no se ejecuta en ARM64."),
        heading("11.3 Prueba antes de servicio", 2),
        code('rupmes-connector validate-config --config production_connector/config.json'),
        code('rupmes-connector run-once --config production_connector/config.json'),
        paragraph("Empiece con dry_run=true si necesita revisar el mapeo sin insertar datos. Cuando la prueba sea correcta, active el servicio continuo y monitorice el checkpoint y los logs."),
        heading("12. Kubernetes y Helm", 1, True),
        heading("12.1 Modelo recomendado", 2),
        paragraph("En produccion, despliegue frontend y backend como workloads Kubernetes y utilice PostgreSQL externo gestionado. El Job de migracion Helm debe aplicar las migraciones de forma controlada. Mantenga RUN_DB_MIGRATIONS=false y RUN_DB_SEED=false en los pods de backend."),
        heading("12.2 Valores esenciales", 2),
        table(["Parametro Helm", "Valor esperado en produccion"], [
            ["images.backend / images.frontend", "Repositorio y etiqueta inmutables del registry."],
            ["frontend.runtimeConfig.apiUrl", "URL HTTPS publica de la API."],
            ["backend.env.frontendOrigins", "URL HTTPS publica del portal."],
            ["backend.env.cookieSecure", "true"],
            ["database.external.enabled", "true si PostgreSQL es externo."],
            ["database.external.url", "Cadena de conexion protegida."],
            ["migrationJob.enabled", "true para aplicar migraciones en el release."],
            ["migrationJob.seed", "true solo en primera inicializacion vacia."],
            ["ingress.frontendHost / backendHost", "DNS publicos del portal y API."],
        ], "Helm"),
        heading("12.3 Despliegue", 2),
        code('helm upgrade --install rupmes ./deploy/helm/rupmes -n rupmes --create-namespace -f values-k3s-prod.yaml'),
        paragraph("Para el entorno K3s del proyecto se dispone de scripts/deploy-k3s.ps1. El script construye las imagenes, las publica en Harbor, ejecuta Helm y espera el rollout de backend y frontend."),
        code('.\\scripts\\deploy-k3s.ps1 -Version 1.0.1 -KubeConfigPath "$env:USERPROFILE\\.kube\\rupmes-k3s.yaml"'),
        heading("12.4 Comprobacion", 2),
        code('kubectl get pods -n rupmes'),
        code('kubectl get ingress -n rupmes'),
        code('kubectl logs -n rupmes deployment/rupmes-rupmes-backend'),
        note("Si Helm no encuentra el cluster en una nueva consola, vuelva a definir KUBECONFIG con el archivo kubeconfig valido antes de ejecutar Helm o kubectl.", "Kubernetes"),
        heading("13. Publicar una nueva version", 1, True),
        numbered([
            "Aplique cambios y ejecute las pruebas relevantes: pytest para backend y npm build para frontend si corresponde.",
            "Elija una etiqueta nueva, por ejemplo 1.0.2. No reutilice una etiqueta ya desplegada.",
            "Ejecute scripts/deploy-k3s.ps1 -Version 1.0.2 con el kubeconfig correcto.",
            "Compruebe los rollouts, pods, logs y acceso a portal y API.",
            "Pruebe login, cambio de tenant, consulta de produccion y una integracion en entorno controlado.",
        ]),
        paragraph("Si solo cambia el frontend use -SkipBackend. Si solo cambia el backend use -SkipFrontend. Use -RenderOnly para validar el renderizado Helm sin aplicar cambios."),
        heading("14. Diagnostico y mantenimiento", 1, True),
        table(["Sintoma", "Causa probable", "Accion"], [
            ["NetworkError al iniciar sesion", "API no accesible, CORS incorrecto o contenido mixto HTTP/HTTPS.", "Revise VITE_API_URL, FRONTEND_ORIGINS, DNS, Ingress y que portal/API usen HTTPS."],
            ["401 Invalid credentials", "Usuario, clave o tenant no validos.", "Compruebe el usuario en la base activa y el tenant seleccionado. No es un error CORS."],
            ["401 despues de login", "Cookie no enviada entre hosts.", "No mezcle localhost y 127.0.0.1; revise SameSite, Secure y dominio."],
            ["permission denied for schema public", "La cuenta PostgreSQL no puede crear Alembic o tablas.", "Conceda USAGE/CREATE en public o use una cuenta de migracion."],
            ["Job Helm en CreateContainerConfigError", "Secret o valor DATABASE_URL no existe.", "Revise kubectl describe pod y los valores/secretos del chart."],
            ["Conector repite o pierde eventos", "Checkpoint compartido, fecha no ordenable o falta id_field.", "Use un checkpoint por pipeline y configure id_field/sequence."],
            ["Reports vacios", "No hay datos para el tenant o filtros activos.", "Valide tenant_id, fechas, result y line_code del evento."],
        ], "Diagnostico"),
        heading("14.1 Copias y observabilidad", 2),
        bullets([
            "Realice copias consistentes de PostgreSQL antes de migraciones o actualizaciones mayores.",
            "Conserve los logs de backend, Ingress y conectores durante un periodo definido por IT/OT.",
            "Monitorice /health, el estado de pods, la antiguedad de checkpoints y errores de entrega de cada conector.",
            "Proteja config.json, secrets Kubernetes y .env: contienen credenciales de bases y API keys.",
        ]),
        heading("15. Lista de salida a produccion", 1, True),
        bullets([
            "DNS del portal y API apuntan al Ingress correcto.",
            "Portal y API estan bajo HTTPS con certificados validos.",
            "COOKIE_SECURE=true y FRONTEND_ORIGINS coincide exactamente con el portal.",
            "La base PostgreSQL tiene copia de seguridad y migraciones aplicadas.",
            "Existe un tenant activo predeterminado y los usuarios tienen tenants asignados segun su rol.",
            "Se han cambiado las credenciales seed y se usan claves tecnicas distintas por integracion.",
            "Cada pipeline tiene config, checkpoint y client_id propios.",
            "Se ha probado un evento de extremo a extremo hasta Produccion y Reports.",
            "El procedimiento de rollback y responsables de soporte estan definidos.",
        ]),
        heading("Anexo A. Ejemplo de configuracion segura", 1, True),
        code('VITE_API_URL=https://api-rupmes.example.local'),
        code('FRONTEND_ORIGINS=https://rupmes.example.local'),
        code('COOKIE_SECURE=true'),
        code('COOKIE_SAMESITE=lax'),
        code('MULTI_TENANT_ENABLED=true'),
        code('DEFAULT_TENANT_ID=DEFAULT'),
        code('RUN_DB_MIGRATIONS=false'),
        code('RUN_DB_SEED=false'),
        paragraph("Guarde DATABASE_URL y claves de API en secretos del gestor de despliegue. No incluya valores reales en .env.example, values versionados o paquetes de conectores entregados a terceros."),
        heading("Anexo B. Referencias del proyecto", 1, True),
        bullets([
            "README.md: instalacion local y Docker.",
            "deploy/helm/rupmes/README.md: despliegue Helm.",
            "production_connector/README.md: arquitectura y configuracion del conector.",
            "production_connector/WINDOWS_DEPLOYMENT.md: empaquetado e instalacion Windows.",
            "production_connector/LINUX_DEPLOYMENT.md: empaquetado e instalacion Linux.",
            "production_connector/PROTOCOLS.md: configuracion de TCP, Modbus, S7 y seguridad de secretos.",
            "http://HOST_API/docs: contrato interactivo de la API desplegada.",
        ]),
    ]
    return ''.join(parts)


CONTENT = """<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<office:document-content xmlns:office=\"urn:oasis:names:tc:opendocument:xmlns:office:1.0\" xmlns:text=\"urn:oasis:names:tc:opendocument:xmlns:text:1.0\" xmlns:style=\"urn:oasis:names:tc:opendocument:xmlns:style:1.0\" xmlns:table=\"urn:oasis:names:tc:opendocument:xmlns:table:1.0\" xmlns:fo=\"urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0\" office:version=\"1.3\">
<office:automatic-styles>
  <style:style style:name=\"Table\" style:family=\"table\"><style:table-properties table:align=\"left\" style:width=\"17.0cm\"/></style:style>
  <style:style style:name=\"TableColumn\" style:family=\"table-column\"><style:table-column-properties style:column-width=\"4.25cm\"/></style:style>
  <style:style style:name=\"TableCell\" style:family=\"table-cell\"><style:table-cell-properties fo:border=\"0.02cm solid #C9D4DF\" fo:padding=\"0.12cm\"/></style:style>
  <style:style style:name=\"TableHeaderCell\" style:family=\"table-cell\"><style:table-cell-properties fo:background-color=\"#E8EEF5\" fo:border=\"0.02cm solid #A9BACB\" fo:padding=\"0.12cm\"/></style:style>
  <style:style style:name=\"H1\" style:family=\"paragraph\" style:parent-style-name=\"Heading_20_1\"/>
  <style:style style:name=\"H1Break\" style:family=\"paragraph\" style:parent-style-name=\"Heading_20_1\"><style:paragraph-properties fo:break-before=\"page\"/></style:style>
</office:automatic-styles>
<office:body><office:text>__BODY__</office:text></office:body></office:document-content>"""


STYLES = """<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<office:document-styles xmlns:office=\"urn:oasis:names:tc:opendocument:xmlns:office:1.0\" xmlns:style=\"urn:oasis:names:tc:opendocument:xmlns:style:1.0\" xmlns:text=\"urn:oasis:names:tc:opendocument:xmlns:text:1.0\" xmlns:fo=\"urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0\" office:version=\"1.3\">
<office:styles>
 <style:style style:name=\"Body\" style:family=\"paragraph\"><style:paragraph-properties fo:margin-bottom=\"0.16cm\" fo:line-height=\"125%\"/><style:text-properties fo:font-family=\"Liberation Sans\" fo:font-size=\"10.5pt\" fo:color=\"#172033\"/></style:style>
 <style:style style:name=\"Title\" style:family=\"paragraph\"><style:paragraph-properties fo:margin-top=\"5.0cm\" fo:margin-bottom=\"0.2cm\"/><style:text-properties fo:font-family=\"Liberation Sans\" fo:font-size=\"30pt\" fo:font-weight=\"bold\" fo:color=\"#0B5275\"/></style:style>
 <style:style style:name=\"Subtitle\" style:family=\"paragraph\"><style:paragraph-properties fo:margin-bottom=\"0.7cm\"/><style:text-properties fo:font-family=\"Liberation Sans\" fo:font-size=\"16pt\" fo:color=\"#4B6479\"/></style:style>
 <style:style style:name=\"Heading_20_1\" style:family=\"paragraph\"><style:paragraph-properties fo:margin-top=\"0.65cm\" fo:margin-bottom=\"0.30cm\"/><style:text-properties fo:font-family=\"Liberation Sans\" fo:font-size=\"16pt\" fo:font-weight=\"bold\" fo:color=\"#0B5275\"/></style:style>
 <style:style style:name=\"H2\" style:family=\"paragraph\"><style:paragraph-properties fo:margin-top=\"0.42cm\" fo:margin-bottom=\"0.20cm\"/><style:text-properties fo:font-family=\"Liberation Sans\" fo:font-size=\"13pt\" fo:font-weight=\"bold\" fo:color=\"#1E6B8C\"/></style:style>
 <style:style style:name=\"H3\" style:family=\"paragraph\"><style:paragraph-properties fo:margin-top=\"0.3cm\" fo:margin-bottom=\"0.14cm\"/><style:text-properties fo:font-family=\"Liberation Sans\" fo:font-size=\"11pt\" fo:font-weight=\"bold\" fo:color=\"#274C63\"/></style:style>
 <style:style style:name=\"Code\" style:family=\"paragraph\"><style:paragraph-properties fo:margin-top=\"0.08cm\" fo:margin-bottom=\"0.08cm\" fo:margin-left=\"0.28cm\" fo:background-color=\"#F2F5F7\" fo:padding=\"0.12cm\"/><style:text-properties fo:font-family=\"Liberation Mono\" fo:font-size=\"8.5pt\" fo:color=\"#1B3548\"/></style:style>
 <style:style style:name=\"Note\" style:family=\"paragraph\"><style:paragraph-properties fo:margin-top=\"0.2cm\" fo:margin-bottom=\"0.24cm\" fo:background-color=\"#EAF5F5\" fo:padding=\"0.16cm\" fo:border-left=\"0.10cm solid #249A9A\"/><style:text-properties fo:font-family=\"Liberation Sans\" fo:font-size=\"10pt\" fo:color=\"#173B45\"/></style:style>
 <style:style style:name=\"NoteLabel\" style:family=\"text\"><style:text-properties fo:font-weight=\"bold\" fo:color=\"#087A7A\"/></style:style>
 <style:style style:name=\"List\" style:family=\"paragraph\"><style:paragraph-properties fo:margin-bottom=\"0.10cm\" fo:line-height=\"120%\"/><style:text-properties fo:font-family=\"Liberation Sans\" fo:font-size=\"10.5pt\" fo:color=\"#172033\"/></style:style>
 <style:style style:name=\"TableHeader\" style:family=\"paragraph\"><style:paragraph-properties fo:margin-bottom=\"0cm\"/><style:text-properties fo:font-family=\"Liberation Sans\" fo:font-size=\"8.5pt\" fo:font-weight=\"bold\" fo:color=\"#123A57\"/></style:style>
 <style:style style:name=\"TableText\" style:family=\"paragraph\"><style:paragraph-properties fo:margin-bottom=\"0cm\"/><style:text-properties fo:font-family=\"Liberation Sans\" fo:font-size=\"8.5pt\" fo:color=\"#172033\"/></style:style>
</office:styles>
<office:automatic-styles>
 <text:list-style style:name=\"BulletList\"><text:list-level-style-bullet text:level=\"1\" text:bullet-char=\"•\"><style:list-level-properties text:space-before=\"0.6cm\" text:min-label-width=\"0.35cm\"/></text:list-level-style-bullet></text:list-style>
 <text:list-style style:name=\"NumberList\"><text:list-level-style-number text:level=\"1\" style:num-format=\"1\"><style:list-level-properties text:space-before=\"0.7cm\" text:min-label-width=\"0.45cm\"/></text:list-level-style-number></text:list-style>
 <style:page-layout style:name=\"PageLayout\"><style:page-layout-properties fo:page-width=\"21cm\" fo:page-height=\"29.7cm\" style:print-orientation=\"portrait\" fo:margin-top=\"2.2cm\" fo:margin-bottom=\"1.8cm\" fo:margin-left=\"2.0cm\" fo:margin-right=\"2.0cm\"/><style:header-style/><style:footer-style/></style:page-layout>
</office:automatic-styles>
<office:master-styles><style:master-page style:name=\"Standard\" style:page-layout-name=\"PageLayout\"><style:footer><text:p text:style-name=\"Body\">RupMes | Manual de operacion y configuracion</text:p></style:footer></style:master-page></office:master-styles>
</office:document-styles>"""


META = """<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<office:document-meta xmlns:office=\"urn:oasis:names:tc:opendocument:xmlns:office:1.0\" xmlns:meta=\"urn:oasis:names:tc:opendocument:xmlns:meta:1.0\" xmlns:dc=\"http://purl.org/dc/elements/1.1/\" office:version=\"1.3\"><office:meta><dc:title>RupMes - Manual de configuracion, operacion y despliegue</dc:title><dc:creator>RupMes</dc:creator><meta:generator>RupMes documentation builder</meta:generator></office:meta></office:document-meta>"""


SETTINGS = """<?xml version=\"1.0\" encoding=\"UTF-8\"?><office:document-settings xmlns:office=\"urn:oasis:names:tc:opendocument:xmlns:office:1.0\" office:version=\"1.3\"><office:settings/></office:document-settings>"""


MANIFEST = """<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<manifest:manifest xmlns:manifest=\"urn:oasis:names:tc:opendocument:xmlns:manifest:1.0\" manifest:version=\"1.3\">
<manifest:file-entry manifest:full-path=\"/\" manifest:media-type=\"application/vnd.oasis.opendocument.text\"/>
<manifest:file-entry manifest:full-path=\"content.xml\" manifest:media-type=\"text/xml\"/>
<manifest:file-entry manifest:full-path=\"styles.xml\" manifest:media-type=\"text/xml\"/>
<manifest:file-entry manifest:full-path=\"meta.xml\" manifest:media-type=\"text/xml\"/>
<manifest:file-entry manifest:full-path=\"settings.xml\" manifest:media-type=\"text/xml\"/>
</manifest:manifest>"""


def main() -> None:
    content = CONTENT.replace("__BODY__", build_content())
    with zipfile.ZipFile(OUT, "w") as archive:
        archive.writestr("mimetype", "application/vnd.oasis.opendocument.text", compress_type=zipfile.ZIP_STORED)
        archive.writestr("content.xml", content)
        archive.writestr("styles.xml", STYLES)
        archive.writestr("meta.xml", META)
        archive.writestr("settings.xml", SETTINGS)
        archive.writestr("META-INF/manifest.xml", MANIFEST)
    print(OUT)


if __name__ == "__main__":
    main()
