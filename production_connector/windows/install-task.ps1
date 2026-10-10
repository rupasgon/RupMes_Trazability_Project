param(
  [Parameter(Mandatory = $true)]
  [string]$ProjectRoot,

  [Parameter(Mandatory = $true)]
  [string]$ConfigPath,

  [string]$BundleRoot = "",
  [string]$PythonExe = "python",
  [string]$TaskName = "RupMesProductionConnector"
)

$connectorRoot = Join-Path $ProjectRoot "production_connector"
$distRoot = if ([string]::IsNullOrWhiteSpace($BundleRoot)) { Join-Path $connectorRoot "dist\windows\cli" } else { $BundleRoot }
$bundleRootPath = Join-Path $distRoot "rupmes-connector"
$bundleExe = Join-Path $bundleRootPath "rupmes-connector.exe"
$venvPath = Join-Path $connectorRoot ".venv"
$pythonVenv = Join-Path $venvPath "Scripts\python.exe"

$taskExec = $null
$taskArgs = $null

if (Test-Path $bundleExe) {
  Write-Host "Using bundled connector executable at $bundleExe"
  $taskExec = $bundleExe
  $taskArgs = "run --config `"$ConfigPath`""
}
else {
  Write-Host "Bundled executable not found. Falling back to Python-based install."
  Write-Host "Creating virtual environment in $venvPath"
  & $PythonExe -m venv $venvPath
  if ($LASTEXITCODE -ne 0) { throw "Unable to create virtual environment" }

  Write-Host "Installing connector dependencies"
  & $pythonVenv -m pip install --upgrade pip
  if ($LASTEXITCODE -ne 0) { throw "Unable to upgrade pip" }
  & $pythonVenv -m pip install -e "$ProjectRoot[connector]"
  if ($LASTEXITCODE -ne 0) { throw "Unable to install connector dependencies" }

  $taskExec = $pythonVenv
  $taskArgs = "-m rupmes_connector run --config `"$ConfigPath`""
}

$action = New-ScheduledTaskAction -Execute $taskExec -Argument $taskArgs
$trigger = New-ScheduledTaskTrigger -AtStartup
$settings = New-ScheduledTaskSettingsSet -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1)

Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Settings $settings -Description "RupMes production connector" -Force | Out-Null

Write-Host "Installed scheduled task $TaskName"
Write-Host "Run once manually with:"
if (Test-Path $bundleExe) {
  Write-Host "`"$bundleExe`" run-once --config `"$ConfigPath`""
}
else {
  Write-Host "`"$pythonVenv`" -m rupmes_connector run-once --config `"$ConfigPath`""
}
