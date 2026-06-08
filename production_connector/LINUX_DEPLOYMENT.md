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
4. Give execution permission to the installer scripts if needed:

```bash
chmod +x production_connector/linux/install.sh production_connector/linux/uninstall.sh
```

5. Install the service:

```bash
cd /path/to/RupMesProductionConnector
./production_connector/linux/install.sh /path/to/RupMesProductionConnector /path/to/RupMesProductionConnector/production_connector/config.json
```

## Uninstall

```bash
cd /path/to/RupMesProductionConnector
./production_connector/linux/uninstall.sh /path/to/RupMesProductionConnector
```

## Notes

- The client machine does not need Python if you install from the bundled package.
- The packaging machine does need Python to generate the bundle.
- SQL Server sources still require the OS-level ODBC driver on the client machine.
- The installer creates a `systemd` service called `rupmes-production-connector`.
- The Linux bundle executable is generated at `production_connector/dist/linux/cli/rupmes-connector/rupmes-connector`.
