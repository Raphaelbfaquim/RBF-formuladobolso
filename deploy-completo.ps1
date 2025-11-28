# Deploy Completo: Build + Push + Deploy + Testes
# Uso: .\deploy-completo.ps1 [api|front|marketing|all]

param([string]$service = "all")

$ErrorActionPreference = "Stop"
$service = $service.ToLower()
if ($service -eq "frontend") { $service = "front" }

if ($service -notin @("api", "front", "marketing", "all")) {
    Write-Host "Uso: .\deploy-completo.ps1 [api|front|marketing|all]" -ForegroundColor Yellow
    exit 1
}

Write-Host "=== DEPLOY COMPLETO ===" -ForegroundColor Cyan
Write-Host "Servico: $service" -ForegroundColor Cyan
Write-Host ""

# PASSO 1: Build e Push
Write-Host "=== PASSO 1: Build e Push ===" -ForegroundColor Yellow
& "$PSScriptRoot\deploy-build-push.ps1" -service $service

if ($LASTEXITCODE -ne 0) {
    Write-Host "Erro no build/push!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "=== PASSO 2: Deploy no Servidor ===" -ForegroundColor Yellow
& "$PSScriptRoot\deploy-server.ps1" -service $service

if ($LASTEXITCODE -ne 0) {
    Write-Host "Erro no deploy!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "=== DEPLOY COMPLETO FINALIZADO ===" -ForegroundColor Green

