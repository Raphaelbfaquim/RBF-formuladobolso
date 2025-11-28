# Script PowerShell para tornar um usuário administrador
# Uso: .\scripts\make-admin.ps1 <email>

param(
    [Parameter(Mandatory=$true)]
    [string]$Email
)

Write-Host "`n=== Tornando Usuario Administrador ===" -ForegroundColor Cyan
Write-Host "Email: $Email" -ForegroundColor White

# Verificar se está no diretório correto
if (-not (Test-Path "back")) {
    Write-Host "❌ Execute este script na raiz do projeto!" -ForegroundColor Red
    exit 1
}

# Verificar se Python está disponível
$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCmd) {
    $pythonCmd = Get-Command python3 -ErrorAction SilentlyContinue
}

if (-not $pythonCmd) {
    Write-Host "❌ Python não encontrado! Instale Python primeiro." -ForegroundColor Red
    exit 1
}

Write-Host "`nExecutando script Python..." -ForegroundColor Yellow
& $pythonCmd.Name "scripts/make-admin.py" $Email

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✅ Concluído!" -ForegroundColor Green
} else {
    Write-Host "`n❌ Erro ao executar script!" -ForegroundColor Red
    exit 1
}

