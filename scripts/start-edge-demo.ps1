param(
    [int]$Port = 8020
)

$projectRoot = Split-Path -Parent $PSScriptRoot
$python = Join-Path $projectRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $python)) {
    $python = (Get-Command py -ErrorAction Stop).Source
}

Push-Location $projectRoot
try {
    Start-Process -FilePath $python -ArgumentList "-3.14 -m rupmes_edge simulator" -WorkingDirectory $projectRoot
    Start-Sleep -Seconds 2
    & $python -m rupmes_edge dashboard --port $Port
}
finally {
    Pop-Location
}
