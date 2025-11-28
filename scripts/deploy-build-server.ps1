# Deploy fazendo BUILD DIRETO NO SERVIDOR (mais confiável)
# Uso: .\scripts\deploy-build-server.ps1 [api|front|all]
#      api   - Deploy apenas da API
#      front - Deploy apenas do Frontend
#      all   - Deploy de ambos (padrao)
#
# VANTAGEM: Garante que o código mais recente do repositório é usado

param(
    [string]$service = "all"
)

$ErrorActionPreference = "Stop"

# Normalizar parametro
$service = $service.ToLower()
if ($service -eq "frontend") { $service = "front" }

# Validar parametro
if ($service -notin @("api", "front", "all")) {
    Write-Host "Parametro invalido: $service" -ForegroundColor Red
    Write-Host "Uso: .\scripts\deploy-build-server.ps1 [api|front|all]" -ForegroundColor Yellow
    exit 1
}

Write-Host "Deploy com Build no Servidor AWS" -ForegroundColor Cyan
Write-Host "Servico: $service" -ForegroundColor Cyan
Write-Host ""

# Configuracoes
$AWS_HOST = "ubuntu@3.238.162.190"
$SSH_KEY = "$env:USERPROFILE\.ssh\LightsailDefaultKey-us-east-1.pem"

# Verificar SSH key
if (-not (Test-Path $SSH_KEY)) {
    Write-Host "Chave SSH nao encontrada: $SSH_KEY" -ForegroundColor Red
    exit 1
}

# Construir script bash para executar no servidor
$scriptLines = @()
$scriptLines += "set -e"
$scriptLines += "cd ~/RBF-formuladobolso || { git clone https://github.com/Raphaelbfaquim/RBF-formuladobolso.git && cd RBF-formuladobolso; }"
$scriptLines += ""
$scriptLines += "echo 'Atualizando codigo do repositorio...'"
$scriptLines += "git pull origin main"
$scriptLines += ""

# Parar containers antigos
$scriptLines += "echo 'Parando containers antigos...'"
if ($service -eq "api") {
    $scriptLines += "docker-compose -f docker-compose.prod.yml stop api || true"
    $scriptLines += "docker-compose -f docker-compose.prod.yml rm -f api || true"
} elseif ($service -eq "front") {
    $scriptLines += "docker-compose -f docker-compose.prod.yml stop frontend nginx || true"
    $scriptLines += "docker-compose -f docker-compose.prod.yml rm -f frontend nginx || true"
} else {
    $scriptLines += "docker-compose -f docker-compose.prod.yml down || true"
}

$scriptLines += ""
$scriptLines += "# Limpar imagens antigas"
$scriptLines += "echo 'Limpando imagens antigas...'"
if ($service -eq "api" -or $service -eq "all") {
    $scriptLines += "docker rmi efaquim/formulado-api:latest formulado-api:latest 2>/dev/null || true"
}
if ($service -eq "front" -or $service -eq "all") {
    $scriptLines += "docker rmi efaquim/formulado-frontend:latest formulado-frontend:latest 2>/dev/null || true"
}

$scriptLines += ""
$scriptLines += "# Build das imagens no servidor (SEM CACHE)"
$scriptLines += "export DOCKER_USERNAME=efaquim"
$scriptLines += "export IMAGE_TAG=latest"

if ($service -eq "api" -or $service -eq "all") {
    $scriptLines += "echo 'Buildando API no servidor (sem cache)...'"
    $scriptLines += "docker build --no-cache -t formulado-api:latest -f back/docker/Dockerfile back/"
    $scriptLines += "docker tag formulado-api:latest efaquim/formulado-api:latest"
}

if ($service -eq "front" -or $service -eq "all") {
    $scriptLines += "echo 'Buildando Frontend no servidor (sem cache)...'"
    $scriptLines += "docker build --no-cache -t formulado-frontend:latest -f front/Dockerfile --build-arg NEXT_PUBLIC_API_URL=http://3.238.162.190 front/"
    $scriptLines += "docker tag formulado-frontend:latest efaquim/formulado-frontend:latest"
}

$scriptLines += ""
$scriptLines += "# Limpar cache do Docker"
$scriptLines += "docker system prune -f || true"
$scriptLines += ""

# Iniciar containers
$scriptLines += "echo 'Iniciando containers...'"
if ($service -eq "api") {
    $scriptLines += "docker-compose -f docker-compose.prod.yml up -d --force-recreate --no-deps api"
    $scriptLines += "echo 'Aguardando API iniciar...'"
    $scriptLines += "sleep 10"
    $scriptLines += "echo 'Executando migracoes do banco de dados...'"
    $scriptLines += "docker-compose -f docker-compose.prod.yml exec -T api alembic upgrade head || echo 'Aviso: Nao foi possivel executar migracoes'"
} elseif ($service -eq "front") {
    $scriptLines += "docker-compose -f docker-compose.prod.yml up -d --force-recreate --no-deps frontend nginx"
} else {
    $scriptLines += "docker-compose -f docker-compose.prod.yml up -d --force-recreate"
    $scriptLines += "echo 'Aguardando servicos iniciarem...'"
    $scriptLines += "sleep 15"
    $scriptLines += "echo 'Executando migracoes do banco de dados...'"
    $scriptLines += "docker-compose -f docker-compose.prod.yml exec -T api alembic upgrade head || echo 'Aviso: Nao foi possivel executar migracoes'"
}

$scriptLines += ""
$scriptLines += "# Verificar status dos containers"
$scriptLines += "echo ''"
$scriptLines += "echo 'Status dos containers:'"
$scriptLines += "docker-compose -f docker-compose.prod.yml ps"
$scriptLines += ""
$scriptLines += "echo 'Deploy concluido!'"

$deployScript = $scriptLines -join "`n"

# Executar script na AWS
Write-Host "Executando deploy na AWS (build no servidor)..." -ForegroundColor Cyan
$fullScript = "export SERVICE_TYPE=$service`n$deployScript"
$fullScript | ssh -i $SSH_KEY $AWS_HOST "bash"

Write-Host ""
Write-Host "Deploy concluido! Acesse: http://3.238.162.190" -ForegroundColor Green
Write-Host ""
Write-Host "Para ver os logs:" -ForegroundColor Yellow
Write-Host "  ssh -i $SSH_KEY $AWS_HOST 'cd ~/RBF-formuladobolso && docker-compose -f docker-compose.prod.yml logs -f'" -ForegroundColor Gray

