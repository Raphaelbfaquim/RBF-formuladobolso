#!/bin/bash

# Script para testar endpoints da API

set -e

API_URL="http://localhost:8000/api/v1"

echo "🧪 Testando API do FormuladoBolso"
echo ""

# Cores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Teste 1: Health
echo "${BLUE}1. Health Check${NC}"
response=$(curl -s http://localhost:8000/health)
echo "Response: $response"
echo ""

# Teste 2: Root
echo "${BLUE}2. API Root${NC}"
response=$(curl -s http://localhost:8000/)
echo "Response: $response"
echo ""

# Teste 3: Criar usuário (registro)
echo "${BLUE}3. Testando Registro de Usuário${NC}"
register_data='{
  "username": "teste_user",
  "email": "teste@example.com",
  "password": "senha123456"
}'

response=$(curl -s -X POST "$API_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d "$register_data")

echo "Response: $response"
echo ""

# Teste 4: Login
echo "${BLUE}4. Testando Login${NC}"
login_data='{
  "username": "teste_user",
  "password": "senha123456"
}'

response=$(curl -s -X POST "$API_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d "$login_data")

echo "Response: $response"
echo ""

# Extrair token se login funcionou
TOKEN=$(echo $response | grep -o '"access_token":"[^"]*' | cut -d'"' -f4 || echo "")

if [ -n "$TOKEN" ]; then
    echo "${GREEN}✅ Login bem-sucedido! Token obtido.${NC}"
    echo ""
    
    # Teste 5: Endpoint protegido
    echo "${BLUE}5. Testando Endpoint Protegido (com token)${NC}"
    response=$(curl -s -X GET "$API_URL/users/me" \
      -H "Authorization: Bearer $TOKEN")
    echo "Response: $response"
    echo ""
else
    echo "${YELLOW}⚠️  Não foi possível obter token. Verifique se o usuário existe.${NC}"
fi

echo "${GREEN}✅ Testes concluídos!${NC}"

