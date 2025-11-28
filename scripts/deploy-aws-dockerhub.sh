#!/bin/bash
set -e

echo "📥 Verificando diretório..."
cd ~/RBF-formuladobolso || {
  echo "📦 Clonando repositório..."
  cd ~
  git clone https://github.com/Raphaelbfaquim/RBF-formuladobolso.git
  cd RBF-formuladobolso
}

# Nota: O git pull já foi feito pelo script PowerShell antes de executar este script
# Os arquivos docker-compose.prod.yml e nginx.conf já foram enviados via SCP

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

# Determinar quais imagens fazer pull
PULL_API=false
PULL_FRONT=false
PULL_MARKETING=false

if [ "$SERVICE_TYPE" = "api" ] || [ "$SERVICE_TYPE" = "all" ]; then
  PULL_API=true
fi

if [ "$SERVICE_TYPE" = "front" ] || [ "$SERVICE_TYPE" = "all" ]; then
  PULL_FRONT=true
fi

if [ "$SERVICE_TYPE" = "marketing" ] || [ "$SERVICE_TYPE" = "all" ]; then
  PULL_MARKETING=true
fi

if [ "$PULL_API" = "true" ]; then
  docker pull ${DOCKER_USERNAME}/formulado-api:${IMAGE_TAG} || {
    echo "❌ Erro ao fazer pull da API"
    exit 1
  }
  echo "✅ API baixada com sucesso"
fi

if [ "$PULL_FRONT" = "true" ]; then
  if docker pull ${DOCKER_USERNAME}/formulado-frontend:${IMAGE_TAG} 2>/dev/null; then
    echo "✅ Frontend baixado com sucesso"
  else
    echo "⚠️  Frontend não encontrado no Docker Hub"
    PULL_FRONT=false
  fi
fi

if [ "$PULL_MARKETING" = "true" ]; then
  echo "📥 Tentando baixar imagem do Marketing..."
  if docker pull ${DOCKER_USERNAME}/formulado-marketing:${IMAGE_TAG} 2>&1; then
    echo "✅ Marketing baixado com sucesso"
  else
    echo "⚠️  Marketing não encontrado no Docker Hub"
    echo "   Tentando novamente com tag latest..."
    if docker pull ${DOCKER_USERNAME}/formulado-marketing:latest 2>&1; then
      echo "✅ Marketing baixado com sucesso (usando latest)"
    else
      echo "❌ Marketing não pode ser baixado"
      PULL_MARKETING=false
    fi
  fi
fi

echo "🛑 Parando containers antigos..."

# Parar apenas os containers que serão atualizados
if [ "$SERVICE_TYPE" = "api" ]; then
  docker-compose -f docker-compose.prod.yml stop api || true
  docker-compose -f docker-compose.prod.yml rm -f api || true
elif [ "$SERVICE_TYPE" = "front" ]; then
  docker-compose -f docker-compose.prod.yml stop frontend nginx || true
  docker-compose -f docker-compose.prod.yml rm -f frontend nginx || true
elif [ "$SERVICE_TYPE" = "marketing" ]; then
  docker-compose -f docker-compose.prod.yml stop marketing nginx || true
  docker-compose -f docker-compose.prod.yml rm -f marketing nginx || true
else
  docker-compose -f docker-compose.prod.yml down || true
fi

echo "🚀 Iniciando containers com imagens do Docker Hub..."
export DOCKER_USERNAME=${DOCKER_USERNAME}
export IMAGE_TAG=${IMAGE_TAG}

# Verificar se docker-compose.prod.yml tem o serviço marketing
if grep -q "marketing:" docker-compose.prod.yml; then
  echo "✅ Serviço marketing encontrado no docker-compose.prod.yml"
else
  echo "⚠️  Serviço marketing NÃO encontrado no docker-compose.prod.yml"
  echo "   Atualizando código do repositório..."
  git pull origin main || true
  if grep -q "marketing:" docker-compose.prod.yml; then
    echo "✅ Serviço marketing encontrado após atualização"
  else
    echo "❌ Serviço marketing ainda não encontrado. Verifique o arquivo docker-compose.prod.yml"
  fi
fi
# Gerar SECRET_KEY se nao existir
if [ -z "$SECRET_KEY" ]; then
  export SECRET_KEY=$(openssl rand -hex 32 2>/dev/null || echo "dev-secret-key-change-in-production-$(date +%s)")
fi
# Configurar CORS_ORIGINS se nao existir
if [ -z "$CORS_ORIGINS" ]; then
  export CORS_ORIGINS="http://3.238.162.190,http://localhost:3000"
fi

# Iniciar containers baseado no serviço
if [ "$SERVICE_TYPE" = "api" ]; then
  docker-compose -f docker-compose.prod.yml up -d api
elif [ "$SERVICE_TYPE" = "front" ]; then
  if [ "$PULL_FRONT" = "true" ]; then
    docker-compose -f docker-compose.prod.yml up -d frontend nginx
  else
    echo "⚠️  Frontend não disponível, iniciando apenas nginx (se existir)"
    docker-compose -f docker-compose.prod.yml up -d nginx || true
  fi
elif [ "$SERVICE_TYPE" = "marketing" ]; then
  if [ "$PULL_MARKETING" = "true" ]; then
    docker-compose -f docker-compose.prod.yml up -d marketing nginx
  else
    echo "⚠️  Marketing não disponível, iniciando apenas nginx (se existir)"
    docker-compose -f docker-compose.prod.yml up -d nginx || true
  fi
else
  echo "🚀 Iniciando todos os containers..."
  if [ "$PULL_FRONT" = "true" ] && [ "$PULL_MARKETING" = "true" ]; then
    echo "✅ Iniciando todos os serviços (frontend e marketing disponíveis)"
    docker-compose -f docker-compose.prod.yml up -d
  elif [ "$PULL_FRONT" = "true" ]; then
    echo "⚠️  Frontend disponível, mas marketing não. Iniciando sem marketing..."
    docker-compose -f docker-compose.prod.yml up -d postgres redis api frontend nginx
    # Tentar iniciar marketing mesmo se não foi baixado (para diagnóstico)
    if [ "$PULL_MARKETING" = "false" ]; then
      echo "⚠️  Tentando iniciar marketing (pode falhar se imagem não existir)..."
      docker-compose -f docker-compose.prod.yml up -d marketing 2>&1 || echo "❌ Marketing não pode ser iniciado - imagem não encontrada"
    fi
  elif [ "$PULL_MARKETING" = "true" ]; then
    echo "⚠️  Marketing disponível, mas frontend não. Iniciando sem frontend..."
    docker-compose -f docker-compose.prod.yml up -d postgres redis api marketing nginx
  else
    echo "📦 Iniciando apenas API, PostgreSQL e Redis (sem frontend/marketing/nginx)..."
    docker-compose -f docker-compose.prod.yml up -d postgres redis api
    # Tentar iniciar marketing e frontend para diagnóstico
    echo "⚠️  Tentando iniciar frontend e marketing (podem falhar se imagens não existirem)..."
    docker-compose -f docker-compose.prod.yml up -d frontend marketing nginx 2>&1 || echo "⚠️  Alguns containers não puderam ser iniciados"
  fi
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

# Aguardar API estabilizar
echo "Aguardando API estabilizar..."
sleep 10
for i in {1..10}; do
  if docker ps | grep -q "formulado_api.*Up"; then
    echo "API esta rodando"
    break
  fi
  echo "Aguardando API... ($i/10)"
  sleep 3
done

# Executar migrações
echo "🔄 Executando migrações..."
docker-compose -f docker-compose.prod.yml exec -T api alembic upgrade head 2>&1 || {
  echo "⚠️  Erro ao executar migrações. Tentando novamente..."
  sleep 5
  docker-compose -f docker-compose.prod.yml exec -T api alembic upgrade head 2>&1 || true
}

echo "📊 Status dos containers:"
docker-compose -f docker-compose.prod.yml ps

echo "✅ Deploy concluído!"

