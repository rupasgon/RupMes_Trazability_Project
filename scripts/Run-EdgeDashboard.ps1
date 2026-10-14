[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$ProjectRoot,

    [string]$ConfigPath = (Join-Path $env:ProgramData "RupMES Edge\config.json"),

    [string]$PythonExe = "python"
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path -LiteralPath $ConfigPath -PathType Leaf)) {
    throw "Edge configuration was not found: $ConfigPath"
}

$sourcePath = Join-Path $ProjectRoot "src"
$vendorPath = Join-Path $ProjectRoot "vendor"
$env:PYTHONPATH = if (Test-Path -LiteralPath $vendorPath) { "$vendorPath;$sourcePath" } else { $sourcePath }
$env:RUPMES_EDGE_CONFIG = $ConfigPath
& $PythonExe -m rupmes_edge dashboard --config $ConfigPath
exit $LASTEXITCODE
