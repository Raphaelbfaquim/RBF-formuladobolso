#!/bin/bash
# Script para verificar usuários diretamente no PostgreSQL

echo "📊 Verificando usuários no banco de dados..."
echo ""

# Extrair informações da conexão
DB_USER="raphael"
DB_NAME="formulado_db"
DB_HOST="localhost"
DB_PORT="5432"

# Comando SQL
psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c "
SELECT 
    id,
    email,
    username,
    full_name,
    is_active,
    is_verified,
    role,
    created_at
FROM users
ORDER BY created_at DESC
LIMIT 100;
"

echo ""
echo "✅ Verificação concluída!"

