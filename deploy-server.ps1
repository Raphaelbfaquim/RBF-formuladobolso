# Deploy no servidor AWS usando imagens do Docker Hub
# Uso: .\deploy-server.ps1 [api|front|marketing|all]

param([string]$service = "all")

$ErrorActionPreference = "Stop"
$service = $service.ToLower()
if ($service -eq "frontend") { $service = "front" }

if ($service -notin @("api", "front", "marketing", "all")) {
    Write-Host "Uso: .\deploy-server.ps1 [api|front|marketing|all]" -ForegroundColor Yellow
    exit 1
}

Write-Host "Deploy no servidor AWS" -ForegroundColor Cyan
Write-Host "Servico: $service" -ForegroundColor Cyan
Write-Host ""

$AWS_HOST = "ubuntu@3.238.162.190"
$SSH_KEY = "$env:USERPROFILE\.ssh\LightsailDefaultKey-us-east-1.pem"
$DOCKER_USERNAME = "faquim"
$IMAGE_TAG = "latest"

if (-not (Test-Path $SSH_KEY)) {
    Write-Host "SSH key nao encontrada: $SSH_KEY" -ForegroundColor Red
    exit 1
}

Write-Host "Conectando no servidor..." -ForegroundColor Yellow

# Usar o script bash que ja existe
$scriptPath = "scripts\deploy-aws-dockerhub.sh"

if (-not (Test-Path $scriptPath)) {
    Write-Host "Script nao encontrado: $scriptPath" -ForegroundColor Red
    exit 1
}

# Enviar script para servidor
& scp -i $SSH_KEY -o StrictHostKeyChecking=no $scriptPath "${AWS_HOST}:~/deploy.sh"

if ($LASTEXITCODE -ne 0) {
    Write-Host "Erro ao enviar script" -ForegroundColor Red
    exit 1
}

# Executar git pull primeiro
Write-Host "Atualizando codigo no servidor..." -ForegroundColor Yellow
& ssh -i $SSH_KEY -o StrictHostKeyChecking=no $AWS_HOST "cd ~/RBF-formuladobolso && git fetch origin && git reset --hard origin/main && git clean -fd"

# Enviar docker-compose.prod.yml e nginx.conf DEPOIS do git pull
Write-Host "Enviando arquivos atualizados para o servidor..." -ForegroundColor Yellow
& scp -i $SSH_KEY -o StrictHostKeyChecking=no "docker-compose.prod.yml" "${AWS_HOST}:~/RBF-formuladobolso/docker-compose.prod.yml"
& scp -i $SSH_KEY -o StrictHostKeyChecking=no "nginx\nginx.conf" "${AWS_HOST}:~/RBF-formuladobolso/nginx/nginx.conf"

# Executar script de deploy no servidor com variaveis de ambiente
$secretKey = -join ((48..57) + (65..90) + (97..122) | Get-Random -Count 32 | ForEach-Object {[char]$_})
$envVars = "DOCKER_USERNAME=$DOCKER_USERNAME SERVICE_TYPE=$service IMAGE_TAG=$IMAGE_TAG SECRET_KEY=$secretKey CORS_ORIGINS=http://3.238.162.190,http://localhost:3000"
$remoteCmd = "export $envVars; bash ~/deploy.sh; rm -f ~/deploy.sh"

& ssh -i $SSH_KEY -o StrictHostKeyChecking=no -o ConnectTimeout=30 $AWS_HOST $remoteCmd

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "=== TESTANDO DEPLOY ===" -ForegroundColor Cyan
    Write-Host ""
    
    # Aguardar um pouco mais para garantir que tudo iniciou
    Write-Host "Aguardando servicos estabilizarem..." -ForegroundColor Yellow
    Start-Sleep -Seconds 10
    
    # Teste 1: Status dos containers
    Write-Host "1. Verificando status dos containers..." -ForegroundColor Yellow
    $containerStatus = & ssh -i $SSH_KEY -o StrictHostKeyChecking=no $AWS_HOST "cd ~/RBF-formuladobolso && docker-compose -f docker-compose.prod.yml ps"
    Write-Host $containerStatus
    Write-Host ""
    
    # Verificar especificamente o marketing
    Write-Host "1.1. Verificando container do Marketing..." -ForegroundColor Yellow
    $marketingStatus = & ssh -i $SSH_KEY -o StrictHostKeyChecking=no $AWS_HOST "docker ps | grep marketing || echo 'Marketing container nao encontrado'"
    Write-Host $marketingStatus
    if ($marketingStatus -match "marketing.*Up") {
        Write-Host "   Marketing container esta rodando" -ForegroundColor Green
    } else {
        Write-Host "   Marketing container NAO esta rodando!" -ForegroundColor Red
        Write-Host "   Tentando iniciar marketing..." -ForegroundColor Yellow
        & ssh -i $SSH_KEY -o StrictHostKeyChecking=no $AWS_HOST "cd ~/RBF-formuladobolso && docker-compose -f docker-compose.prod.yml up -d marketing"
        Start-Sleep -Seconds 5
    }
    Write-Host ""
    
    # Teste 2: API Health Check (localmente no servidor)
    Write-Host "2. Testando API (health check)..." -ForegroundColor Yellow
    $healthTest = & ssh -i $SSH_KEY -o StrictHostKeyChecking=no $AWS_HOST "curl -s http://localhost:8000/health 2>&1"
    if ($healthTest -match "ok|healthy|status") {
        Write-Host "   API esta respondendo: $healthTest" -ForegroundColor Green
    } else {
        Write-Host "   API nao esta respondendo corretamente" -ForegroundColor Red
        Write-Host "   Resposta: $healthTest" -ForegroundColor Gray
    }
    Write-Host ""
    
    # Teste 3: API externamente
    Write-Host "3. Testando API externamente (http://3.238.162.190:8000/health)..." -ForegroundColor Yellow
    try {
        $apiResponse = Invoke-WebRequest -Uri "http://3.238.162.190:8000/health" -TimeoutSec 10 -UseBasicParsing -ErrorAction Stop
        Write-Host "   API esta acessivel externamente! Status: $($apiResponse.StatusCode)" -ForegroundColor Green
    } catch {
        Write-Host "   API nao esta acessivel externamente: $($_.Exception.Message)" -ForegroundColor Red
    }
    Write-Host ""
    
    # Teste 4: Marketing (página inicial)
    Write-Host "4. Testando Marketing - Pagina Inicial (http://3.238.162.190/)..." -ForegroundColor Yellow
    try {
        $marketingResponse = Invoke-WebRequest -Uri "http://3.238.162.190/" -TimeoutSec 10 -UseBasicParsing -ErrorAction Stop
        if ($marketingResponse.StatusCode -eq 200) {
            Write-Host "   Marketing esta acessivel! Status: $($marketingResponse.StatusCode)" -ForegroundColor Green
        } else {
            Write-Host "   Marketing retornou status: $($marketingResponse.StatusCode)" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "   Marketing nao esta acessivel: $($_.Exception.Message)" -ForegroundColor Red
    }
    Write-Host ""
    
    # Teste 5: Frontend - Dashboard (/app)
    Write-Host "5. Testando Frontend - Dashboard (http://3.238.162.190/app)..." -ForegroundColor Yellow
    try {
        $appResponse = Invoke-WebRequest -Uri "http://3.238.162.190/app" -TimeoutSec 10 -UseBasicParsing -ErrorAction Stop
        if ($appResponse.StatusCode -eq 200) {
            Write-Host "   Dashboard esta acessivel! Status: $($appResponse.StatusCode)" -ForegroundColor Green
        } else {
            Write-Host "   Dashboard retornou status: $($appResponse.StatusCode)" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "   Dashboard nao esta acessivel: $($_.Exception.Message)" -ForegroundColor Red
    }
    Write-Host ""
    
    # Teste 6: Frontend - Login (/app/login)
    Write-Host "6. Testando Frontend - Login (http://3.238.162.190/app/login)..." -ForegroundColor Yellow
    try {
        $loginResponse = Invoke-WebRequest -Uri "http://3.238.162.190/app/login" -TimeoutSec 10 -UseBasicParsing -ErrorAction Stop
        if ($loginResponse.StatusCode -eq 200) {
            Write-Host "   Pagina de Login esta acessivel! Status: $($loginResponse.StatusCode)" -ForegroundColor Green
        } else {
            Write-Host "   Pagina de Login retornou status: $($loginResponse.StatusCode)" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "   Pagina de Login nao esta acessivel: $($_.Exception.Message)" -ForegroundColor Red
    }
    Write-Host ""
    
    # Teste 7: Frontend - Register (/app/register)
    Write-Host "7. Testando Frontend - Register (http://3.238.162.190/app/register)..." -ForegroundColor Yellow
    try {
        $registerResponse = Invoke-WebRequest -Uri "http://3.238.162.190/app/register" -TimeoutSec 10 -UseBasicParsing -ErrorAction Stop
        if ($registerResponse.StatusCode -eq 200) {
            Write-Host "   Pagina de Registro esta acessivel! Status: $($registerResponse.StatusCode)" -ForegroundColor Green
        } else {
            Write-Host "   Pagina de Registro retornou status: $($registerResponse.StatusCode)" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "   Pagina de Registro nao esta acessivel: $($_.Exception.Message)" -ForegroundColor Red
    }
    Write-Host ""
    
    # Teste 8: Marketing - Features (/features)
    Write-Host "8. Testando Marketing - Features (http://3.238.162.190/features)..." -ForegroundColor Yellow
    try {
        $featuresResponse = Invoke-WebRequest -Uri "http://3.238.162.190/features" -TimeoutSec 10 -UseBasicParsing -ErrorAction Stop
        if ($featuresResponse.StatusCode -eq 200) {
            Write-Host "   Pagina Features esta acessivel! Status: $($featuresResponse.StatusCode)" -ForegroundColor Green
        } else {
            Write-Host "   Pagina Features retornou status: $($featuresResponse.StatusCode)" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "   Pagina Features nao esta acessivel: $($_.Exception.Message)" -ForegroundColor Red
    }
    Write-Host ""
    
    # Teste 9: Marketing - Pricing (/pricing)
    Write-Host "9. Testando Marketing - Pricing (http://3.238.162.190/pricing)..." -ForegroundColor Yellow
    try {
        $pricingResponse = Invoke-WebRequest -Uri "http://3.238.162.190/pricing" -TimeoutSec 10 -UseBasicParsing -ErrorAction Stop
        if ($pricingResponse.StatusCode -eq 200) {
            Write-Host "   Pagina Pricing esta acessivel! Status: $($pricingResponse.StatusCode)" -ForegroundColor Green
        } else {
            Write-Host "   Pagina Pricing retornou status: $($pricingResponse.StatusCode)" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "   Pagina Pricing nao esta acessivel: $($_.Exception.Message)" -ForegroundColor Red
    }
    Write-Host ""
    
    # Teste 10: API Docs
    Write-Host "10. Testando API Docs (http://3.238.162.190:8000/docs)..." -ForegroundColor Yellow
    try {
        $docsResponse = Invoke-WebRequest -Uri "http://3.238.162.190:8000/docs" -TimeoutSec 10 -UseBasicParsing -ErrorAction Stop
        if ($docsResponse.StatusCode -eq 200) {
            Write-Host "   API Docs esta acessivel! Status: $($docsResponse.StatusCode)" -ForegroundColor Green
        } else {
            Write-Host "   API Docs retornou status: $($docsResponse.StatusCode)" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "   API Docs nao esta acessivel: $($_.Exception.Message)" -ForegroundColor Red
    }
    Write-Host ""
    
    Write-Host "=== DEPLOY CONCLUIDO ===" -ForegroundColor Green
    Write-Host ""
    Write-Host "Acesse:" -ForegroundColor Cyan
    Write-Host "  - Marketing: http://3.238.162.190" -ForegroundColor Cyan
    Write-Host "  - Dashboard: http://3.238.162.190/app" -ForegroundColor Cyan
    Write-Host "  - Login: http://3.238.162.190/app/login" -ForegroundColor Cyan
    Write-Host "  - Register: http://3.238.162.190/app/register" -ForegroundColor Cyan
    Write-Host "  - API: http://3.238.162.190:8000" -ForegroundColor Cyan
    Write-Host "  - API Docs: http://3.238.162.190:8000/docs" -ForegroundColor Cyan
} else {
    Write-Host "Deploy falhou!" -ForegroundColor Red
    exit 1
}
