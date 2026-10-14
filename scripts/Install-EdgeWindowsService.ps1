[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$ProjectRoot,

    [string]$PythonExe = "python",

    [string]$ConfigPath = (Join-Path $env:ProgramData "RupMES Edge\config.json"),

    [string]$TaskName = "RupMES Edge Dashboard"
)

$ErrorActionPreference = "Stop"

if (-not ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    throw "Run this script from an elevated PowerShell window."
}

$project = (Resolve-Path -LiteralPath $ProjectRoot).Path
$configDirectory = Split-Path -Parent $ConfigPath
$runScript = Join-Path $project "scripts\Run-EdgeDashboard.ps1"
$template = Join-Path $project "scripts\edge-config.production.example.json"

if (-not (Test-Path -LiteralPath $runScript -PathType Leaf)) {
    throw "Run script not found: $runScript"
}

New-Item -ItemType Directory -Force -Path $configDirectory, (Join-Path $configDirectory "certificates"), (Join-Path $configDirectory "data") | Out-Null

if (-not (Test-Path -LiteralPath $ConfigPath)) {
    Copy-Item -LiteralPath $template -Destination $ConfigPath
    Write-Warning "Template created at $ConfigPath. Configure the PLC endpoint, NodeIds and certificates before starting the service."
}

$arguments = "-NoProfile -ExecutionPolicy Bypass -File `"$runScript`" -ProjectRoot `"$project`" -ConfigPath `"$ConfigPath`" -PythonExe `"$PythonExe`""
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument $arguments
$trigger = New-ScheduledTaskTrigger -AtStartup
$principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1) -ExecutionTimeLimit (New-TimeSpan -Days 0)

Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Force | Out-Null
Write-Host "Scheduled task '$TaskName' installed. Edit $ConfigPath, then run: Start-ScheduledTask -TaskName '$TaskName'"
