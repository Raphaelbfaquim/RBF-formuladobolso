# Script PowerShell para fazer deploy na AWS usando imagens do Docker Hub
# Uso: .\scripts\deploy-aws-images.ps1 [api|front|all]
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
    Write-Host "Uso: .\scripts\deploy-aws-images.ps1 [api|front|all]" -ForegroundColor Yellow
    exit 1
}

# Cores
function Write-ColorOutput($ForegroundColor) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    if ($args) {
        Write-Output $args
    }
    $host.UI.RawUI.ForegroundColor = $fc
}

# Variáveis
$AWS_HOST = if ($env:AWS_HOST) { $env:AWS_HOST } else { "ubuntu@3.238.162.190" }
$DOCKER_USERNAME = if ($env:DOCKER_USERNAME) { $env:DOCKER_USERNAME } else { "efaquim" }
$DOCKER_PASSWORD = $env:DOCKER_PASSWORD
$IMAGE_TAG = if ($env:IMAGE_TAG) { $env:IMAGE_TAG } else { "latest" }
$SSH_KEY = if ($env:AWS_SSH_KEY) { $env:AWS_SSH_KEY } else { "$env:USERPROFILE\.ssh\LightsailDefaultKey-us-east-1.pem" }

Write-ColorOutput Cyan "🚀 Deploy na AWS usando imagens do Docker Hub..."
Write-ColorOutput Cyan "Servico: $service`n"

# Verificar SSH key
if (-not (Test-Path $SSH_KEY)) {
    Write-ColorOutput Red "❌ SSH key não encontrada em: $SSH_KEY"
    Write-Output "   Configure AWS_SSH_KEY ou coloque a key no caminho padrão"
    exit 1
}

# Verificar se Docker password foi fornecido
if (-not $DOCKER_PASSWORD) {
    Write-ColorOutput Yellow "⚠️  DOCKER_PASSWORD não configurado"
    Write-Output "   Configure: `$env:DOCKER_PASSWORD = 'sua-senha-docker-hub'"
    Write-Output "   Ou execute: docker login na instância AWS manualmente"
}

Write-ColorOutput Green "📡 Conectando na instância AWS..."

# Construir comandos bash para executar na instância
$bashScript = @'
set -e

echo "📥 Atualizando código..."
cd ~/RBF-formuladobolso || {
  echo "📦 Clonando repositório..."
  cd ~
  git clone https://github.com/Raphaelbfaquim/RBF-formuladobolso.git
  cd RBF-formuladobolso
}

git fetch origin
git reset --hard origin/main
git clean -fd

echo "🐳 Fazendo login no Docker Hub..."
if [ -n "$DOCKER_PASSWORD" ]; then
  echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin || {
    echo "⚠️  Login falhou. Você precisa configurar DOCKER_PASSWORD"
    exit 1
  }
else
  echo "⚠️  DOCKER_PASSWORD não fornecido. Faça login manualmente:"
  echo "   docker login"
fi

echo "📥 Fazendo pull das imagens..."
docker pull ${DOCKER_USERNAME}/formulado-api:${IMAGE_TAG} || {
  echo "❌ Erro ao fazer pull da API"
  exit 1
}

# Tentar fazer pull do frontend (opcional, pode não existir ainda)
if docker pull ${DOCKER_USERNAME}/formulado-frontend:${IMAGE_TAG} 2>/dev/null; then
  echo "✅ Frontend encontrado no Docker Hub"
else
  echo "⚠️  Frontend não encontrado no Docker Hub, será pulado"
  export SKIP_FRONTEND=true
fi

echo "🛑 Parando containers antigos..."
docker-compose -f docker-compose.prod.yml down || true

echo "🚀 Iniciando containers com imagens do Docker Hub..."
export DOCKER_USERNAME=${DOCKER_USERNAME}
export IMAGE_TAG=${IMAGE_TAG}

# Se frontend não existe, iniciar apenas API e dependências (sem nginx)
if [ "$SKIP_FRONTEND" = "true" ]; then
  echo "📦 Iniciando apenas API, PostgreSQL e Redis (sem frontend/nginx)..."
  docker-compose -f docker-compose.prod.yml up -d postgres redis api
else
  docker-compose -f docker-compose.prod.yml up -d
fi

echo "⏳ Aguardando serviços iniciarem..."
sleep 30

# Verificar PostgreSQL
echo "🔍 Verificando PostgreSQL..."
for i in {1..30}; do
  if docker-compose -f docker-compose.prod.yml exec -T postgres pg_isready -U formulado_user > /dev/null 2>&1; then
    echo "✅ PostgreSQL está pronto!"
    break
  fi
  echo "Tentativa $i/30..."
  sleep 2
done

# Executar migrações
echo "🔄 Executando migrações..."
docker-compose -f docker-compose.prod.yml exec -T api alembic upgrade head || {
  echo "⚠️  Erro ao executar migrações. Tentando inicializar banco..."
  docker-compose -f docker-compose.prod.yml exec -T api python scripts/init_db.py || true
  docker-compose -f docker-compose.prod.yml exec -T api alembic upgrade head || true
}

echo "📊 Status dos containers:"
docker-compose -f docker-compose.prod.yml ps

echo "✅ Deploy concluído!"
'@

# Preparar variáveis de ambiente para passar via SSH
$envVars = "DOCKER_USERNAME=$DOCKER_USERNAME"
if ($DOCKER_PASSWORD) {
    $envVars += " DOCKER_PASSWORD=$DOCKER_PASSWORD"
}
$envVars += " IMAGE_TAG=$IMAGE_TAG"

# Executar script via SSH com variáveis de ambiente
$bashScript | ssh -i $SSH_KEY -o StrictHostKeyChecking=no $AWS_HOST "$envVars bash"

if ($LASTEXITCODE -eq 0) {
    Write-Output ""
    Write-ColorOutput Green "✅ Deploy finalizado!"
    $ip = $AWS_HOST -replace ".*@", ""
    Write-ColorOutput Cyan "🌐 Acesse: http://$ip"
} else {
    Write-ColorOutput Red "❌ Deploy falhou!"
    exit 1
}


