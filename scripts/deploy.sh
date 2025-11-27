#!/bin/bash

# Script de deploy para FormuladoBolso
# Deploy automático em Vercel (frontend) e Render (backend)

set -e

echo "🚀 Iniciando deploy do FormuladoBolso..."
echo ""

# Cores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Verificar se está na raiz do projeto
if [ ! -d "back" ] || [ ! -d "front" ]; then
    echo "❌ Erro: Execute este script da raiz do projeto"
    exit 1
fi

# Função para verificar se comando existe
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Verificar dependências
echo "📋 Verificando dependências..."

if ! command_exists vercel; then
    echo "⚠️  Vercel CLI não encontrado. Instalando..."
    npm install -g vercel
fi

if ! command_exists render; then
    echo "⚠️  Render CLI não encontrado."
    echo "   Instale: https://render.com/docs/cli"
    echo "   Ou faça deploy manual em: https://render.com"
fi

echo ""
echo "🌐 Escolha o que deseja fazer:"
echo "1) Deploy do Frontend (Vercel)"
echo "2) Deploy do Backend (Render)"
echo "3) Deploy completo (Frontend + Backend)"
echo "4) Apenas configurar (sem deploy)"
read -p "Escolha uma opção (1-4): " choice

case $choice in
    1)
        echo ""
        echo "${BLUE}📦 Deploy do Frontend na Vercel...${NC}"
        cd front
        
        # Verificar se já está logado
        if ! vercel whoami >/dev/null 2>&1; then
            echo "🔐 Faça login na Vercel:"
            vercel login
        fi
        
        # Deploy
        echo "🚀 Fazendo deploy..."
        vercel --prod
        
        echo ""
        echo "${GREEN}✅ Frontend deployado com sucesso!${NC}"
        echo "   URL será exibida acima"
        ;;
        
    2)
        echo ""
        echo "${BLUE}📦 Deploy do Backend no Render...${NC}"
        echo ""
        echo "📝 Instruções:"
        echo "1. Acesse: https://render.com"
        echo "2. Crie uma conta (gratuita)"
        echo "3. Clique em 'New +' > 'Web Service'"
        echo "4. Conecte seu repositório GitHub"
        echo "5. Configure:"
        echo "   - Build Command: pip install -r requirements.txt"
        echo "   - Start Command: uvicorn src.presentation.api.main:app --host 0.0.0.0 --port \$PORT"
        echo "   - Environment: Python 3"
        echo "6. Adicione as variáveis de ambiente do arquivo .env"
        echo ""
        echo "Ou use o arquivo render.yaml na pasta back/"
        ;;
        
    3)
        echo ""
        echo "${BLUE}📦 Deploy Completo...${NC}"
        
        # Frontend
        echo ""
        echo "${YELLOW}1/2 - Deploy do Frontend${NC}"
        cd front
        if ! vercel whoami >/dev/null 2>&1; then
            vercel login
        fi
        vercel --prod
        FRONTEND_URL=$(vercel ls | grep -o 'https://[^ ]*' | head -1 || echo "")
        cd ..
        
        echo ""
        echo "${YELLOW}2/2 - Configurar Backend${NC}"
        echo "Configure o backend no Render com a URL do frontend:"
        echo "Frontend URL: $FRONTEND_URL"
        echo ""
        echo "Acesse: https://render.com e configure manualmente"
        ;;
        
    4)
        echo ""
        echo "${BLUE}⚙️  Apenas configurando arquivos...${NC}"
        echo "✅ Arquivos de configuração já criados!"
        echo ""
        echo "📁 Arquivos criados:"
        echo "   • front/vercel.json - Config Vercel"
        echo "   • back/render.yaml - Config Render"
        echo "   • back/Procfile - Comando de start"
        ;;
        
    *)
        echo "❌ Opção inválida"
        exit 1
        ;;
esac

echo ""
echo "${GREEN}✅ Concluído!${NC}"

