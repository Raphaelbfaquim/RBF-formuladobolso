# Build e Push para Docker Hub
# Uso: .\scripts\build-and-push-dockerhub.ps1 [api|front|all]
#      api   - Build e push apenas da API
#      front - Build e push apenas do Frontend
#      all   - Build e push de ambos (padrao)

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
    Write-Host "Uso: .\scripts\build-and-push-dockerhub.ps1 [api|front|all]" -ForegroundColor Yellow
    exit 1
}

Write-Host "Build e Push para Docker Hub" -ForegroundColor Cyan
Write-Host "Servico: $service" -ForegroundColor Cyan
Write-Host ""

# Verificar Docker
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "Docker nao encontrado!" -ForegroundColor Red
    exit 1
}

# Configuracoes
$DOCKER_USERNAME = if ($env:DOCKER_USERNAME) { $env:DOCKER_USERNAME } else { "faquim" }
$IMAGE_TAG = if ($env:IMAGE_TAG) { $env:IMAGE_TAG } else { "latest" }

# Verificar login no Docker Hub
Write-Host "Verificando login no Docker Hub..." -ForegroundColor Yellow
$dockerLogin = docker info 2>&1 | Select-String "Username"
if (-not $dockerLogin) {
    Write-Host "Fazendo login no Docker Hub..." -ForegroundColor Yellow
    Write-Host "Use o email completo para login: efaquim@gmail.com" -ForegroundColor Cyan
    Write-Host "E o token quando pedir a senha" -ForegroundColor Cyan
    docker login -u "efaquim@gmail.com"
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Erro ao fazer login no Docker Hub!" -ForegroundColor Red
        Write-Host "Tente fazer login manualmente: docker login -u efaquim@gmail.com" -ForegroundColor Yellow
        exit 1
    }
} else {
    Write-Host "Ja esta logado no Docker Hub" -ForegroundColor Green
}

# Build das imagens
$buildApi = ($service -eq "api" -or $service -eq "all")
$buildFront = ($service -eq "front" -or $service -eq "all")

if ($buildApi) {
    Write-Host "`nBuildando API..." -ForegroundColor Yellow
    docker build -t $DOCKER_USERNAME/formulado-api:$IMAGE_TAG -f back/docker/Dockerfile back/
    docker tag $DOCKER_USERNAME/formulado-api:$IMAGE_TAG $DOCKER_USERNAME/formulado-api:latest
    if ($LASTEXITCODE -ne 0) { exit 1 }
    
    Write-Host "Fazendo push da API para Docker Hub..." -ForegroundColor Yellow
    docker push $DOCKER_USERNAME/formulado-api:$IMAGE_TAG
    docker push $DOCKER_USERNAME/formulado-api:latest
    if ($LASTEXITCODE -ne 0) { exit 1 }
    Write-Host "API enviada com sucesso!" -ForegroundColor Green
}

if ($buildFront) {
    Write-Host "`nBuildando Frontend..." -ForegroundColor Yellow
    docker build -t $DOCKER_USERNAME/formulado-frontend:$IMAGE_TAG -f front/Dockerfile --build-arg NEXT_PUBLIC_API_URL=http://3.238.162.190 front/
    docker tag $DOCKER_USERNAME/formulado-frontend:$IMAGE_TAG $DOCKER_USERNAME/formulado-frontend:latest
    if ($LASTEXITCODE -ne 0) { exit 1 }
    
    Write-Host "Fazendo push do Frontend para Docker Hub..." -ForegroundColor Yellow
    docker push $DOCKER_USERNAME/formulado-frontend:$IMAGE_TAG
    docker push $DOCKER_USERNAME/formulado-frontend:latest
    if ($LASTEXITCODE -ne 0) { exit 1 }
    Write-Host "Frontend enviado com sucesso!" -ForegroundColor Green
}

Write-Host ""
Write-Host "Build e push concluidos!" -ForegroundColor Green
Write-Host "Imagens disponiveis em: https://hub.docker.com/r/$DOCKER_USERNAME" -ForegroundColor Cyan

