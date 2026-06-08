param(
  [Parameter(Mandatory = $true)]
  [string]$ProjectRoot,

  [string]$ConfigPath = "",
  [string]$OutputRoot = "",
  [switch]$BuildBundle,
  [switch]$ZipPackage
)

$connectorRoot = Join-Path $ProjectRoot "production_connector"
$windowsRoot = Join-Path $connectorRoot "windows"
$distRoot = Join-Path $connectorRoot "dist\windows"
$cliBundleRoot = Join-Path $distRoot "cli\rupmes-connector"
$serviceBundleRoot = Join-Path $distRoot "service\rupmes-connector-service"
$releaseRoot = if ([string]::IsNullOrWhiteSpace($OutputRoot)) { Join-Path $connectorRoot "release\windows" } else { $OutputRoot }
$packageRoot = Join-Path $releaseRoot "RupMesProductionConnector"
$packageConnectorRoot = Join-Path $packageRoot "production_connector"
$packageWindowsRoot = Join-Path $packageConnectorRoot "windows"
$packageDistRoot = Join-Path $packageConnectorRoot "dist\windows"
$packageCliRoot = Join-Path $packageDistRoot "cli"
$packageServiceRoot = Join-Path $packageDistRoot "service"
$packageStateRoot = Join-Path $packageConnectorRoot "state"
$packageLogsRoot = Join-Path $packageConnectorRoot "logs"
$packageZip = Join-Path $releaseRoot "RupMesProductionConnector.zip"

if ($BuildBundle) {
  & (Join-Path $windowsRoot "build-bundle.ps1") -ProjectRoot $ProjectRoot
  if ($LASTEXITCODE -ne 0) { throw "Unable to build Windows bundle" }
}

$cliExe = Join-Path $cliBundleRoot "rupmes-connector.exe"
$serviceExe = Join-Path $serviceBundleRoot "rupmes-connector-service.exe"

if (-not (Test-Path $cliExe)) {
  throw "CLI bundle not found. Run build-bundle.ps1 first or use -BuildBundle."
}
if (-not (Test-Path $serviceExe)) {
  throw "Service bundle not found. Run build-bundle.ps1 first or use -BuildBundle."
}

if (Test-Path $packageRoot) {
  Remove-Item -LiteralPath $packageRoot -Recurse -Force
}

New-Item -ItemType Directory -Path $packageWindowsRoot -Force | Out-Null
New-Item -ItemType Directory -Path $packageCliRoot -Force | Out-Null
New-Item -ItemType Directory -Path $packageServiceRoot -Force | Out-Null
New-Item -ItemType Directory -Path $packageStateRoot -Force | Out-Null
New-Item -ItemType Directory -Path $packageLogsRoot -Force | Out-Null

Copy-Item -Path (Join-Path $windowsRoot "install.ps1") -Destination $packageWindowsRoot -Force
Copy-Item -Path (Join-Path $windowsRoot "install-task.ps1") -Destination $packageWindowsRoot -Force
Copy-Item -Path (Join-Path $windowsRoot "install-service.ps1") -Destination $packageWindowsRoot -Force
Copy-Item -Path (Join-Path $windowsRoot "uninstall-task.ps1") -Destination $packageWindowsRoot -Force
Copy-Item -Path (Join-Path $windowsRoot "uninstall-service.ps1") -Destination $packageWindowsRoot -Force

Copy-Item -Path (Join-Path $cliBundleRoot "*") -Destination $packageCliRoot -Recurse -Force
Copy-Item -Path (Join-Path $serviceBundleRoot "*") -Destination $packageServiceRoot -Recurse -Force

if (-not [string]::IsNullOrWhiteSpace($ConfigPath)) {
  Copy-Item -Path $ConfigPath -Destination (Join-Path $packageConnectorRoot "config.json") -Force
}
else {
  Copy-Item -Path (Join-Path $connectorRoot "config.example.json") -Destination (Join-Path $packageConnectorRoot "config.template.json") -Force
}

@'
RupMes Production Connector

Recommended installation on client machines:

1. Open PowerShell as administrator.
2. Edit production_connector\config.json if included, or copy config.template.json to config.json and complete it.
3. Install as Windows service:
   .\production_connector\windows\install-service.ps1 -ProjectRoot "<package-root>" -ConfigPath "<package-root>\production_connector\config.json"

Alternative lab mode:
   .\production_connector\windows\install-task.ps1 -ProjectRoot "<package-root>" -ConfigPath "<package-root>\production_connector\config.json"
'@ | Set-Content -Path (Join-Path $packageRoot "README.txt") -Encoding ASCII

if ($ZipPackage) {
  if (Test-Path $packageZip) {
    Remove-Item -LiteralPath $packageZip -Force
  }
  Compress-Archive -Path $packageRoot -DestinationPath $packageZip -Force
}

Write-Host "Windows client package created in $packageRoot"
if ($ZipPackage) {
  Write-Host "ZIP package created in $packageZip"
}
