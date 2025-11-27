#!/bin/bash
# Script para executhttp://localhost:3000/bills                                                                                             em ar o sistema completo (Backend + Frontend)

echo "🚀 Iniciando Sistema FormuladoBolso"
echo ""

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Verificar Node.js
if ! command -v node &> /dev/null; then
    echo -e "${YELLOW}⚠️  Node.js não encontrado${NC}"
    echo ""
    echo "Instalando Node.js via NVM (recomendado)..."
    
    # Instalar NVM se não existir
    if [ ! -d "$HOME/.nvm" ]; then
        echo "Instalando NVM..."
        curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
        export NVM_DIR="$HOME/.nvm"
        [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
    else
        export NVM_DIR="$HOME/.nvm"
        [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
    fi
    
    # Instalar Node.js LTS
    nvm install --lts
    nvm use --lts
fi

# Verificar se Node.js está disponível agora
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Erro: Node.js ainda não está disponível${NC}"
    echo ""
    echo "Por favor, instale manualmente:"
    echo "  sudo apt update"
    echo "  sudo apt install nodejs npm"
    exit 1
fi

echo -e "${GREEN}✅ Node.js $(node --version) encontrado${NC}"
echo -e "${GREEN}✅ npm $(npm --version) encontrado${NC}"
echo ""

# Verificar Backend
echo "🔍 Verificando Backend..."
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Backend rodando em http://localhost:8000${NC}"
else
    echo -e "${YELLOW}⚠️  Backend não está rodando. Iniciando...${NC}"
    cd back
    source ../venv/bin/activate
    nohup uvicorn src.presentation.api.main:app --host 0.0.0.0 --port 8000 --reload > /tmp/backend.log 2>&1 &
    echo $! > /tmp/backend.pid
    sleep 3
    cd ..
    echo -e "${GREEN}✅ Backend iniciado (PID: $(cat /tmp/backend.pid))${NC}"
fi
echo ""

# Instalar dependências do frontend se necessário
cd front
if [ ! -d "node_modules" ]; then
    echo "📦 Instalando dependências do frontend..."
    npm install
fi

# Limpar cache
echo "🧹 Limpando cache..."
rm -rf .next node_modules/.cache .turbo

# Iniciar frontend
echo ""
echo -e "${GREEN}🚀 Iniciando Frontend...${NC}"
echo ""
echo "📊 URLs:"
echo "   Frontend: http://localhost:3000"
echo "   Backend:  http://localhost:8000"
echo "   Login:    http://localhost:3000/login"
echo "   Dashboard: http://localhost:3000/dashboard"
echo ""
echo "Pressione Ctrl+C para parar o servidor"
echo ""

npm run dev

