#!/bin/bash
# Script para fazer deploy na AWS usando imagens do Docker Hub
# Não precisa buildar na instância, apenas faz pull e roda

set -e

# Cores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Variáveis (configure no .env ou exporte)
AWS_HOST="${AWS_HOST:-ubuntu@3.238.162.190}"
DOCKER_USERNAME="${DOCKER_USERNAME:-raphaelbfaquim}"
IMAGE_TAG="${IMAGE_TAG:-latest}"

echo -e "${BLUE}🚀 Deploy na AWS usando imagens do Docker Hub...${NC}\n"

# Verificar se SSH key está configurada
if [ -z "$AWS_SSH_KEY" ] && [ ! -f "$HOME/.ssh/LightsailDefaultKey-us-east-1.pem" ]; then
    echo -e "${RED}❌ SSH key não encontrada!${NC}"
    echo "   Configure AWS_SSH_KEY ou coloque a key em ~/.ssh/LightsailDefaultKey-us-east-1.pem"
    exit 1
fi

SSH_KEY="${AWS_SSH_KEY:-$HOME/.ssh/LightsailDefaultKey-us-east-1.pem}"

echo -e "${GREEN}📡 Conectando na instância AWS...${NC}"

# Comandos para executar na instância
ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$AWS_HOST" << EOF
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
echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin || {
  echo "⚠️  Login falhou. Você precisa configurar DOCKER_PASSWORD"
  exit 1
}

echo "📥 Fazendo pull das imagens..."
docker pull ${DOCKER_USERNAME}/formulado-api:${IMAGE_TAG}
docker pull ${DOCKER_USERNAME}/formulado-frontend:${IMAGE_TAG}

echo "🛑 Parando containers antigos..."
docker-compose -f docker-compose.prod.yml down || true

echo "🚀 Iniciando containers com imagens do Docker Hub..."
export DOCKER_USERNAME=${DOCKER_USERNAME}
export IMAGE_TAG=${IMAGE_TAG}
docker-compose -f docker-compose.prod.yml up -d

echo "⏳ Aguardando serviços iniciarem..."
sleep 30

# Verificar PostgreSQL
echo "🔍 Verificando PostgreSQL..."
for i in {1..30}; do
  if docker-compose -f docker-compose.prod.yml exec -T postgres pg_isready -U formulado_user > /dev/null 2>&1; then
    echo "✅ PostgreSQL está pronto!"
    break
  fi
  echo "Tentativa \$i/30..."
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
EOF

echo -e "\n${GREEN}✅ Deploy finalizado!${NC}"
echo -e "${BLUE}🌐 Acesse: http://${AWS_HOST#*@}${NC}"


