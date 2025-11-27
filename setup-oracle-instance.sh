#!/bin/bash

# Script completo para configurar instância Oracle Cloud
# Execute na instância: bash setup-oracle-instance.sh

set -e

echo "🚀 Configurando instância Oracle Cloud para FormuladoBolso"
echo ""

# 1. Atualizar sistema
echo "📦 1/6 - Atualizando sistema..."
sudo dnf update -y -q

# 2. Instalar Docker e Git
echo "📦 2/6 - Instalando Docker e Git..."
sudo dnf install -y docker git

# 3. Configurar Docker
echo "⚙️  3/6 - Configurando Docker..."
sudo systemctl enable docker
sudo systemctl start docker
sudo usermod -aG docker opc

# 4. Instalar Docker Compose
echo "📦 4/6 - Instalando Docker Compose..."
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 5. Clonar repositório
echo "📥 5/6 - Clonando repositório..."
cd ~
if [ -d "RBF-formuladobolso" ]; then
    echo "   Repositório já existe, atualizando..."
    cd RBF-formuladobolso
    git pull origin main || true
else
    git clone https://github.com/Raphaelbfaquim/RBF-formuladobolso.git
    cd RBF-formuladobolso
fi

# 6. Criar .env se não existir
echo "⚙️  6/6 - Configurando ambiente..."
cd back
if [ ! -f .env ]; then
    cp env.example .env
    echo "   ✅ Arquivo .env criado a partir do exemplo"
    echo "   ⚠️  IMPORTANTE: Edite o arquivo .env com suas configurações!"
else
    echo "   ✅ Arquivo .env já existe"
fi

echo ""
echo "✅ Configuração concluída!"
echo ""
echo "📋 Próximos passos:"
echo "   1. Edite o arquivo ~/RBF-formuladobolso/back/.env"
echo "   2. Faça logout e login novamente (para aplicar grupo docker)"
echo "   3. Execute: cd ~/RBF-formuladobolso/back && docker-compose up -d --build"
echo ""

