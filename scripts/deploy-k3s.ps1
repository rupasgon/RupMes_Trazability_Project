param(
  [Parameter(Mandatory = $true)]
  [string]$Version,

  [string]$Namespace = "rupmes",
  [string]$ReleaseName = "rupmes",
  [string]$Registry = "registry-ot-sp.merit-automotive.com",
  [string]$Project = "rupmes",
  [string]$BackendImageName = "rupmes-backend",
  [string]$FrontendImageName = "rupmes-frontend",
  [string]$ValuesFile = "values-k3s-prod.yaml",
  [string]$ChartPath = ".\deploy\helm\rupmes",
  [string]$KubeConfigPath = "",
  [string]$HelmPath = "",
  [switch]$SkipBackend,
  [switch]$SkipFrontend,
  [switch]$SkipPush,
  [switch]$SkipDeploy,
  [switch]$RenderOnly
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Resolve-Helm {
  param([string]$RequestedPath)

  if ($RequestedPath -and (Test-Path $RequestedPath)) {
    return $RequestedPath
  }

  $helmCmd = Get-Command helm -ErrorAction SilentlyContinue
  if ($helmCmd) {
    return $helmCmd.Source
  }

  $wingetHelm = Join-Path $env:LOCALAPPDATA "Microsoft\WinGet\Packages\Helm.Helm_Microsoft.Winget.Source_8wekyb3d8bbwe\windows-amd64\helm.exe"
  if (Test-Path $wingetHelm) {
    return $wingetHelm
  }

  throw "Helm executable not found. Install Helm or pass -HelmPath."
}

function Invoke-Checked {
  param(
    [string]$FilePath,
    [string[]]$Arguments
  )

  & $FilePath @Arguments
  if ($LASTEXITCODE -ne 0) {
    throw "Command failed: $FilePath $($Arguments -join ' ')"
  }
}

if ($KubeConfigPath) {
  $env:KUBECONFIG = $KubeConfigPath
}

$helmExe = Resolve-Helm -RequestedPath $HelmPath
$backendRepository = "$Registry/$Project/$BackendImageName"
$frontendRepository = "$Registry/$Project/$FrontendImageName"
$backendImage = "${backendRepository}:${Version}"
$frontendImage = "${frontendRepository}:${Version}"

Write-Host "Release: $ReleaseName"
Write-Host "Namespace: $Namespace"
Write-Host "Backend image: $backendImage"
Write-Host "Frontend image: $frontendImage"

if (-not $SkipBackend) {
  Write-Host "Building backend image..."
  Invoke-Checked -FilePath "docker" -Arguments @("build", "-t", $backendImage, ".")
}

if (-not $SkipFrontend) {
  Write-Host "Building frontend image..."
  Invoke-Checked -FilePath "docker" -Arguments @("build", "-t", $frontendImage, ".\frontend")
}

if (-not $SkipPush) {
  if (-not $SkipBackend) {
    Write-Host "Pushing backend image..."
    Invoke-Checked -FilePath "docker" -Arguments @("push", $backendImage)
  }
  if (-not $SkipFrontend) {
    Write-Host "Pushing frontend image..."
    Invoke-Checked -FilePath "docker" -Arguments @("push", $frontendImage)
  }
}

$helmArgs = @(
  "upgrade", "--install", $ReleaseName, $ChartPath,
  "-n", $Namespace,
  "--create-namespace",
  "-f", $ValuesFile,
  "--set-string", "images.backend.repository=$backendRepository",
  "--set-string", "images.backend.tag=$Version",
  "--set-string", "images.frontend.repository=$frontendRepository",
  "--set-string", "images.frontend.tag=$Version"
)

if ($RenderOnly) {
  Write-Host "Rendering chart only..."
  Invoke-Checked -FilePath $helmExe -Arguments @("template", $ReleaseName, $ChartPath, "-n", $Namespace, "-f", $ValuesFile,
    "--set-string", "images.backend.repository=$backendRepository",
    "--set-string", "images.backend.tag=$Version",
    "--set-string", "images.frontend.repository=$frontendRepository",
    "--set-string", "images.frontend.tag=$Version")
  exit 0
}

if (-not $SkipDeploy) {
  Write-Host "Deploying with Helm..."
  Invoke-Checked -FilePath $helmExe -Arguments $helmArgs

  Write-Host "Waiting for backend rollout..."
  Invoke-Checked -FilePath "kubectl" -Arguments @("rollout", "status", "deployment/$ReleaseName-rupmes-backend", "-n", $Namespace, "--timeout=180s")

  Write-Host "Waiting for frontend rollout..."
  Invoke-Checked -FilePath "kubectl" -Arguments @("rollout", "status", "deployment/$ReleaseName-rupmes-frontend", "-n", $Namespace, "--timeout=180s")

  Write-Host "Ingress:"
  Invoke-Checked -FilePath "kubectl" -Arguments @("get", "ingress", "-n", $Namespace)
}
