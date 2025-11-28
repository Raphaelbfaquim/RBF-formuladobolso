# Executar migração no servidor AWS
# Uso: .\run-migration.ps1

$ErrorActionPreference = "Stop"

Write-Host "Executando migração no servidor AWS..." -ForegroundColor Cyan
Write-Host ""

$AWS_HOST = "ubuntu@3.238.162.190"
$SSH_KEY = "$env:USERPROFILE\.ssh\LightsailDefaultKey-us-east-1.pem"

if (-not (Test-Path $SSH_KEY)) {
    Write-Host "SSH key nao encontrada: $SSH_KEY" -ForegroundColor Red
    exit 1
}

Write-Host "Conectando no servidor..." -ForegroundColor Yellow

# Executar migração
$migrationCmd = "cd ~/RBF-formuladobolso && docker-compose -f docker-compose.prod.yml exec -T api alembic upgrade head"

& ssh -i $SSH_KEY -o StrictHostKeyChecking=no -o ConnectTimeout=30 $AWS_HOST $migrationCmd

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "Migração executada com sucesso!" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "Erro ao executar migração!" -ForegroundColor Red
    exit 1
}

