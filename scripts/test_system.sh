#!/bin/bash

# Script de teste do sistema FormuladoBolso

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "${BLUE}🧪 TESTANDO SISTEMA FORMULADOBOLSO${NC}"
echo ""

# Testes
PASSED=0
FAILED=0

test_endpoint() {
    local name=$1
    local url=$2
    local expected_status=${3:-200}
    
    echo -n "Testando $name... "
    
    status=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null || echo "000")
    
    if [ "$status" = "$expected_status" ]; then
        echo "${GREEN}✅ PASSOU${NC} (Status: $status)"
        ((PASSED++))
        return 0
    else
        echo "${RED}❌ FALHOU${NC} (Status: $status, esperado: $expected_status)"
        ((FAILED++))
        return 1
    fi
}

# 1. Backend Health
echo "${YELLOW}📋 Testando Backend...${NC}"
test_endpoint "Health Check" "http://localhost:8000/health" 200
test_endpoint "Root Endpoint" "http://localhost:8000/" 200
test_endpoint "API Docs" "http://localhost:8000/docs" 200

# 2. Frontend
echo ""
echo "${YELLOW}📋 Testando Frontend...${NC}"
test_endpoint "Homepage" "http://localhost:3000" 200
test_endpoint "Login Page" "http://localhost:3000/login" 200
test_endpoint "Register Page" "http://localhost:3000/register" 200

# 3. API Endpoints (sem auth)
echo ""
echo "${YELLOW}📋 Testando Endpoints da API...${NC}"
test_endpoint "Auth Endpoints" "http://localhost:8000/api/v1/auth" 404  # Deve retornar 404 ou 405, não 500

# Resumo
echo ""
echo "${BLUE}📊 RESUMO DOS TESTES${NC}"
echo "${GREEN}✅ Passou: $PASSED${NC}"
echo "${RED}❌ Falhou: $FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo "${GREEN}🎉 Todos os testes passaram!${NC}"
    exit 0
else
    echo "${YELLOW}⚠️  Alguns testes falharam. Verifique os serviços.${NC}"
    exit 1
fi

