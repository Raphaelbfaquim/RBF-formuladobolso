#!/bin/bash
# Script para reiniciar o servidor Next.js corretamente

echo "🔄 Reiniciando servidor Next.js..."
echo ""

# Parar processos do Next.js
echo "1. Parando processos existentes..."
pkill -f "next dev" 2>/dev/null || true
sleep 2

# Limpar cache
echo "2. Limpando cache..."
rm -rf .next
rm -rf node_modules/.cache
rm -rf .turbo
echo "✅ Cache limpo"

# Verificar se node_modules existe
if [ ! -d "node_modules" ]; then
    echo "3. Instalando dependências..."
    npm install
fi

# Iniciar servidor
echo "4. Iniciando servidor de desenvolvimento..."
echo ""
npm run dev

