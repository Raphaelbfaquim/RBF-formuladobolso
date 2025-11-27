#!/bin/bash

# Script para instalar Node.js usando NVM

echo "🚀 Instalando Node.js via NVM..."

# Verificar se nvm já está instalado
if [ -s "$HOME/.nvm/nvm.sh" ]; then
    echo "✅ NVM já está instalado"
    source "$HOME/.nvm/nvm.sh"
else
    echo "📥 Instalando NVM..."
    curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
    
    # Carregar NVM
    export NVM_DIR="$HOME/.nvm"
    [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
    [ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"
fi

# Instalar Node.js LTS
echo "📦 Instalando Node.js LTS..."
nvm install --lts
nvm use --lts

# Verificar instalação
echo ""
echo "✅ Verificando instalação..."
node --version
npm --version

echo ""
echo "✅ Node.js instalado com sucesso!"
echo ""
echo "📝 Próximos passos:"
echo "   cd front"
echo "   npm install"
echo "   npm run dev"

