#!/bin/bash

# Script para instalar Docker e Git na instância Oracle Cloud
# Execute este script na instância: bash install-docker-oracle.sh

set -e

echo "🚀 Instalando Docker e Git na instância Oracle Cloud..."
echo ""

# Atualizar sistema
echo "📦 Atualizando sistema..."
sudo dnf update -y

# Instalar Docker e Git
echo "📦 Instalando Docker e Git..."
sudo dnf install -y docker git

# Configurar Docker
echo "⚙️  Configurando Docker..."
sudo systemctl enable docker
sudo systemctl start docker
sudo usermod -aG docker opc

# Instalar Docker Compose
echo "📦 Instalando Docker Compose..."
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verificar instalação
echo ""
echo "✅ Verificando instalação..."
docker --version
git --version
docker-compose --version

echo ""
echo "✅ Instalação concluída!"
echo ""
echo "⚠️  IMPORTANTE: Faça logout e login novamente para usar Docker sem sudo"
echo "   Execute: exit"
echo "   Depois reconecte: ssh -i sua_chave.pem opc@136.248.95.96"

