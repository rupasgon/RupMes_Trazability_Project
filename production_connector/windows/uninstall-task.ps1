param(
  [string]$TaskName = "RupMesProductionConnector"
)

$task = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if (-not $task) {
  Write-Host "Scheduled task $TaskName not found"
  exit 0
}

Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
Write-Host "Uninstalled scheduled task $TaskName"
