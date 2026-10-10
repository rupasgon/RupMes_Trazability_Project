# Integración WIP a Oracle APEX

Esta tubería lee producción correcta de `bmw_szl_levers_results_assy`, agrupa las piezas por `MPN` y envía un lote por modelo al endpoint Oracle APEX utilizado por `TcpToApexBridge`.

## Garantías

- Solo procesa `ProductionMode = Produccion`, `Status = OK`, `MPN` informado y `ST34_P100DM` informado.
- `ST34_P100DM` es la clave única de pieza: una pieza solo puede estar en un lote local.
- Antes de hacer una llamada HTTP, el lote y sus piezas se guardan en una base SQLite local.
- El lote usa la máscara configurable `{prefix}-{service}-{date:%Y%m%d}-{sequence:06d}`.
- APEX confirma el envío con un `id` positivo. La respuesta conocida de restricción única `WO_PACK_FILE_LINE_CON` se trata como una confirmación idempotente.
- Si el contador `Id` de origen se reinicia, se detecta cuando el máximo actual es inferior al cursor local. El conector repasa la ventana configurada (`reconciliation_hours`) y elimina duplicados mediante `ST34_P100DM`.

## Configuración

Copiar [wip-oracle-apex.json](../production_connector/templates/wip-oracle-apex.json) a un directorio de configuraciones del conector. Ajustar los campos no secretos:

- `wip_oracle.service_id`: identificador exclusivo de la instancia, por ejemplo `WIPBPCS`.
- `wip_oracle.lot_prefix` y `lot_mask`.
- `wip_oracle.external_type` y `organization_id` según Oracle.
- `wip_oracle.state_db_path`: ruta persistente y exclusiva por servicio.
- `runtime.dry_run`: mantener `true` en la primera validación; cambiar a `false` solo tras revisar la cola creada.

El archivo `secrets.env`, con permisos de lectura exclusivos para la cuenta del servicio, debe contener:

```text
RUPMES_SOURCE_DATABASE_URL=mysql+pymysql://usuario:contraseña@servidor:3306/base
ORACLE_APEX_BASE_URL=https://servidor/ords/apps
ORACLE_APEX_TOKEN_URL=https://servidor/oauth/token
ORACLE_APEX_CLIENT_ID=...
ORACLE_APEX_CLIENT_SECRET=...
ORACLE_ORGANIZATION_ID=...
```

No guardar esas credenciales en Git ni en un archivo de configuración distribuido.

## Validación e instalación en Rocky 9

```bash
rupmes-connector validate-config --config /opt/rupmes-production-connector/production_connector/configs/bmw-wip-oracle.json
rupmes-connector run-once --config /opt/rupmes-production-connector/production_connector/configs/bmw-wip-oracle.json
```

La primera ejecución debe hacerse con `dry_run: true`. Cuando se valide el número de lotes y las cantidades, cambiar a `false` e instalar o reiniciar el servicio `rupmes-production-connector`.

## Control operativo

La base `state_db_path` contiene:

- `oracle_lots`: payload, estado, intentos, respuesta y error.
- `oracle_lot_pieces`: vínculo entre cada `ST34_P100DM` y su lote.
- `wip_state`: cursor normal y cursor de recuperación tras reinicio de `Id`.

Los lotes `PENDING` se reintentan automáticamente en el siguiente ciclo. Los `CONFIRMED` no se reenvían.
