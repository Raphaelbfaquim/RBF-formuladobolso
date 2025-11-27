#!/bin/bash
# Script para buildar imagens localmente e fazer push para Docker Hub

set -e

# Cores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Variáveis
DOCKER_USERNAME="${DOCKER_USERNAME:-raphaelbfaquim}"  # Seu username do Docker Hub
IMAGE_TAG="${IMAGE_TAG:-latest}"
AWS_IP="${AWS_IP:-3.238.162.190}"

echo -e "${BLUE}🐳 Buildando e fazendo push das imagens Docker...${NC}\n"

# Verificar se está logado no Docker Hub
if ! docker info | grep -q "Username"; then
    echo -e "${YELLOW}⚠️  Você precisa fazer login no Docker Hub primeiro:${NC}"
    echo "   docker login"
    exit 1
fi

# Build e push da API
echo -e "${GREEN}📦 Buildando imagem da API...${NC}"
docker build -t ${DOCKER_USERNAME}/formulado-api:${IMAGE_TAG} \
    -f back/docker/Dockerfile \
    --build-arg NEXT_PUBLIC_API_URL=http://${AWS_IP}:8000 \
    back/

echo -e "${GREEN}📤 Fazendo push da API...${NC}"
docker push ${DOCKER_USERNAME}/formulado-api:${IMAGE_TAG}

# Build e push do Frontend
echo -e "${GREEN}📦 Buildando imagem do Frontend...${NC}"
docker build -t ${DOCKER_USERNAME}/formulado-frontend:${IMAGE_TAG} \
    -f front/Dockerfile \
    --build-arg NEXT_PUBLIC_API_URL=http://${AWS_IP}:8000 \
    front/

echo -e "${GREEN}📤 Fazendo push do Frontend...${NC}"
docker push ${DOCKER_USERNAME}/formulado-frontend:${IMAGE_TAG}

echo -e "\n${GREEN}✅ Imagens buildadas e enviadas para Docker Hub!${NC}"
echo -e "${BLUE}📋 Imagens:${NC}"
echo "   - ${DOCKER_USERNAME}/formulado-api:${IMAGE_TAG}"
echo "   - ${DOCKER_USERNAME}/formulado-frontend:${IMAGE_TAG}"
echo ""
echo -e "${YELLOW}💡 Próximo passo: Execute 'make deploy-aws-images' para fazer deploy na AWS${NC}"

