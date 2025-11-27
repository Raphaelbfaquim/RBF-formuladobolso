#!/bin/bash

# Deploy automático - Frontend primeiro

set -e

echo "🚀 Deploy Automático do FormuladoBolso"
echo ""

cd "$(dirname "$0")/../front"

# Verificar Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js não encontrado. Execute: ./install_node.sh"
    exit 1
fi

# Carregar nvm se disponível
if [ -s "$HOME/.nvm/nvm.sh" ]; then
    source "$HOME/.nvm/nvm.sh"
fi

# Instalar Vercel CLI se necessário
if ! command -v vercel &> /dev/null; then
    echo "📦 Instalando Vercel CLI..."
    npm install -g vercel
fi

# Verificar login
if ! vercel whoami >/dev/null 2>&1; then
    echo "🔐 Faça login na Vercel:"
    vercel login
fi

echo "🚀 Fazendo deploy do frontend..."
echo ""

# Deploy
vercel --prod --yes

echo ""
echo "✅ Frontend deployado!"
echo ""
echo "📝 Próximos passos:"
echo "1. Configure o database no Supabase: https://supabase.com"
echo "2. Configure o backend no Railway: https://railway.app"
echo "3. Veja o guia completo: cat DEPLOY_AGORA.md"

