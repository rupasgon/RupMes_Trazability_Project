# Windows Deployment

## Packaging on the development machine

Build the client-ready package:

```powershell
cd C:\path\to\project
.\production_connector\windows\build-package.ps1 -ProjectRoot "C:\path\to\project" -BuildBundle -ZipPackage
```

If you already have the real client configuration:

```powershell
cd C:\path\to\project
.\production_connector\windows\build-package.ps1 -ProjectRoot "C:\path\to\project" -ConfigPath "C:\path\to\project\production_connector\config.json" -BuildBundle -ZipPackage
```

Generated output:

- `production_connector\release\windows\RupMesProductionConnector\`
- `production_connector\release\windows\RupMesProductionConnector.zip`

## Files to copy to the client

Copy only the generated package folder or ZIP:

- `RupMesProductionConnector\`

Do not copy the source repository.

## Installation on the client

1. Copy the package to the target machine.
2. Extract it if you copied the ZIP.
3. Edit `production_connector\config.json` if included, or copy `config.template.json` to `config.json`.
4. Open PowerShell as administrator.
5. Install the service:

```powershell
cd C:\path\to\RupMesProductionConnector
.\production_connector\windows\install-service.ps1 -ProjectRoot "C:\path\to\RupMesProductionConnector" -ConfigPath "C:\path\to\RupMesProductionConnector\production_connector\config.json"
```

## Uninstall

```powershell
cd C:\path\to\RupMesProductionConnector
.\production_connector\windows\uninstall-service.ps1 -ProjectRoot "C:\path\to\RupMesProductionConnector"
```

## Notes

- The client machine does not need Python preinstalled.
- The packaging machine does need Python to generate the bundle.
- SQL Server sources still require the Microsoft ODBC driver on the client machine.
