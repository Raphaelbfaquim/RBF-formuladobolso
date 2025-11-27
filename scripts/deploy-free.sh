#!/bin/bash

# Script de deploy GRATUITO para FormuladoBolso
# Railway (Backend) + Vercel (Frontend) + Supabase (Database)

set -e

echo "🚀 Deploy GRATUITO do FormuladoBolso..."
echo ""

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "${BLUE}📋 Opções de Deploy Gratuito:${NC}"
echo ""
echo "1) Railway (Backend) - $5 créditos grátis/mês"
echo "2) Vercel (Frontend) - Gratuito ilimitado"
echo "3) Supabase (Database) - Gratuito permanente"
echo "4) Deploy completo (todos acima)"
echo ""
read -p "Escolha uma opção (1-4): " choice

case $choice in
    1)
        echo ""
        echo "${BLUE}🚂 Deploy Backend no Railway...${NC}"
        echo ""
        echo "📝 Passos:"
        echo "1. Acesse: https://railway.app"
        echo "2. Faça login com GitHub"
        echo "3. Clique em 'New Project'"
        echo "4. Selecione 'Deploy from GitHub repo'"
        echo "5. Escolha este repositório"
        echo "6. Railway detectará automaticamente Python"
        echo "7. Configure Root Directory: back"
        echo "8. Adicione variáveis de ambiente:"
        echo "   - DATABASE_URL (do Supabase)"
        echo "   - JWT_SECRET_KEY"
        echo "   - JWT_REFRESH_SECRET_KEY"
        echo "   - CORS_ORIGINS"
        echo ""
        echo "✅ Railway é GRATUITO com $5 créditos/mês!"
        ;;
        
    2)
        echo ""
        echo "${BLUE}▲ Deploy Frontend na Vercel...${NC}"
        cd front
        
        if ! command -v vercel &> /dev/null; then
            echo "📦 Instalando Vercel CLI..."
            npm install -g vercel
        fi
        
        if ! vercel whoami >/dev/null 2>&1; then
            echo "🔐 Login na Vercel:"
            vercel login
        fi
        
        echo "🚀 Fazendo deploy..."
        vercel --prod
        
        echo ""
        echo "${GREEN}✅ Frontend deployado!${NC}"
        ;;
        
    3)
        echo ""
        echo "${BLUE}🗄️  Configurar Supabase (Database)...${NC}"
        echo ""
        echo "📝 Passos:"
        echo "1. Acesse: https://supabase.com"
        echo "2. Crie uma conta (gratuita)"
        echo "3. Clique em 'New Project'"
        echo "4. Escolha organização e nome do projeto"
        echo "5. Aguarde criação (2-3 minutos)"
        echo "6. Vá em Settings > Database"
        echo "7. Copie a 'Connection String' (URI)"
        echo "8. Use no DATABASE_URL do backend"
        echo ""
        echo "✅ Supabase é GRATUITO permanentemente!"
        ;;
        
    4)
        echo ""
        echo "${BLUE}🚀 Deploy Completo Gratuito...${NC}"
        echo ""
        
        # 1. Supabase
        echo "${YELLOW}1/3 - Configure Supabase${NC}"
        echo "Acesse: https://supabase.com"
        echo "Crie projeto e copie DATABASE_URL"
        echo ""
        read -p "Pressione Enter quando tiver o DATABASE_URL..."
        
        # 2. Railway Backend
        echo ""
        echo "${YELLOW}2/3 - Deploy Backend no Railway${NC}"
        echo "Acesse: https://railway.app"
        echo "Conecte GitHub e faça deploy"
        echo "Root Directory: back"
        echo ""
        read -p "Pressione Enter quando backend estiver no ar..."
        
        # 3. Vercel Frontend
        echo ""
        echo "${YELLOW}3/3 - Deploy Frontend na Vercel${NC}"
        cd front
        
        if ! command -v vercel &> /dev/null; then
            npm install -g vercel
        fi
        
        if ! vercel whoami >/dev/null 2>&1; then
            vercel login
        fi
        
        echo "🚀 Fazendo deploy do frontend..."
        FRONTEND_URL=$(vercel --prod | grep -o 'https://[^ ]*' | head -1 || echo "")
        
        echo ""
        echo "${GREEN}✅ Deploy completo!${NC}"
        echo "Frontend: $FRONTEND_URL"
        echo ""
        echo "📝 Configure CORS_ORIGINS no Railway com: $FRONTEND_URL"
        ;;
        
    *)
        echo "❌ Opção inválida"
        exit 1
        ;;
esac

echo ""
echo "${GREEN}✅ Concluído!${NC}"

