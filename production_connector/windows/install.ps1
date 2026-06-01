param(
  [Parameter(Mandatory = $true)]
  [string]$ProjectRoot,

  [Parameter(Mandatory = $true)]
  [string]$ConfigPath,

  [string]$PythonExe = "python",
  [string]$TaskName = "RupMesProductionConnector"
)

$connectorRoot = Join-Path $ProjectRoot "production_connector"
$venvPath = Join-Path $connectorRoot ".venv"
$pythonVenv = Join-Path $venvPath "Scripts\python.exe"

Write-Host "Creating virtual environment in $venvPath"
& $PythonExe -m venv $venvPath

Write-Host "Installing connector dependencies"
& $pythonVenv -m pip install --upgrade pip
& $pythonVenv -m pip install -e "$ProjectRoot[connector]"

$action = New-ScheduledTaskAction -Execute $pythonVenv -Argument "-m rupmes_connector run --config `"$ConfigPath`""
$trigger = New-ScheduledTaskTrigger -AtStartup
$settings = New-ScheduledTaskSettingsSet -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1)

Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Settings $settings -Description "RupMes production connector" -Force | Out-Null

Write-Host "Installed scheduled task $TaskName"
Write-Host "Run once manually with:"
Write-Host "`"$pythonVenv`" -m rupmes_connector run-once --config `"$ConfigPath`""
