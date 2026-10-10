param(
  [Parameter(Mandatory = $true)]
  [string]$ProjectRoot,

  [Parameter(Mandatory = $true)]
  [string]$ConfigPath,

  [string]$PythonExe = "python",
  [string]$TaskName = "RupMesProductionConnector"
)

Write-Host "install.ps1 keeps backward compatibility and installs the scheduled task mode."
Write-Host "For a production Windows service use production_connector\\windows\\install-service.ps1."

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$taskInstaller = Join-Path $scriptRoot "install-task.ps1"

& $taskInstaller -ProjectRoot $ProjectRoot -ConfigPath $ConfigPath -PythonExe $PythonExe -TaskName $TaskName
exit $LASTEXITCODE
