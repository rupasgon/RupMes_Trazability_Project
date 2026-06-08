# RupMes Production Gateway

Configurable Windows/Linux gateway that reads industrial source data and pushes normalized events to RupMes through `POST /production-reports/ingest`.

## Purpose

- Keep PLC/SCADA/source systems decoupled from the RupMes API.
- Support different source technologies with the same delivery model.
- Allow per-line or per-machine configuration.
- Preserve transfer progress using a timestamp checkpoint and optional sequence/id tie-breaker.

## Supported source types

- `sql`
- `mqtt`
- `opcua`

## Supported SQL engines

- MySQL via `mysql+pymysql://...`
- PostgreSQL via `postgresql+psycopg2://...`
- Microsoft SQL Server via `mssql+pyodbc://...`

## Features

- Windows and Linux compatible
- Multi-pipeline runner from a config directory
- Configurable source-to-payload mapping
- Required and optional field mapping
- Timestamp checkpointing with optional id/sequence tracking
- Continuous service mode or one-shot mode
- API delivery using `X-Client-Id` and `X-API-Key`

## Structure

- Example config: [config.example.json](C:\Users\qpk1kx\Documents\RupMes_Trazability_Project\production_connector\config.example.json)
- Windows scheduled task install: [windows/install-task.ps1](C:\Users\qpk1kx\Documents\RupMes_Trazability_Project\production_connector\windows\install-task.ps1)
- Windows service install: [windows/install-service.ps1](C:\Users\qpk1kx\Documents\RupMes_Trazability_Project\production_connector\windows\install-service.ps1)
- Windows scheduled task uninstall: [windows/uninstall-task.ps1](C:\Users\qpk1kx\Documents\RupMes_Trazability_Project\production_connector\windows\uninstall-task.ps1)
- Windows service uninstall: [windows/uninstall-service.ps1](C:\Users\qpk1kx\Documents\RupMes_Trazability_Project\production_connector\windows\uninstall-service.ps1)
- Linux install: [linux/install.sh](C:\Users\qpk1kx\Documents\RupMes_Trazability_Project\production_connector\linux\install.sh)
- Linux service unit: [linux/rupmes-production-connector.service](C:\Users\qpk1kx\Documents\RupMes_Trazability_Project\production_connector\linux\rupmes-production-connector.service)

## Install

### Windows

Recommended mode:

- Production: Windows service
- Lab or quick pilot: scheduled task
- Client runtime: bundled executable, without Python preinstalled

The legacy installer [windows/install.ps1](C:\Users\qpk1kx\Documents\RupMes_Trazability_Project\production_connector\windows\install.ps1) is still available and installs the scheduled task mode for backward compatibility.

#### Build the Windows bundle

Build this once on an engineering or packaging machine, then copy the generated `production_connector/dist/windows/` folder to the target Windows machine.

```powershell
cd C:\path\to\project
.\production_connector\windows\build-bundle.ps1 -ProjectRoot "C:\path\to\project"
```

This generates:

- `production_connector/dist/windows/cli/rupmes-connector.exe`
- `production_connector/dist/windows/service/rupmes-connector-service.exe`

#### Build the Windows client package

To prepare a client-ready package automatically:

```powershell
cd C:\path\to\project
.\production_connector\windows\build-package.ps1 -ProjectRoot "C:\path\to\project" -BuildBundle -ZipPackage
```

Optional:

- `-ConfigPath "C:\path\to\project\production_connector\config.json"` to include a real client config
- `-OutputRoot "C:\path\to\output"` to change the delivery folder

This creates:

- `production_connector/release/windows/RupMesProductionConnector/`
- optionally `production_connector/release/windows/RupMesProductionConnector.zip`

The package already includes:

- bundled executables
- install and uninstall scripts
- `state/` and `logs/` folders
- `config.json` if provided, otherwise `config.template.json`

#### Windows service

1. Build the Windows bundle on a packaging machine.
2. Copy the project plus `production_connector/dist/windows/` to the target machine.
3. Open PowerShell as administrator.
4. Run:

```powershell
cd C:\path\to\project
.\production_connector\windows\install-service.ps1 -ProjectRoot "C:\path\to\project" -ConfigPath "C:\path\to\project\production_connector\config.json"
```

The script:
- uses `production_connector/dist/windows/service/rupmes-connector-service.exe` when available
- installs a Windows service called `RupMesProductionConnectorService`
- writes service settings next to the service runtime
- starts the service automatically

If the bundle is not present, the script falls back to the Python-based mode for development use.

Optional parameters:

- `-BundleRoot "C:\path\to\project\production_connector\dist\windows\service"`
- `-ServiceName "RupMesProductionConnectorService"`
- `-DisplayName "RupMes Production Connector"`
- `-Description "RupMes production gateway service"`
- `-LogPath "C:\path\to\project\production_connector\logs\windows-service.log"`

Uninstall:

```powershell
cd C:\path\to\project
.\production_connector\windows\uninstall-service.ps1 -ProjectRoot "C:\path\to\project"
```

#### Windows scheduled task

Use this mode for lab, demo or very small installations.

```powershell
cd C:\path\to\project
.\production_connector\windows\install-task.ps1 -ProjectRoot "C:\path\to\project" -ConfigPath "C:\path\to\project\production_connector\config.json"
```

The script:
- uses `production_connector/dist/windows/cli/rupmes-connector.exe` when available
- creates a scheduled task called `RupMesProductionConnector`

If the bundle is not present, the script falls back to the Python-based mode for development use.

Optional parameters:

- `-BundleRoot "C:\path\to\project\production_connector\dist\windows\cli"`
- `-TaskName "RupMesProductionConnector"`

Backward-compatible alias:

```powershell
cd C:\path\to\project
.\production_connector\windows\install.ps1 -ProjectRoot "C:\path\to\project" -ConfigPath "C:\path\to\project\production_connector\config.json"
```

Uninstall:

```powershell
cd C:\path\to\project
.\production_connector\windows\uninstall-task.ps1 -TaskName "RupMesProductionConnector"
```

### Linux

```bash
cd /path/to/project
chmod +x production_connector/linux/install.sh
./production_connector/linux/install.sh /path/to/project /path/to/project/production_connector/config.json
```

The script:
- creates `production_connector/.venv`
- installs the connector extras
- installs a `systemd` unit

## Manual execution

Single pipeline:

```bash
python -m rupmes_connector validate-config --config production_connector/config.json
python -m rupmes_connector run-once --config production_connector/config.json
python -m rupmes_connector run --config production_connector/config.json
```

Multiple pipelines from one directory:

```bash
python -m rupmes_connector validate-config --config production_connector/configs
python -m rupmes_connector run-once --config production_connector/configs
python -m rupmes_connector run --config production_connector/configs
```

## Configuration model

Each JSON config defines:

- `name`
- `api`
- `source`
- `payload`
- `state`
- `runtime`

### Shared tracking rules

- `source.date_field` is mandatory
- `state.initial_value` is the starting point if no checkpoint exists
- `source.id_field` is strongly recommended when several records may share the same timestamp

### Mapping rules

Each payload field can come from:

- `source`
- `constant`
- `default`

Supported transforms:

- `none`
- `string`
- `int`
- `float`
- `bool`
- `datetime`
- `date`

## Connection string examples

MySQL:

```text
mysql+pymysql://user:pass@localhost:3306/mes_source
```

PostgreSQL:

```text
postgresql+psycopg2://user:pass@localhost:5432/mes_source
```

SQL Server:

```text
mssql+pyodbc://user:pass@server:1433/mes_source?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes
```

SQL Server notes:

- Windows: install `ODBC Driver 18 for SQL Server`
- Linux: install `msodbcsql18` and `unixodbc`

## SQL source example

```json
{
  "name": "line_a_mysql",
  "api": {
    "base_url": "http://localhost:8000",
    "endpoint": "/production-reports/ingest",
    "client_id": "LINE-A-SQL",
    "api_key": "super-secret-sql"
  },
  "source": {
    "type": "sql",
    "connection_url": "mysql+pymysql://user:pass@localhost:3306/mes_source",
    "schema": null,
    "table": "production_events",
    "query": null,
    "date_field": "event_ts",
    "id_field": "id",
    "batch_size": 500,
    "extra_filters": []
  },
  "payload": {
    "required_fields": ["line_code", "serial_number", "result", "production_datetime"],
    "drop_null_fields": true,
    "mappings": {
      "plant_code": { "constant": "PLANT-ES" },
      "line_code": { "source": "line_name", "transform": "string" },
      "serial_number": { "source": "serial_no", "transform": "string" },
      "result": {
        "source": "status_code",
        "transform": "string",
        "value_map": {
          "PASS": "OK",
          "FAIL": "NOK",
          "SCRAP": "SCRAP",
          "REWORK": "REWORK"
        }
      },
      "production_datetime": { "source": "event_ts", "transform": "datetime" }
    }
  },
  "state": {
    "checkpoint_file": "production_connector/state/line_a_sql.json",
    "initial_value": "2026-01-01T00:00:00"
  },
  "runtime": {
    "poll_interval_seconds": 30,
    "log_level": "INFO",
    "dry_run": false,
    "stop_on_error": false,
    "max_batches_per_cycle": 100
  }
}
```

## MQTT source example

```json
{
  "name": "line_a_mqtt",
  "api": {
    "base_url": "http://localhost:8000",
    "client_id": "LINE-A-MQTT",
    "api_key": "super-secret-mqtt"
  },
  "source": {
    "type": "mqtt",
    "broker_host": "mqtt-broker.local",
    "broker_port": 1883,
    "topic": "factory/line-a/production",
    "qos": 1,
    "date_field": "event_ts",
    "id_field": "sequence_id"
  },
  "payload": {
    "required_fields": ["line_code", "serial_number", "result", "production_datetime"],
    "mappings": {
      "plant_code": { "constant": "PLANT-ES" },
      "line_code": { "source": "line_code", "transform": "string" },
      "serial_number": { "source": "serial_number", "transform": "string" },
      "result": { "source": "result", "transform": "string" },
      "production_datetime": { "source": "event_ts", "transform": "datetime" }
    }
  },
  "state": {
    "checkpoint_file": "production_connector/state/line_a_mqtt.json",
    "initial_value": "2026-01-01T00:00:00"
  }
}
```

Expected MQTT message format:

```json
{
  "sequence_id": 101,
  "event_ts": "2026-06-01T10:15:00",
  "line_code": "LINE-A",
  "serial_number": "SN-000001",
  "result": "OK"
}
```

## OPC UA source example

```json
{
  "name": "line_a_opcua",
  "api": {
    "base_url": "http://localhost:8000",
    "client_id": "LINE-A-OPCUA",
    "api_key": "super-secret-opcua"
  },
  "source": {
    "type": "opcua",
    "endpoint_url": "opc.tcp://10.10.10.20:4840",
    "date_field": "event_ts",
    "id_field": "sequence_id",
    "trigger_node": "ns=2;s=LineA.DataReady",
    "trigger_value": true,
    "node_map": {
      "event_ts": "ns=2;s=LineA.EventTs",
      "sequence_id": "ns=2;s=LineA.SequenceId",
      "line_code": "ns=2;s=LineA.LineCode",
      "serial_number": "ns=2;s=LineA.SerialNumber",
      "result": "ns=2;s=LineA.Result",
      "cycle_time_seconds": "ns=2;s=LineA.CycleTime"
    }
  },
  "payload": {
    "required_fields": ["line_code", "serial_number", "result", "production_datetime"],
    "mappings": {
      "plant_code": { "constant": "PLANT-ES" },
      "line_code": { "source": "line_code", "transform": "string" },
      "serial_number": { "source": "serial_number", "transform": "string" },
      "result": { "source": "result", "transform": "string" },
      "production_datetime": { "source": "event_ts", "transform": "datetime" },
      "cycle_time_seconds": { "source": "cycle_time_seconds", "transform": "float" }
    }
  },
  "state": {
    "checkpoint_file": "production_connector/state/line_a_opcua.json",
    "initial_value": "2026-01-01T00:00:00"
  }
}
```

## SQL query mode

Instead of `source.table`, you can provide `source.query`.

Available parameters:

- `:since_ts`
- `:last_id`
- `:limit`

Example:

```sql
SELECT
  id,
  event_ts,
  line_code,
  serial_number,
  result
FROM production_events
WHERE event_ts > :since_ts
ORDER BY event_ts ASC, id ASC
LIMIT :limit
```

## Recommended deployment model

- One pipeline per line, machine, or source integration
- One config file per pipeline
- One shared process can load a whole config directory

Example:

```text
production_connector/configs/
  line_a_sql.json
  line_b_mqtt.json
  line_c_opcua.json
```

## Scaling model

The gateway is designed to scale by configuration, not by code changes.

If you need to add 10 more machines, lines, PLCs, or source systems, the normal workflow is:

1. Create 10 new pipeline config files
2. Assign one checkpoint file per pipeline
3. Assign one `client_id` and `api_key` per pipeline when possible
4. Start the gateway against the config directory

You should not need to modify Python code to add new equipment.

### What you add for each new equipment

Each equipment integration should define:

- `name`
- `source.type`
- source connection or endpoint
- `date_field`
- `id_field` or sequence field when available
- field mapping
- `checkpoint_file`
- target API credentials

Example layout for 10 equipments:

```text
production_connector/
  configs/
    line01_sql.json
    line02_sql.json
    line03_sql.json
    line04_mqtt.json
    line05_mqtt.json
    line06_opcua.json
    line07_opcua.json
    line08_opcua.json
    line09_sql.json
    line10_sql.json
  state/
    line01_sql.json
    line02_sql.json
    line03_sql.json
    line04_mqtt.json
    line05_mqtt.json
    line06_opcua.json
    line07_opcua.json
    line08_opcua.json
    line09_sql.json
    line10_sql.json
```

Run all of them with:

```bash
python -m rupmes_connector run --config production_connector/configs
```

### Recommended directory structure

For larger installations, group by source type or plant area:

```text
production_connector/
  configs/
    sql/
    mqtt/
    opcua/
  state/
    sql/
    mqtt/
    opcua/
  logs/
```

Example:

```text
production_connector/configs/sql/line01.json
production_connector/configs/sql/line02.json
production_connector/configs/mqtt/packaging01.json
production_connector/configs/opcua/testbench03.json
```

### When a single process is enough

A single multipipeline process is usually enough when:

- source polling intervals are moderate
- event volume is low or medium
- all pipelines run on the same server
- failure isolation between lines is not critical

### When to split into multiple services

Split the gateway into several services when:

- one source type needs different operational handling
- one line has much higher throughput than the others
- different plant areas are on different networks
- you need to restart one group without affecting the others
- one customer or plant requires strong isolation

Typical split:

- one service for SQL sources
- one service for MQTT sources
- one service for OPC UA sources

Or:

- one service per production area
- one service per critical line

### Example scalable deployment patterns

Pattern A: one process for everything

```bash
python -m rupmes_connector run --config production_connector/configs
```

Pattern B: one process per source family

```bash
python -m rupmes_connector run --config production_connector/configs/sql
python -m rupmes_connector run --config production_connector/configs/mqtt
python -m rupmes_connector run --config production_connector/configs/opcua
```

Pattern C: one service per critical line

```bash
python -m rupmes_connector run --config production_connector/configs/opcua/line_a.json
python -m rupmes_connector run --config production_connector/configs/opcua/line_b.json
```

### Operational rules for good scalability

- Keep one checkpoint file per pipeline
- Keep one logical equipment per config file
- Prefer one `client_id` per line or machine
- Use `id_field` or sequence counters whenever possible
- Keep mappings explicit instead of relying on source column names by coincidence
- Separate high-volume lines from low-volume lines when throughput grows
- Keep source-specific credentials out of the code and only in config

### Template cloning workflow

Recommended way to onboard a new equipment:

1. Copy a config template close to the target source type
2. Rename `name`
3. Update source connection settings
4. Update `date_field` and `id_field`
5. Update mapping section
6. Set a unique checkpoint file
7. Validate config
8. Run in `dry_run` or `run-once`
9. Move to continuous service mode

Validation example:

```bash
python -m rupmes_connector validate-config --config production_connector/configs/line11_sql.json
python -m rupmes_connector run-once --config production_connector/configs/line11_sql.json
```

## Operational recommendations

- Always use `id_field` or `sequence_id` when available
- Start with `run-once` and optionally `dry_run=true`
- Keep checkpoints on persistent local storage
- Do not call the RupMes API directly from SQL triggers
- For MQTT, include the event timestamp in every message
- For OPC UA, expose both event timestamp and sequence counter if possible
