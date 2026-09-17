# Protocol Configuration Guide

This guide configures one RupMes Production Connector pipeline per machine, line, gateway, or data source. The same connector executable supports SQL, MQTT, OPC UA, TCP, Modbus, and Siemens S7.

## 1. Operating model

```text
Machine / PLC / SCADA / source database
                |
                v
RupMes Production Connector on Windows, Linux, or Raspberry Pi
                |
                v
HTTPS + X-Client-Id + X-API-Key
                |
                v
RupMes API and PostgreSQL
```

The connector reads sources only. It must not control PLC outputs or operate directly as a PROFINET, EtherCAT, or fieldbus controller.

## 2. Before configuring a machine

1. In the RupMes portal, select the target tenant.
2. Create the required line, cell, model, and status masters.
3. Open `Administration > Integrations` and create one active technical client per machine or logical line.
4. Limit the client to its tenant, plant, line, station, machine, and source system when applicable.
5. Save the generated `client_id` and API key in the connector machine only.

Every production event requires `line_code`, `serial_number`, `result`, and `production_datetime`. The result must be `OK`, `NOK`, `SCRAP`, or `REWORK`.

## 3. Configuration files and secrets

The package uses this layout:

```text
production_connector/
  config.json             # One active pipeline or a directory of pipeline JSON files
  secrets.env             # Local credentials; never commit or distribute with a real key
  templates/              # Safe starting templates
  state/                  # One checkpoint per pipeline
  logs/
```

Copy the closest template to `config.json`, then copy `secrets.env.template` to `secrets.env`.

```text
RUPMES_CLIENT_ID=LINE-A-PLC
RUPMES_API_KEY=the-key-generated-in-the-portal
```

Values written as `${ENV:NAME}` in JSON are read from `secrets.env`. A system environment variable with the same name has precedence. Keep `secrets.env` restricted to the service account and out of backups shared outside OT.

## 4. Checkpoint rule

The checkpoint prevents duplicate transfers after restart.

- Use `checkpoint_mode: "datetime"` when the source contains a reliable event timestamp. Configure `date_field` and ideally `id_field`.
- Use `checkpoint_mode: "sequence"` for PLC registers, raw TCP messages, or devices that expose a monotonically increasing sequence/counter. `id_field` is mandatory.
- Use `timestamp_source: "received_at"` only when the source does not contain a timestamp. RupMes receives the connector UTC timestamp, while the sequence prevents duplicates.
- Allocate one `state.checkpoint_file` per machine. Never share it between pipelines.

For a PLC counter that can reset after a power cycle, use a PLC timestamp too, or define a reset procedure that archives/removes the checkpoint only after confirming no historical events will be resent.

## 5. TCP JSON

Templates:

- `templates/tcp-client.json`: the connector connects to a machine and optionally sends a request.
- `templates/tcp-listener.json`: a machine connects to the connector and sends an event.

Supported frames:

- `newline`: one UTF-8 JSON object per line. In listener mode, send one event per TCP connection.
- `length_prefix_be`: a 4-byte big-endian payload length followed by one UTF-8 JSON object.

Example machine message:

```json
{
  "sequence_id": 1042,
  "event_ts": "2026-09-17T10:20:12+00:00",
  "serial_number": "SN-0001042",
  "result": "OK"
}
```

For listener mode allow the connector machine port in the OT firewall. TCP listener TLS is intentionally not supported by the connector; use a dedicated industrial gateway or reverse proxy that terminates TLS when it is required.

## 6. Modbus TCP and RTU

Templates:

- `templates/modbus-tcp.json`
- `templates/modbus-rtu.json`

`modbus_registers` maps a logical field name to a PLC or device address.

```json
"sequence_id": { "address": 0, "area": "holding", "data_type": "uint32" },
"serial_number": { "address": 10, "area": "holding", "data_type": "string", "count": 10 },
"data_ready": { "address": 0, "area": "coil", "data_type": "bool" }
```

Supported areas are `holding`, `input`, `coil`, and `discrete`. Supported types are `bool`, `uint16`, `int16`, `uint32`, `int32`, `float32`, and `string`.

Important:

- Confirm whether the machine documentation uses zero-based addresses or reference notation such as `40001`. The connector expects the protocol offset, normally zero-based.
- Use `word_order: "little"` only when the device stores 32-bit values with reversed 16-bit words.
- Use `modbus_trigger_field` and `modbus_trigger_value` when the PLC exposes a data-ready bit.
- The connector reads Modbus values only. It does not reset the PLC trigger bit; make the PLC increment `sequence_id` for each new event.
- For RTU on Raspberry, use a supported USB-RS485 adapter and set `modbus_serial_port`, usually `/dev/ttyUSB0` or `/dev/ttyAMA0`.

## 7. Siemens S7

Template: `templates/s7.json`.

`s7_variables` reads data blocks (DB) in read-only mode:

```json
"sequence_id": { "db_number": 10, "start": 0, "data_type": "uint32" },
"serial_number": { "db_number": 10, "start": 4, "data_type": "string", "length": 20 },
"data_ready": { "db_number": 10, "start": 26, "data_type": "bool", "bit": 0 }
```

Supported types are `bool`, `byte`, `uint16`, `int16`, `uint32`, `int32`, `float32`, and fixed-length `string`.

Before installing, coordinate with the automation owner:

1. Confirm the PLC IP address, rack, and slot.
2. Create a dedicated DB exposing only the traceability data needed by RupMes.
3. Enable the minimum external read access required by the PLC model and project security policy.
4. Do not use a DB that contains safety, control, or write-command values.
5. Use a sequence counter and optionally a `data_ready` trigger.

For S7-1200/1500, OPC UA is preferable when it is licensed and exposed. S7 is useful for existing installations where OPC UA is unavailable.

## 8. Dynamic routing results

Routings are configured in the portal under **Masters > Routings**. The hierarchy is `Line -> Routing -> ordered Cells/Processes -> Models`:

1. A routing belongs to one existing `Line`; a line can contain several routings.
2. One or more existing `Models` masters are assigned to each routing.
3. Ordered processes, each linked to an existing `Cell`, define the physical flow such as `TORQUE`, `LEAK_TEST`, or `VISION`.
4. A result schema per process. Each field has a code, label, type, required flag, and optional allowed values for lists.

The source equipment must publish a process event to `POST /routing-process-results/ingest`. The integration credentials are the same `X-Client-Id` and `X-API-Key` used for production ingest. The model, process, and dynamic fields are validated against the active routing for that integration tenant.

Use `templates/routing-process-result.json` as the connector starting point. It demonstrates the `nested_mappings` section, which creates the dynamic `result_values` object:

```json
{
  "model_id": "MODEL-100",
  "serial_number": "SN-000123",
  "process_id": "TORQUE",
  "result": "OK",
  "process_datetime": "2026-09-17T10:30:00",
  "result_values": {
    "torque_nm": 12.6,
    "program": "P1"
  }
}
```

Required top-level fields are `model_id`, `serial_number`, `process_id`, `result`, and `process_datetime`. Valid results are `OK`, `NOK`, and `SKIPPED`. A skipped process does not require its process fields. When the integration has plant, line, station, machine, or source-system restrictions, include matching values in the payload mappings.

For SQL sources with `checkpoint_mode: "sequence"`, set `id_field` to an increasing source event ID and set `state.initial_value` to the initial ID, normally `0`. The connector then transfers only rows whose ID is greater than its saved checkpoint.

## 9. Validation and installation

Start with `dry_run: true`. The connector validates and saves checkpoints but does not call the RupMes API.

Windows package:

```powershell
Copy-Item .\production_connector\templates\modbus-tcp.json .\production_connector\config.json
Copy-Item .\production_connector\secrets.env.template .\production_connector\secrets.env
.\production_connector\dist\windows\cli\rupmes-connector\rupmes-connector.exe validate-config --config .\production_connector\config.json
.\production_connector\dist\windows\cli\rupmes-connector\rupmes-connector.exe run-once --config .\production_connector\config.json
```

Linux package:

```bash
cp production_connector/templates/modbus-tcp.json production_connector/config.json
cp production_connector/secrets.env.template production_connector/secrets.env
./production_connector/dist/linux/cli/rupmes-connector/rupmes-connector validate-config --config production_connector/config.json
./production_connector/dist/linux/cli/rupmes-connector/rupmes-connector run-once --config production_connector/config.json
```

When the mapping and source connection are correct, set `dry_run` to `false`, run `run-once` again, verify the record in RupMes Production, then install the Windows service or Linux systemd service.

## 10. Raspberry Pi

Use Raspberry Pi OS 64-bit or another supported ARM64 Linux distribution. Build the Linux bundle on ARM64 hardware, preferably the target Raspberry or an ARM64 build runner:

```bash
BUILD_BUNDLE=1 ZIP_PACKAGE=1 ./production_connector/linux/build-package.sh /path/to/RupMes_Trazability_Project
```

Copy only `RupMesProductionConnector.tar.gz` to the Raspberry. A package built on x86_64 Linux cannot run on ARM64. The target machine does not need Python after the ARM64 bundle is built.

## 11. Protocol selection

Use the highest-level read-only interface exposed by the equipment:

1. OPC UA when available.
2. MQTT when a gateway already publishes events.
3. SQL when the machine/SCADA maintains a reliable event table.
4. TCP JSON for machines with a documented socket protocol.
5. Modbus or S7 when the PLC exposes only registers or DB data.

Do not connect this connector directly to PROFINET, EtherCAT, PROFIBUS, or other real-time control buses. Use OPC UA, S7, Modbus, or a SCADA/gateway layer to keep MES traffic isolated from machine control.
