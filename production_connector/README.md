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
- Windows install: [windows/install.ps1](C:\Users\qpk1kx\Documents\RupMes_Trazability_Project\production_connector\windows\install.ps1)
- Linux install: [linux/install.sh](C:\Users\qpk1kx\Documents\RupMes_Trazability_Project\production_connector\linux\install.sh)
- Linux service unit: [linux/rupmes-production-connector.service](C:\Users\qpk1kx\Documents\RupMes_Trazability_Project\production_connector\linux\rupmes-production-connector.service)

## Install

### Windows

1. Install Python 3.10 or newer.
2. Open PowerShell as administrator.
3. Run:

```powershell
cd C:\path\to\project
.\production_connector\windows\install.ps1 -ProjectRoot "C:\path\to\project" -ConfigPath "C:\path\to\project\production_connector\config.json"
```

The script:
- creates `production_connector\.venv`
- installs the connector extras
- creates a scheduled task called `RupMesProductionConnector`

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

## Operational recommendations

- Always use `id_field` or `sequence_id` when available
- Start with `run-once` and optionally `dry_run=true`
- Keep checkpoints on persistent local storage
- Do not call the RupMes API directly from SQL triggers
- For MQTT, include the event timestamp in every message
- For OPC UA, expose both event timestamp and sequence counter if possible
