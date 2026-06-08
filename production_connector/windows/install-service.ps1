param(
  [Parameter(Mandatory = $true)]
  [string]$ProjectRoot,

  [Parameter(Mandatory = $true)]
  [string]$ConfigPath,

  [string]$BundleRoot = "",
  [string]$PythonExe = "python",
  [string]$ServiceName = "RupMesProductionConnectorService",
  [string]$DisplayName = "RupMes Production Connector",
  [string]$Description = "RupMes production gateway service",
  [string]$LogPath = ""
)

$connectorRoot = Join-Path $ProjectRoot "production_connector"
$defaultBundleRoot = Join-Path $connectorRoot "dist\windows\service"
$bundleRootPath = if ([string]::IsNullOrWhiteSpace($BundleRoot)) { $defaultBundleRoot } else { $BundleRoot }
$bundleRuntimeRoot = Join-Path $bundleRootPath "rupmes-connector-service"
$bundleExe = Join-Path $bundleRuntimeRoot "rupmes-connector-service.exe"
$windowsRoot = if (Test-Path $bundleExe) { $bundleRuntimeRoot } else { Join-Path $connectorRoot "windows" }
$venvPath = Join-Path $connectorRoot ".venv"
$pythonVenv = Join-Path $venvPath "Scripts\python.exe"
$settingsPath = Join-Path $windowsRoot "service.settings.json"

if ([string]::IsNullOrWhiteSpace($LogPath)) {
  $LogPath = Join-Path $connectorRoot "logs\windows-service.log"
}

if (Get-Service -Name $ServiceName -ErrorAction SilentlyContinue) {
  throw "Windows service $ServiceName already exists. Uninstall it first."
}

$serviceCommand = $null

if (Test-Path $bundleExe) {
  Write-Host "Using bundled Windows service executable at $bundleExe"
  $serviceCommand = $bundleExe
}
else {
  Write-Host "Bundled Windows service executable not found. Falling back to Python-based install."
  Write-Host "Creating virtual environment in $venvPath"
  & $PythonExe -m venv $venvPath
  if ($LASTEXITCODE -ne 0) { throw "Unable to create virtual environment" }

  Write-Host "Installing connector dependencies"
  & $pythonVenv -m pip install --upgrade pip
  if ($LASTEXITCODE -ne 0) { throw "Unable to upgrade pip" }
  & $pythonVenv -m pip install -e "$ProjectRoot[connector]"
  if ($LASTEXITCODE -ne 0) { throw "Unable to install connector dependencies" }

  $serviceCommand = "$pythonVenv -m rupmes_connector.windows_service"
}

$settings = @{
  service_name = $ServiceName
  display_name = $DisplayName
  description  = $Description
  config_path  = $ConfigPath
  log_path     = $LogPath
  service_executable = $serviceCommand
}

$settings | ConvertTo-Json | Set-Content -Path $settingsPath -Encoding UTF8

Write-Host "Installing Windows service $ServiceName"
if (Test-Path $bundleExe) {
  & $bundleExe --startup auto install
}
else {
  & $pythonVenv -m rupmes_connector.windows_service --startup auto install
}
if ($LASTEXITCODE -ne 0) { throw "Unable to install Windows service" }

if (Test-Path $bundleExe) {
  & $bundleExe start
}
else {
  & $pythonVenv -m rupmes_connector.windows_service start
}
if ($LASTEXITCODE -ne 0) { throw "Service installed but could not be started" }

Write-Host "Installed Windows service $ServiceName"
Write-Host "Service settings: $settingsPath"
Write-Host "Service log: $LogPath"
