param(
  [Parameter(Mandatory = $true)]
  [string]$ProjectRoot,

  [string]$BundleRoot = "",
  [string]$PythonExe = "python"
)

$connectorRoot = Join-Path $ProjectRoot "production_connector"
$defaultBundleRoot = Join-Path $connectorRoot "dist\windows\service"
$bundleRootPath = if ([string]::IsNullOrWhiteSpace($BundleRoot)) { $defaultBundleRoot } else { $BundleRoot }
$bundleSettingsPath = Join-Path $bundleRootPath "service.settings.json"
$windowsRoot = Join-Path $connectorRoot "windows"
$venvPath = Join-Path $connectorRoot ".venv"
$pythonVenv = Join-Path $venvPath "Scripts\python.exe"
$settingsPath = if (Test-Path $bundleSettingsPath) { $bundleSettingsPath } else { Join-Path $windowsRoot "service.settings.json" }

if (-not (Test-Path $settingsPath)) {
  Write-Host "Service settings file not found: $settingsPath"
  Write-Host "Nothing to uninstall."
  exit 0
}

$settings = Get-Content $settingsPath -Raw | ConvertFrom-Json
$serviceName = $settings.service_name
$serviceExecutable = $settings.service_executable

if (-not (Get-Service -Name $serviceName -ErrorAction SilentlyContinue)) {
  Write-Host "Windows service $serviceName not found"
  Remove-Item -LiteralPath $settingsPath -Force -ErrorAction SilentlyContinue
  exit 0
}

if ($serviceExecutable -and (Test-Path $serviceExecutable)) {
  & $serviceExecutable stop
  & $serviceExecutable remove
}
else {
  & $pythonVenv -m rupmes_connector.windows_service stop
  & $pythonVenv -m rupmes_connector.windows_service remove
}

Remove-Item -LiteralPath $settingsPath -Force -ErrorAction SilentlyContinue
Write-Host "Uninstalled Windows service $serviceName"
