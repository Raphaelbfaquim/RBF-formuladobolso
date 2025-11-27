#!/bin/bash

# Script de deploy para Oracle Cloud
# Automatiza o processo de deploy na instância Oracle Cloud
# Para Oracle Linux 9 com usuário 'opc'

set -e

echo "🚀 Deploy do FormuladoBolso na Oracle Cloud"
echo "📋 Sistema: Oracle Linux 9"
echo "👤 Usuário: opc"
echo ""

# Cores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Verificar se está na raiz do projeto
if [ ! -d "back" ] || [ ! -d "front" ]; then
    echo "${RED}❌ Erro: Execute este script da raiz do projeto${NC}"
    exit 1
fi

# Verificar se Docker está instalado
if ! command -v docker &> /dev/null; then
    echo "${YELLOW}⚠️  Docker não encontrado. Instalando...${NC}"
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
    echo "${GREEN}✅ Docker instalado!${NC}"
    echo "${YELLOW}⚠️  Você precisa fazer logout e login novamente para usar Docker${NC}"
    exit 0
fi

# Verificar se Docker Compose está instalado
if ! command -v docker-compose &> /dev/null; then
    echo "${YELLOW}⚠️  Docker Compose não encontrado. Instalando...${NC}"
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    echo "${GREEN}✅ Docker Compose instalado!${NC}"
fi

# Verificar se arquivo .env existe
if [ ! -f "back/.env" ]; then
    echo "${YELLOW}⚠️  Arquivo .env não encontrado. Criando a partir do exemplo...${NC}"
    if [ -f "back/env.example" ]; then
        cp back/env.example back/.env
        echo "${GREEN}✅ Arquivo .env criado!${NC}"
        echo "${YELLOW}⚠️  IMPORTANTE: Edite o arquivo back/.env com suas configurações antes de continuar${NC}"
        echo ""
        read -p "Pressione Enter após editar o .env..."
    else
        echo "${RED}❌ Arquivo env.example não encontrado!${NC}"
        exit 1
    fi
fi

# Navegar para pasta back
cd back

echo ""
echo "${BLUE}📦 Parando containers existentes...${NC}"
docker-compose down || true

echo ""
echo "${BLUE}🔨 Construindo e iniciando containers...${NC}"
docker-compose up -d --build

echo ""
echo "${BLUE}⏳ Aguardando serviços iniciarem...${NC}"
sleep 10

echo ""
echo "${BLUE}📊 Verificando status dos containers...${NC}"
docker-compose ps

echo ""
echo "${BLUE}🔄 Executando migrações do banco de dados...${NC}"
# Aguardar PostgreSQL estar pronto
echo "Aguardando PostgreSQL..."
for i in {1..30}; do
    if docker-compose exec -T postgres pg_isready -U formulado_user > /dev/null 2>&1; then
        echo "${GREEN}✅ PostgreSQL está pronto!${NC}"
        break
    fi
    echo "Tentativa $i/30..."
    sleep 2
done

# Executar migrações
docker-compose exec -T api alembic upgrade head || {
    echo "${YELLOW}⚠️  Erro ao executar migrações. Verificando se banco precisa ser inicializado...${NC}"
    # Tentar inicializar banco se necessário
    docker-compose exec -T api python scripts/init_db.py || true
    docker-compose exec -T api alembic upgrade head || true
}

echo ""
echo "${GREEN}✅ Deploy concluído!${NC}"
echo ""

# Verificar saúde da API
echo "${BLUE}🏥 Verificando saúde da API...${NC}"
sleep 5

if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "${GREEN}✅ API está respondendo!${NC}"
else
    echo "${YELLOW}⚠️  API ainda não está respondendo. Verifique os logs:${NC}"
    echo "   docker-compose logs -f api"
fi

echo ""
echo "${BLUE}📋 Comandos úteis:${NC}"
echo "   Ver logs:        docker-compose logs -f"
echo "   Parar serviços:  docker-compose down"
echo "   Reiniciar:       docker-compose restart"
echo "   Status:          docker-compose ps"
echo ""
echo "${GREEN}🎉 Deploy finalizado!${NC}"

