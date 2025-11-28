# Script para executar migrações no Docker
# Uso: .\run-migrations.ps1

Write-Host "Executando migracoes do banco de dados..." -ForegroundColor Cyan

# Verificar se está usando docker-compose da raiz ou do back
if (Test-Path "docker-compose.yml") {
    Write-Host "Usando docker-compose.yml da raiz" -ForegroundColor Yellow
    
    # Parar containers conflitantes se existirem
    docker-compose down 2>$null
    
    # Iniciar serviços
    docker-compose up -d postgres redis
    
    # Aguardar PostgreSQL ficar pronto
    Write-Host "Aguardando PostgreSQL ficar pronto..." -ForegroundColor Yellow
    Start-Sleep -Seconds 5
    
    # Executar migrações com variáveis de ambiente corretas
    docker-compose exec -e DATABASE_SYNC_URL=postgresql://formulado_user:formulado_pass@postgres:5432/formulado_db api alembic upgrade head
} else {
    Write-Host "Usando docker-compose.yml do diretorio back" -ForegroundColor Yellow
    cd back
    docker-compose exec -e DATABASE_SYNC_URL=postgresql://formulado_user:formulado_pass@postgres:5432/formulado_db api alembic upgrade head
}

if ($LASTEXITCODE -eq 0) {
    Write-Host "`nMigracoes executadas com sucesso!" -ForegroundColor Green
} else {
    Write-Host "`nErro ao executar migracoes!" -ForegroundColor Red
}

