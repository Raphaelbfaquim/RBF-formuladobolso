# Deploy DIRETO da maquina para AWS (SEM Docker Hub)
# Uso: .\scripts\deploy-direto-aws.ps1 [api|front|all]
#      api   - Deploy apenas da API
#      front - Deploy apenas do Frontend
#      all   - Deploy de ambos (padrao)

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
    Write-Host "Uso: .\scripts\deploy-direto-aws.ps1 [api|front|all]" -ForegroundColor Yellow
    exit 1
}

Write-Host "Deploy Direto para AWS (sem Docker Hub)" -ForegroundColor Cyan
Write-Host "Servico: $service" -ForegroundColor Cyan
Write-Host ""

# Verificar Docker
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "Docker nao encontrado!" -ForegroundColor Red
    exit 1
}

# Configuracoes
$AWS_HOST = "ubuntu@3.238.162.190"
$SSH_KEY = "$env:USERPROFILE\.ssh\LightsailDefaultKey-us-east-1.pem"

# Verificar SSH key
if (-not (Test-Path $SSH_KEY)) {
    Write-Host "Chave SSH nao encontrada: $SSH_KEY" -ForegroundColor Red
    exit 1
}

# Build das imagens localmente
$buildApi = ($service -eq "api" -or $service -eq "all")
$buildFront = ($service -eq "front" -or $service -eq "all")

if ($buildApi) {
    Write-Host "Buildando API..." -ForegroundColor Yellow
    docker build -t formulado-api:latest -f back/docker/Dockerfile back/
    if ($LASTEXITCODE -ne 0) { exit 1 }
}

if ($buildFront) {
    Write-Host "Buildando Frontend..." -ForegroundColor Yellow
    docker build -t formulado-frontend:latest -f front/Dockerfile --build-arg NEXT_PUBLIC_API_URL=http://3.238.162.190 front/
    if ($LASTEXITCODE -ne 0) { exit 1 }
}

# Salvar imagens em arquivos
Write-Host "Salvando imagens..." -ForegroundColor Cyan
$imagesToSend = @()
if ($buildApi) {
    docker save formulado-api:latest -o api-image.tar
    $imagesToSend += "api-image.tar"
}
if ($buildFront) {
    docker save formulado-frontend:latest -o frontend-image.tar
    $imagesToSend += "frontend-image.tar"
}

# Enviar imagens para AWS
Write-Host "Enviando imagens para AWS..." -ForegroundColor Cyan
$scpFiles = $imagesToSend -join " "
scp -i $SSH_KEY $scpFiles ${AWS_HOST}:~/

# Construir script bash dinamicamente
$scriptLines = @()
$scriptLines += "cd ~/RBF-formuladobolso || { git clone https://github.com/Raphaelbfaquim/RBF-formuladobolso.git && cd RBF-formuladobolso; }"
$scriptLines += "git pull origin main"
$scriptLines += ""
$scriptLines += "# Carregar imagens"
$scriptLines += "echo 'Carregando imagens...'"

if ($buildApi) {
    $scriptLines += "docker load -i ~/api-image.tar"
    $scriptLines += "docker tag formulado-api:latest efaquim/formulado-api:latest"
}

if ($buildFront) {
    $scriptLines += "docker load -i ~/frontend-image.tar"
    $scriptLines += "docker tag formulado-frontend:latest efaquim/formulado-frontend:latest"
}

$scriptLines += ""
$scriptLines += "# Parar containers antigos (apenas os que serao atualizados)"
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
$scriptLines += "# Iniciar containers"
$scriptLines += "export DOCKER_USERNAME=efaquim"
$scriptLines += "export IMAGE_TAG=latest"

if ($service -eq "api") {
    $scriptLines += "docker-compose -f docker-compose.prod.yml up -d api"
} elseif ($service -eq "front") {
    $scriptLines += "docker-compose -f docker-compose.prod.yml up -d frontend nginx"
} else {
    $scriptLines += "docker-compose -f docker-compose.prod.yml up -d"
}

$scriptLines += ""
$scriptLines += "# Limpar arquivos temporarios"
if ($buildApi) {
    $scriptLines += "rm -f ~/api-image.tar"
}
if ($buildFront) {
    $scriptLines += "rm -f ~/frontend-image.tar"
}

$scriptLines += ""
$scriptLines += "echo 'Deploy concluido!'"

$deployScript = $scriptLines -join "`n"

# Executar script na AWS
Write-Host "Executando deploy na AWS..." -ForegroundColor Cyan
# Passar o serviço como variável de ambiente
$fullScript = "export SERVICE_TYPE=$service`n$deployScript"
$fullScript | ssh -i $SSH_KEY $AWS_HOST "bash"

# Limpar arquivos locais
if ($buildApi) {
    Remove-Item api-image.tar -ErrorAction SilentlyContinue
}
if ($buildFront) {
    Remove-Item frontend-image.tar -ErrorAction SilentlyContinue
}

Write-Host ""
Write-Host "Deploy concluido! Acesse: http://3.238.162.190" -ForegroundColor Green

