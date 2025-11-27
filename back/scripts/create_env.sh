#!/bin/bash

# Script para criar arquivo .env a partir do env.example

if [ -f .env ]; then
    echo "Arquivo .env já existe!"
    echo "Deseja sobrescrever? (s/N)"
    read -r response
    if [[ ! "$response" =~ ^[Ss]$ ]]; then
        echo "Cancelado."
        exit 0
    fi
fi

# Copiar env.example para .env
cp env.example .env

echo "✅ Arquivo .env criado com sucesso!"
echo ""
echo "⚠️  IMPORTANTE: Edite o arquivo .env e configure:"
echo "   - SECRET_KEY (gere uma chave aleatória longa)"
echo "   - SMTP_USER e SMTP_PASSWORD (se for usar email)"
echo "   - WHATSAPP_API_TOKEN (se for usar WhatsApp)"
echo "   - OPENAI_API_KEY (se for usar IA)"
echo ""
echo "Para gerar uma SECRET_KEY segura, execute:"
echo "python3 -c 'import secrets; print(secrets.token_urlsafe(32))'"

