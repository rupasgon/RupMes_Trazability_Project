[CmdletBinding()]
param(
    [string]$OutputDirectory,
    [switch]$SkipDependencyBundle
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
if (-not $OutputDirectory) {
    $OutputDirectory = Join-Path $projectRoot "dist"
}
$staging = Join-Path $env:TEMP ("rupmes-edge-package-" + [guid]::NewGuid())
$packageRoot = Join-Path $staging "RupMES-Edge-Windows"
$zipPath = Join-Path $OutputDirectory "RupMES-Edge-Windows.zip"

New-Item -ItemType Directory -Force -Path $packageRoot, $OutputDirectory | Out-Null
try {
    New-Item -ItemType Directory -Force -Path (Join-Path $packageRoot "app\src"), (Join-Path $packageRoot "app\scripts") | Out-Null
    Copy-Item -LiteralPath (Join-Path $projectRoot "src\rupmes_edge") -Destination (Join-Path $packageRoot "app\src") -Recurse
    Copy-Item -LiteralPath (Join-Path $projectRoot "scripts\Run-EdgeDashboard.ps1"), (Join-Path $projectRoot "scripts\Install-EdgeWindowsService.ps1") -Destination (Join-Path $packageRoot "app\scripts")
    Copy-Item -LiteralPath (Join-Path $projectRoot "scripts\edge-config.production.example.json") -Destination (Join-Path $packageRoot "config.example.json")
    Copy-Item -LiteralPath (Join-Path $projectRoot "scripts\Install-EdgePackage.ps1") -Destination $packageRoot
    Copy-Item -LiteralPath (Join-Path $projectRoot "scripts\INSTALL_EDGE_WINDOWS.cmd") -Destination $packageRoot
    $edgeRequirements = Join-Path $projectRoot "scripts\edge-requirements.txt"
    if (-not (Test-Path -LiteralPath $edgeRequirements)) { throw "scripts\\edge-requirements.txt is required to build the offline package." }
    Copy-Item -LiteralPath $edgeRequirements -Destination (Join-Path $packageRoot "edge-requirements.txt")
    if (-not $SkipDependencyBundle) {
        Copy-Item -LiteralPath (Join-Path $projectRoot "scripts\build_edge_vendor.py") -Destination (Join-Path $packageRoot "app\scripts")
        & python (Join-Path $projectRoot "scripts\build_edge_vendor.py") --destination (Join-Path $packageRoot "app\vendor")
        if ($LASTEXITCODE -ne 0) { throw "Could not bundle the installed Edge dependencies." }
        $wheels = Join-Path $packageRoot "wheels"
        New-Item -ItemType Directory -Force -Path $wheels | Out-Null
        & python -m pip download --dest $wheels --only-binary=:all: --requirement $edgeRequirements
        if ($LASTEXITCODE -ne 0) { throw "Could not create the offline dependency bundle." }
    }
    if (Test-Path -LiteralPath $zipPath) { Remove-Item -LiteralPath $zipPath -Force }
    Compress-Archive -Path (Join-Path $packageRoot "*") -DestinationPath $zipPath
    Write-Host "Package created: $zipPath" -ForegroundColor Green
} finally {
    Remove-Item -LiteralPath $staging -Recurse -Force -ErrorAction SilentlyContinue
}
