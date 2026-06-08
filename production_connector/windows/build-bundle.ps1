param(
  [Parameter(Mandatory = $true)]
  [string]$ProjectRoot,

  [string]$PythonExe = "python"
)

$connectorRoot = Join-Path $ProjectRoot "production_connector"
$windowsRoot = Join-Path $connectorRoot "windows"
$buildVenvPath = Join-Path $connectorRoot ".build-venv"
$pythonBuild = Join-Path $buildVenvPath "Scripts\python.exe"
$pyinstallerExe = Join-Path $buildVenvPath "Scripts\pyinstaller.exe"
$distRoot = Join-Path $connectorRoot "dist\windows"
$buildRoot = Join-Path $connectorRoot "build\windows"
$specRoot = Join-Path $buildRoot "spec"
$cliDist = Join-Path $distRoot "cli"
$serviceDist = Join-Path $distRoot "service"
$cliWork = Join-Path $buildRoot "cli"
$serviceWork = Join-Path $buildRoot "service"

Write-Host "Creating build virtual environment in $buildVenvPath"
& $PythonExe -m venv $buildVenvPath
if ($LASTEXITCODE -ne 0) { throw "Unable to create build virtual environment" }

Write-Host "Installing build dependencies"
& $pythonBuild -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) { throw "Unable to upgrade pip" }
& $pythonBuild -m pip install -e "$ProjectRoot[connector,connector-build]"
if ($LASTEXITCODE -ne 0) { throw "Unable to install build dependencies" }

New-Item -ItemType Directory -Path $cliDist -Force | Out-Null
New-Item -ItemType Directory -Path $serviceDist -Force | Out-Null
New-Item -ItemType Directory -Path $cliWork -Force | Out-Null
New-Item -ItemType Directory -Path $serviceWork -Force | Out-Null
New-Item -ItemType Directory -Path $specRoot -Force | Out-Null

Write-Host "Building CLI bundle"
& $pyinstallerExe --noconfirm --clean --onedir --contents-directory . --name rupmes-connector --distpath $cliDist --workpath $cliWork --specpath $specRoot "$windowsRoot\entry_cli.py"
if ($LASTEXITCODE -ne 0) { throw "Unable to build CLI bundle" }

Write-Host "Building Windows service bundle"
& $pyinstallerExe --noconfirm --clean --onedir --contents-directory . --name rupmes-connector-service --distpath $serviceDist --workpath $serviceWork --specpath $specRoot "$windowsRoot\entry_service.py"
if ($LASTEXITCODE -ne 0) { throw "Unable to build Windows service bundle" }

Write-Host "Bundles created in $distRoot"
