# Linux Deployment

## Packaging on the development machine

Build the client-ready package:

```bash
cd /path/to/project
BUILD_BUNDLE=1 ZIP_PACKAGE=1 ./production_connector/linux/build-package.sh /path/to/project
```

If you already have the real client configuration:

```bash
cd /path/to/project
BUILD_BUNDLE=1 ZIP_PACKAGE=1 ./production_connector/linux/build-package.sh /path/to/project /path/to/project/production_connector/config.json
```

Generated output:

- `production_connector/release/linux/RupMesProductionConnector/`
- `production_connector/release/linux/RupMesProductionConnector.tar.gz`

## Files to copy to the client

Copy only the generated package folder or archive:

- `RupMesProductionConnector/`

Do not copy the source repository.

## Installation on the client

1. Copy the package to the target machine.
2. Extract it if you copied the archive.
3. Edit `production_connector/config.json` if included, or copy `config.template.json` to `config.json`.
4. Choose a unique lowercase instance ID, for example `bmw-szl-levers-wip`, and extract the package to `/opt/rupmes-connectors/<instance-id>`.
5. Copy `production_connector/secrets.env.template` to `production_connector/secrets.env` and store the integration `client_id` and API key there.
6. Copy the closest file from `production_connector/templates/` to `production_connector/config.json` when configuring TCP, Modbus or Siemens S7.
7. Validate before installing:

```bash
./production_connector/dist/linux/cli/rupmes-connector validate-config --config production_connector/config.json
```

8. Give execution permission to the installer scripts if needed:

```bash
chmod +x production_connector/linux/install.sh production_connector/linux/uninstall.sh
```

9. Install the independent service instance:

```bash
cd /opt/rupmes-connectors/bmw-szl-levers-wip
./production_connector/linux/install.sh bmw-szl-levers-wip
```

## Uninstall

```bash
cd /opt/rupmes-connectors/bmw-szl-levers-wip
./production_connector/linux/uninstall.sh bmw-szl-levers-wip
```

## Notes

- The client machine does not need Python if you install from the bundled package.
- The packaging machine does need Python to generate the bundle.
- SQL Server sources still require the OS-level ODBC driver on the client machine.
- The installer creates a `systemd` instance named `rupmes-production-connector@<instance-id>`. Each instance has its own package, configuration, secret file and checkpoint. Use `systemctl status rupmes-production-connector@<instance-id>` and `journalctl -u rupmes-production-connector@<instance-id>` to operate one connector without affecting the others.
- The Linux bundle executable is generated at `production_connector/dist/linux/cli/rupmes-connector`.
- Build the Linux bundle on the same CPU architecture as its destination. Raspberry Pi requires ARM64/aarch64 packaging.
