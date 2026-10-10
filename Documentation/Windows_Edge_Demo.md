# Windows OPC UA Dashboard Demo

This demo runs a local read-only OPC UA simulator and a standalone RupMES Edge
dashboard. It does not connect to a PLC, the central RupMES API, or PostgreSQL.

## Prerequisites

- Windows 10 or 11, 64-bit
- Python 3.10 or newer

From the repository root, create an environment and install the edge extra:

```powershell
py -3.14 -m venv .venv
.venv\Scripts\Activate.ps1
py -3.14 -m pip install -e .[edge,dev]
```

## Run the demo

Start both local services with:

```powershell
.\scripts\start-edge-demo.ps1
```

Open `http://127.0.0.1:8020/edge`.

The simulator provides four stations. Their running, idle, manual, fault,
counter, and cycle-time values change every second. Station `ST03` periodically
raises alarm `E-201` so the dashboard fault view can be verified.

To run the processes separately, use two PowerShell windows:

```powershell
py -3.14 -m rupmes_edge simulator
```

```powershell
py -3.14 -m rupmes_edge dashboard
```

Stop each process with `Ctrl+C`. The dashboard exposes `GET /edge/health` and
`GET /edge/api/snapshot` for diagnostics. To test against a real read-only OPC
UA endpoint later, set `RUPMES_EDGE_OPCUA_ENDPOINT` before starting the
dashboard; station NodeId configuration will be added in the administration
phase.
