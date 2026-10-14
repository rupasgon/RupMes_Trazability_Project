[CmdletBinding()]
param(
    [string]$InstallRoot = "C:\Program Files\RupMES Edge",
    [string]$TaskName = "RupMES Edge Dashboard"
)

$ErrorActionPreference = "Stop"

if (-not ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole(
        [Security.Principal.WindowsBuiltInRole]::Administrator)) {
    throw "Run this update as Administrator."
}

$payloadRoot = Join-Path $PSScriptRoot "payload\src\rupmes_edge"
$targetRoot = Join-Path $InstallRoot "src\rupmes_edge"
$files = @("app.py", "runtime.py", "store.py", "static\index.html")

if (-not (Test-Path -LiteralPath $targetRoot)) {
    throw "RupMES Edge was not found in: $InstallRoot"
}

foreach ($relativeFile in $files) {
    $source = Join-Path $payloadRoot $relativeFile
    $destination = Join-Path $targetRoot $relativeFile
    if (-not (Test-Path -LiteralPath $source)) {
        throw "Update payload is incomplete: $source"
    }

    New-Item -ItemType Directory -Path (Split-Path -Parent $destination) -Force | Out-Null
    Copy-Item -LiteralPath $source -Destination $destination -Force
}

Stop-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2
Start-ScheduledTask -TaskName $TaskName

Write-Host "RupMES Edge history update installed. Reload http://127.0.0.1:8020/edge"
