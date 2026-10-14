# Dynamic Routing and Traceability Guide

This guide configures routing execution traceability from an industrial station to RupMes. It applies when different stations produce different measurement sets for the same product flow.

## 1. Operating model

```text
Model -> Routing -> ordered process/cell -> result schema
                                      |
Machine / PLC / SCADA -> Production Connector -> RupMes API
                                      |
                              routing_process_results
                                      |
                         traceability_measurements
```

RupMes stores the complete station payload as JSON and, in the same database transaction, extracts fields marked as reportable into normalized measurements. This keeps the original evidence while making numeric and categorical values available for reports and dashboards.

## 2. Configure the portal first

Perform the following steps in the target tenant. A tenant isolates its masters, routings, events, measurements, production view, and reports from other tenants.

1. Create the `Line`, `Cell`, and `Model` masters under **Masters**.
2. Open **Masters > Routings** and create a routing for an existing line.
3. Assign one or more existing models to that routing.
4. Create ordered processes. Each process has an identifier such as `TORQUE`, a cell, and a sequence number.
5. Define the result schema for every process.
6. In **Administration > Integrations**, create one active client for the equipment or gateway. Restrict it to the correct tenant, plant, line, station, machine, and source system when those values are known.
7. Save the `client_id` and generated API key only on the connector computer.

Example flow:

```text
Line: ASSEMBLY-01
Routing: MODEL-A-ROUTING
Models: MODEL-A, MODEL-A-SPORT

10  Cell: TORQUE-01  Process: TORQUE
20  Cell: LEAK-01    Process: LEAK_TEST
30  Cell: VISION-01  Process: VISION
```

## 3. Result schema

Each process declares its own fields. The field `code` is the integration contract: connector `result_values` must use the exact same code.

Example for the `TORQUE` process:

| Code | Type | Required | Reportable | Unit |
| --- | --- | --- | --- | --- |
| `torque_nm` | `number` | Yes | Yes | `Nm` |
| `angle_deg` | `number` | Yes | Yes | `deg` |
| `program` | `text` | Yes | Yes | |
| `tool_serial` | `text` | No | No | |

Supported field types are `text`, `number`, `integer`, `boolean`, `select`, `date`, and `datetime`.

- A required field must be present unless the process result is `SKIPPED`.
- A `select` field can restrict accepted values with `allowed_values`.
- A reportable field is copied to `traceability_measurements`; non-reportable fields remain available in the event JSON only.
- Units are metadata for reports and dashboards. Use consistent codes and units across compatible processes.

## 4. API contract

The connector posts one station result to:

```text
POST /routing-process-results/ingest
X-Client-Id: <technical-client-id>
X-API-Key: <technical-client-api-key>
Content-Type: application/json
```

Required top-level fields:

- `model_id`
- `serial_number`
- `process_id`
- `result`: `OK`, `NOK`, or `SKIPPED`
- `process_datetime`

Example payload:

```json
{
  "model_id": "MODEL-A",
  "serial_number": "SN-20260918-000123",
  "process_id": "TORQUE",
  "result": "OK",
  "process_datetime": "2026-09-18T10:30:00+02:00",
  "plant_code": "PLANT-ES",
  "line_code": "ASSEMBLY-01",
  "station_code": "TORQUE-01",
  "machine_code": "ATLAS-01",
  "source_system": "TORQUE-PLC",
  "result_values": {
    "torque_nm": 12.6,
    "angle_deg": 91.2,
    "program": "P1",
    "tool_serial": "TOOL-8472"
  }
}
```

The API validates that the model is assigned to a routing in the integration tenant, that the process belongs to that routing, that the cell flow is valid, and that the dynamic values conform to the process schema. It also validates any technical-client scope configured in Administration.

## 5. Connector mappings

A mapping converts a source-system field into an API field. `source` reads a column/tag/key, `constant` supplies fixed context, `transform` converts its type, and `value_map` normalizes source statuses.

`nested_mappings.result_values` maps the variable measurements for one process. Its names must match the process result-schema codes.

Example MySQL pipeline for a torque station:

```json
{
  "name": "torque_station",
  "api": {
    "base_url": "https://api-rupmes.example.local",
    "endpoint": "/routing-process-results/ingest",
    "client_id": "${ENV:RUPMES_CLIENT_ID}",
    "api_key": "${ENV:RUPMES_API_KEY}",
    "timeout_seconds": 30,
    "verify_tls": true
  },
  "source": {
    "type": "sql",
    "connection_url": "${ENV:RUPMES_SOURCE_DATABASE_URL}",
    "table": "torque_results",
    "date_field": "event_ts",
    "id_field": "id",
    "checkpoint_mode": "sequence",
    "timestamp_source": "source",
    "batch_size": 200,
    "extra_filters": []
  },
  "payload": {
    "required_fields": ["model_id", "serial_number", "process_id", "result", "process_datetime"],
    "drop_null_fields": true,
    "mappings": {
      "model_id": { "source": "model_code", "transform": "string" },
      "serial_number": { "source": "barcode", "transform": "string" },
      "process_id": { "constant": "TORQUE", "transform": "string" },
      "result": {
        "source": "status",
        "transform": "string",
        "value_map": { "PASS": "OK", "FAIL": "NOK", "BYPASS": "SKIPPED" }
      },
      "process_datetime": { "source": "event_ts", "transform": "datetime" },
      "plant_code": { "constant": "PLANT-ES" },
      "line_code": { "constant": "ASSEMBLY-01" },
      "station_code": { "constant": "TORQUE-01" },
      "machine_code": { "constant": "ATLAS-01" },
      "source_system": { "constant": "TORQUE-PLC" }
    },
    "nested_mappings": {
      "result_values": {
        "torque_nm": { "source": "actual_torque", "transform": "float" },
        "angle_deg": { "source": "actual_angle", "transform": "float" },
        "program": { "source": "program_name", "transform": "string" },
        "tool_serial": { "source": "tool_id", "transform": "string" }
      }
    }
  },
  "state": {
    "checkpoint_file": "production_connector/state/torque_station.json",
    "initial_value": "0"
  },
  "runtime": {
    "poll_interval_seconds": 10,
    "log_level": "INFO",
    "dry_run": true,
    "stop_on_error": false,
    "max_batches_per_cycle": 100
  }
}
```

Save credentials separately in `secrets.env`:

```text
RUPMES_CLIENT_ID=TORQUE-STATION-01
RUPMES_API_KEY=generated-key-from-administration
RUPMES_SOURCE_DATABASE_URL=mysql+pymysql://rupmes_reader:replace-password@127.0.0.1:3306/machine_source
```

Do not place real credentials in JSON, Git, screenshots, or shared installation packages.

## 6. Checkpoint and duplicate control

Use one configuration and one checkpoint file per machine/process source. For SQL, prefer an increasing `id_field` plus a reliable `date_field`; `checkpoint_mode: "sequence"` avoids ambiguity when multiple records have the same timestamp.

The connector only reads the source database. It never writes to the source table and it does not write directly to RupMes PostgreSQL.

## 7. Storage model

For the example event, RupMes writes both records atomically:

| Table | Purpose | Example content |
| --- | --- | --- |
| `routing_process_results` | Complete traceability event | serial, model, routing, process, result, timestamp, raw `result_values` JSON |
| `traceability_measurements` | One row per reportable dynamic field | `torque_nm=12.6 Nm`, `angle_deg=91.2 deg`, `program=P1` |

If validation or storage of any reportable measurement fails, the entire event is rejected. There is no partial event.

The raw JSON preserves full station evidence. The normalized measurements support filtering, trends, limits, distributions, First Time Quality, and dashboard KPIs without creating a custom database table for every station.

## 8. Verification procedure

1. Run `validate-config` against the connector JSON.
2. Run `run-once` with `dry_run: true` and confirm source connectivity and mappings in logs.
3. Set `dry_run` to `false`.
4. Run `run-once` again.
5. Verify the event in the routing traceability view and the corresponding reportable values in reports/dashboard data.
6. Install the continuous Windows service or Linux systemd service only after the controlled test succeeds.

See `production_connector/README.md` for connector installation and `production_connector/PROTOCOLS.md` for TCP, Modbus, S7, MQTT, and OPC UA source configuration.
