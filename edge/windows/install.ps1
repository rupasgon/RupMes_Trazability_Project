param(
    [Parameter(Mandatory)] [string]$PackagePath,
    [string]$InstallRoot = "$env:ProgramFiles\RupMES Edge",
    [string]$DataRoot = "$env:ProgramData\RupMES Edge"
)

$ErrorActionPreference = "Stop"
New-Item -ItemType Directory -Force $InstallRoot, $DataRoot, "$DataRoot\certs", "$DataRoot\data" | Out-Null
$python = (Get-Command py -ErrorAction Stop).Source
& $python -3.14 -m venv "$InstallRoot\venv"
& "$InstallRoot\venv\Scripts\python.exe" -m pip install --upgrade pip
& "$InstallRoot\venv\Scripts\python.exe" -m pip install "${PackagePath}[edge]"
Copy-Item "$PSScriptRoot\..\config.example.json" "$DataRoot\config.json" -ErrorAction SilentlyContinue
(Get-Content "$DataRoot\config.json" -Raw).Replace('"data/rupmes-edge.db"', ('"' + ($DataRoot.Replace('\', '\\')) + '\\data\\rupmes-edge.db"')) | Set-Content "$DataRoot\config.json" -Encoding utf8
@"
RUPMES_EDGE_CONFIG=$DataRoot\config.json
RUPMES_EDGE_ADMIN_TOKEN=change-me-before-starting
RUPMES_EDGE_PLC_01_PASSWORD=replace-with-a-read-only-PLC-password
"@ | Set-Content "$DataRoot\secrets.env" -Encoding ascii

$action = New-ScheduledTaskAction -Execute "$InstallRoot\venv\Scripts\rupmes-edge.exe" -Argument "dashboard --config `"$DataRoot\config.json`""
$trigger = New-ScheduledTaskTrigger -AtStartup
Register-ScheduledTask -TaskName "RupMES Edge" -Action $action -Trigger $trigger -RunLevel Highest -User "SYSTEM" -Force
Write-Output "Review $DataRoot\config.json and certificates before starting the RupMES Edge task."
