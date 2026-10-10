# RupMES Edge Dashboard Architecture

## Scope and decision

RupMES currently provides a central MES portal built with FastAPI, SQLAlchemy,
Alembic, PostgreSQL, and a React/Vite frontend. It also includes a reusable
`rupmes_connector` package with source adapters, including an `asyncua` OPC UA
adapter. The current OPC UA adapter is a batch reader for production ingest; it
connects, reads configured nodes, and sends rows to a remote API. It does not
provide subscriptions, long-lived sessions, PLC security configuration,
reconnection, or local dashboard storage.

The industrial dashboard must therefore be delivered as a sibling local runtime
called `rupmes_edge`. Raspberry Pi OS 64-bit on Raspberry Pi 5 is the primary
development and deployment platform, with one device per production line.
Windows 10/11 64-bit is also a supported local deployment target. The runtime
is deliberately independent of the central RupMES deployment. It must
not require PostgreSQL, Docker, Kubernetes, a cloud service, or access to the
central RupMES API during normal operation.

This keeps PLC traffic and live machine state within the OT network while
preserving the existing central application and its database schema.

## Existing components to reuse

| Existing component | Reuse approach |
| --- | --- |
| Python 3.10+, FastAPI, Pydantic | Local REST and streaming API with the same validation conventions. |
| SQLAlchemy and Alembic | SQLite models and migrations in an edge-specific migration directory. |
| React/Vite and the portal styling/i18n patterns | Dedicated edge dashboard and setup routes, optimized for kiosk displays. |
| `rupmes_connector` adapter concepts | A protocol-neutral acquisition interface. Do not reuse its polling loop for live state. |
| `asyncua` optional dependency | Long-lived, read-only OPC UA session with subscriptions. |
| Existing production and line vocabulary | Line, station, cycle, target, shift, alarm, and production-report naming. |

## Runtime topology

```text
PLC / OPC UA gateway
        |
        | OPC UA subscriptions (read-only)
        v
rupmes_edge collector ----> state evaluator ----> SQLite event/history store
        |                         |                       |
        +-------------------------+-----------------------+
                                  |
                                  v
                       FastAPI local API + WebSocket/SSE
                                  |
                                  v
                  React dashboard / local administration UI
                                  |
                                  v
                      Chromium kiosk on the same Raspberry Pi
```

The browser never connects to a PLC. The collector is the only OPC UA client.
The dashboard receives normalized state and aggregate data only from the local
FastAPI process.

## Proposed package layout

```text
src/rupmes_edge/
  api/                 # local FastAPI routes and local-admin auth
  collectors/          # connector protocol and OPC UA subscriber
  domain/              # station state, cycle, shift, KPI calculations
  persistence/         # SQLite models, repositories, retention jobs
  services/            # orchestration, health, import/export, diagnostics
  config/              # validated non-secret configuration models
  simulator/           # development-only OPC UA simulator
frontend/src/edge/     # kiosk dashboard and local setup UI
alembic_edge/          # SQLite-only migration chain
edge/                  # Raspberry Pi service, kiosk, install assets
```

`rupmes_edge` must not import central request handlers or central database
models. Shared pure utilities may be extracted later only when they have no
central database or tenant dependency.

## Connector contract

The edge collector layer exposes a protocol-neutral interface:

```python
class IndustrialConnector(Protocol):
    async def connect(self) -> None: ...
    async def start(self, on_update: Callable[[SignalUpdate], Awaitable[None]]) -> None: ...
    async def browse(self) -> list[BrowseNode]: ...
    async def disconnect(self) -> None: ...
    def health(self) -> ConnectorHealth: ...
```

`OpcUaConnector` is the first implementation. It creates one long-lived
`asyncua.Client` per endpoint, subscribes only to configured nodes, detects
stale data, and reconnects with bounded exponential backoff. It supports:

- endpoint URL, subscription interval, and timeout;
- anonymous or username/password authentication;
- client certificate and private-key configuration;
- server certificate trust/rejection handling;
- configured security policy and `Sign` / `SignAndEncrypt` modes;
- browse-only node discovery for an authenticated local administrator; and
- read-only node access. No write or method-call API is exposed.

The existing `rupmes_connector.adapters.opcua.OpcUaSourceAdapter` remains
unchanged for batch production-ingest pipelines. It must not be used for the
edge dashboard because repeatedly connecting and polling would create needless
PLC load and cannot provide correct live state transitions.

## Local data model

SQLite is the default storage engine. The initial migration introduces these
edge-owned tables:

| Table | Purpose |
| --- | --- |
| `edge_settings` | UI, retention, timezone, authentication, and dashboard preferences. |
| `edge_lines` | One local production line and its identity. |
| `edge_opcua_endpoints` | Endpoint configuration and non-secret security references. |
| `edge_stations` | Station identity, display order, targets, state rules, and enabled metrics. |
| `edge_signal_mappings` | Logical metric to NodeId, data type, conversion, and quality rules. |
| `edge_shifts` | Shift schedules, including cross-midnight schedules. |
| `edge_station_snapshots` | Last accepted value and timestamp per mapped signal. |
| `edge_cycle_events` | Completed cycle records and calculated/PLC supplied duration. |
| `edge_station_state_events` | State transitions and downtime intervals. |
| `edge_hourly_production` | Hourly and shift aggregates for fast dashboard queries. |
| `edge_connector_events` | Connect, reconnect, certificate, subscription, and health events. |
| `edge_alarms` | Active and historical normalized alarms. |
| `edge_audit_events` | Local configuration changes without recording credentials. |

Credentials, private-key passwords, and API secrets are not stored in exported
configuration or returned by API endpoints. They are stored in a local
root-readable secrets file, referenced by name from SQLite configuration.

## State and KPI semantics

Each station owns a state rule set with explicit priority and timeout values.
The default priority is `DISCONNECTED`, `FAULT`, `MANUAL`, `STOPPED`,
`RUNNING`, `IDLE`, then `UNKNOWN`. A value becomes disconnected when an endpoint
is offline, a subscription fails, or all required state signals are stale.

Cycle time is recorded as either:

1. a PLC-provided value, converted to seconds using the configured unit; or
2. elapsed time between configured `CycleActive` and `CycleComplete` events.

The implementation records which method produced each cycle. It never equates
the gap between parts with the machine processing cycle unless the station
configuration explicitly chooses that interpretation.

Counters are deduplicated with the source timestamp plus a monotonically
increasing counter/event identity when available. Counter resets and rollovers
are stored as events and start a new logical counter segment. This preserves
correct hourly statistics after reconnects and Pi restarts.

## Local API and UI

The local API exposes read-only dashboard endpoints plus authenticated local
administration endpoints. A WebSocket or Server-Sent Events endpoint pushes
normalized line and station snapshots to the kiosk UI; chart history remains
ordinary REST queries from SQLite.

The initial UI routes are:

- `/edge` - fullscreen line overview and station cards;
- `/edge/stations/:stationId` - station trends and downtime history;
- `/edge/admin` - local configuration, node browse, endpoint test, and import/export;
- `/edge/diagnostics` - connector health, last update, and recent errors.

The line overview shows only fresh values. A stale or failed station is rendered
as `DISCONNECTED`, never with its previous operating state. The desktop portal
is not altered in the first edge release.

## Raspberry Pi deployment

The primary deployment target is Raspberry Pi OS 64-bit on a Raspberry Pi 5;
Windows 10/11 64-bit is supported for industrial PCs, engineering workstations,
and local demonstrations. The application code is designed for ARM64 and
Windows x64 from the start; desktop development is not treated as a substitute
for Raspberry Pi validation. The package supplies:

- an offline-installable Python virtual environment or packaged service;
- a Linux `systemd` service and a Windows Service or Task Scheduler launcher
  for `rupmes-edge`, both with automatic restart;
- a Linux systemd timer and Windows scheduled task for retention and SQLite
  maintenance;
- Chromium or Microsoft Edge kiosk startup pointing at
  `http://127.0.0.1:<local-port>/edge`;
- Linux shell and Windows PowerShell install scripts that create restricted
  configuration and secrets paths;
- a configuration export/import command; and
- a health endpoint suitable for local diagnostics.

The service listens on loopback by default. Local-network administration is an
explicit configuration choice protected by local administrator authentication.

### Platform constraints

- Support Raspberry Pi 5 with at least 4 GB RAM and ARM64 Python wheels.
- Keep the steady-state process count to collector, local API, and Chromium;
  do not add Redis, a message broker, PostgreSQL, or containers as runtime
  requirements.
- Use SQLite WAL mode, bounded retention, batched writes, and indexed aggregate
  tables to reduce SD-card/SSD writes and keep dashboard queries predictable.
- Keep chart history and in-memory subscription caches bounded by configuration.
- Package all frontend assets locally; kiosk operation and normal dashboard use
  must continue without Internet access.
- Provide ARM64 installation and smoke-test instructions before considering the
  dashboard feature complete.
- Treat Ethernet as the expected OT connection. Wi-Fi configuration is outside
  the application runtime and must not be assumed.
- Use `pathlib`, explicit configuration directories, and Python wheels that
  support both ARM64 Linux and Windows x64. No Linux-only paths, shell commands,
  or service assumptions are allowed in application code.
- Keep Windows deployment local and self-contained: SQLite, frontend assets,
  OPC UA certificates, logs, and configuration remain on the device and do not
  require a central Windows server.

## Delivery sequence

1. Add edge configuration models, SQLite migrations, the connector protocol,
   and a simulated OPC UA server with unit tests.
2. Implement the long-lived read-only OPC UA connector, certificate handling,
   browsing, subscriptions, health, and reconnection tests.
3. Add station evaluation, cycles, counters, shift logic, aggregates, retention,
   and restart/reconnect tests.
4. Build the kiosk dashboard and local setup UI against the local API.
5. Add Raspberry Pi systemd/kiosk assets, installation documentation, and a
   hardware validation checklist.

No production PLC is contacted until the simulator tests pass and a reviewed,
read-only endpoint configuration is available.
