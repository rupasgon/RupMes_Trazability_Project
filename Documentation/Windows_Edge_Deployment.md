# RupMES Edge on Windows

## Easy installation package

On the development PC, generate one ZIP file:

```powershell
.\scripts\Build-EdgeWindowsPackage.ps1
```

Copy only `dist\RupMES-Edge-Windows.zip` to the destination PC, extract it and run `INSTALL_EDGE_WINDOWS.cmd` with **Run as administrator**. The ZIP includes an offline Python wheel bundle for the Edge runtime, so the destination PC does not need Internet access. The installer creates the Python environment, installs dependencies from that bundle, preserves an existing configuration and registers automatic startup.

The only manual work afterwards is completing the generated `C:\ProgramData\RupMES Edge\config.json`, copying the OPC UA certificates and setting the two machine secrets.

## Files kept locally on the Edge PC

Create `C:\ProgramData\RupMES Edge\` with:

- `config.json`: PLC endpoint, station NodeIds, UI binding and SQLite retention.
- `certificates\`: OPC UA client certificate, private key and trusted PLC certificate.
- `data\rupmes-edge.db`: local SQLite history of station state changes, cycles and connector health.

These paths are outside the repository and must not be copied to Git.

## Configure

1. Copy `scripts\edge-config.production.example.json` to `C:\ProgramData\RupMES Edge\config.json`.
2. Replace the endpoint placeholder, NodeIds, station names and targets.
3. Put the three OPC UA certificate files in the configured paths.
4. Set the password and dashboard administration token as machine environment variables:

```powershell
[Environment]::SetEnvironmentVariable("RUPMES_EDGE_OPCUA_PASSWORD", "<reader-password>", "Machine")
[Environment]::SetEnvironmentVariable("RUPMES_EDGE_ADMIN_TOKEN", "<long-random-token>", "Machine")
```

The OPC UA account must be read-only. Do not expose the dashboard to an untrusted network; its default binding is `127.0.0.1`.

## Run manually

```powershell
$env:PYTHONPATH = "C:\RupMES\RupMes_Trazability_Project\src"
python -m rupmes_edge dashboard --config "C:\ProgramData\RupMES Edge\config.json"
```

Open `http://127.0.0.1:8020/edge`.

## Register automatic startup

From an elevated PowerShell window:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\scripts\Install-EdgeWindowsService.ps1 -ProjectRoot "C:\RupMES\RupMes_Trazability_Project" -PythonExe "C:\RupMES\RupMes_Trazability_Project\.venv\Scripts\python.exe"
Start-ScheduledTask -TaskName "RupMES Edge Dashboard"
```

The task runs as `SYSTEM`, starts on boot and retries three times after a failure. Validate `/edge/health` after installation.
