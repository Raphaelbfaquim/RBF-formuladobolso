# Build e Push para Docker Hub
# Uso: .\deploy-build-push.ps1 [api|front|marketing|all]

param([string]$service = "all")

$ErrorActionPreference = "Stop"
$service = $service.ToLower()
if ($service -eq "frontend") { $service = "front" }

if ($service -notin @("api", "front", "marketing", "all")) {
    Write-Host "Uso: .\deploy-build-push.ps1 [api|front|marketing|all]" -ForegroundColor Yellow
    exit 1
}

Write-Host "Build e Push para Docker Hub" -ForegroundColor Cyan
Write-Host "Servico: $service" -ForegroundColor Cyan
Write-Host ""

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "Docker nao encontrado!" -ForegroundColor Red
    exit 1
}

$DOCKER_USERNAME = "faquim"
$DOCKER_LOGIN_USER = "efaquim@gmail.com"
$IMAGE_TAG = "latest"

Write-Host "Verificando login no Docker Hub..." -ForegroundColor Yellow
$dockerLogin = docker info 2>&1 | Select-String "Username"
if (-not $dockerLogin) {
    Write-Host "Fazendo login no Docker Hub..." -ForegroundColor Yellow
    Write-Host "Usuario: $DOCKER_LOGIN_USER" -ForegroundColor Cyan
    Write-Host "Use seu token do Docker Hub quando pedir a senha" -ForegroundColor Cyan
    docker login -u "$DOCKER_LOGIN_USER"
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Erro ao fazer login!" -ForegroundColor Red
        Write-Host "Tente fazer login manualmente: docker login -u efaquim@gmail.com" -ForegroundColor Yellow
        exit 1
    }
} else {
    Write-Host "Ja esta logado" -ForegroundColor Green
}

$buildApi = ($service -eq "api" -or $service -eq "all")
$buildFront = ($service -eq "front" -or $service -eq "all")
$buildMarketing = ($service -eq "marketing" -or $service -eq "all")

if ($buildApi) {
    Write-Host "Buildando API..." -ForegroundColor Yellow
    docker build -t ${DOCKER_USERNAME}/formulado-api:${IMAGE_TAG} -f back/docker/Dockerfile back/
    if ($LASTEXITCODE -ne 0) { exit 1 }
    
    docker tag ${DOCKER_USERNAME}/formulado-api:${IMAGE_TAG} ${DOCKER_USERNAME}/formulado-api:latest
    if ($LASTEXITCODE -ne 0) { exit 1 }
    
    Write-Host "Fazendo push da API..." -ForegroundColor Yellow
    docker push ${DOCKER_USERNAME}/formulado-api:${IMAGE_TAG}
    if ($LASTEXITCODE -ne 0) { exit 1 }
    
    docker push ${DOCKER_USERNAME}/formulado-api:latest
    if ($LASTEXITCODE -ne 0) { exit 1 }
    
    Write-Host "API enviada com sucesso!" -ForegroundColor Green
}

if ($buildFront) {
    Write-Host "Buildando Frontend..." -ForegroundColor Yellow
    docker build -t ${DOCKER_USERNAME}/formulado-frontend:${IMAGE_TAG} -f front/Dockerfile --build-arg NEXT_PUBLIC_API_URL=http://3.238.162.190 front/
    if ($LASTEXITCODE -ne 0) { exit 1 }
    
    docker tag ${DOCKER_USERNAME}/formulado-frontend:${IMAGE_TAG} ${DOCKER_USERNAME}/formulado-frontend:latest
    if ($LASTEXITCODE -ne 0) { exit 1 }
    
    Write-Host "Fazendo push do Frontend..." -ForegroundColor Yellow
    docker push ${DOCKER_USERNAME}/formulado-frontend:${IMAGE_TAG}
    if ($LASTEXITCODE -ne 0) { exit 1 }
    
    docker push ${DOCKER_USERNAME}/formulado-frontend:latest
    if ($LASTEXITCODE -ne 0) { exit 1 }
    
    Write-Host "Frontend enviado com sucesso!" -ForegroundColor Green
}

if ($buildMarketing) {
    Write-Host "Buildando Marketing..." -ForegroundColor Yellow
    docker build -t ${DOCKER_USERNAME}/formulado-marketing:${IMAGE_TAG} -f sites/formula-bolso/Dockerfile sites/formula-bolso/
    if ($LASTEXITCODE -ne 0) { exit 1 }
    
    docker tag ${DOCKER_USERNAME}/formulado-marketing:${IMAGE_TAG} ${DOCKER_USERNAME}/formulado-marketing:latest
    if ($LASTEXITCODE -ne 0) { exit 1 }
    
    Write-Host "Fazendo push do Marketing..." -ForegroundColor Yellow
    docker push ${DOCKER_USERNAME}/formulado-marketing:${IMAGE_TAG}
    if ($LASTEXITCODE -ne 0) { exit 1 }
    
    docker push ${DOCKER_USERNAME}/formulado-marketing:latest
    if ($LASTEXITCODE -ne 0) { exit 1 }
    
    Write-Host "Marketing enviado com sucesso!" -ForegroundColor Green
}

Write-Host ""
Write-Host "Build e push concluidos!" -ForegroundColor Green

