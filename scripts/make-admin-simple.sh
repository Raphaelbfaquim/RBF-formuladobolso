#!/bin/bash
# Script simples para tornar usuário admin via SQL
# Uso: ./make-admin-simple.sh <email>

if [ -z "$1" ]; then
    echo "Uso: ./make-admin-simple.sh <email>"
    echo "Exemplo: ./make-admin-simple.sh usuario@email.com"
    exit 1
fi

EMAIL=$1

# Tentar diferentes formas de conectar ao PostgreSQL
if docker-compose ps postgres | grep -q "Up"; then
    echo "Usando docker-compose..."
    docker-compose exec -T postgres psql -U formulado_user -d formulado_db <<EOF
UPDATE users SET role = 'admin' WHERE email = '$EMAIL';
SELECT email, username, role FROM users WHERE email = '$EMAIL';
EOF
elif command -v psql &> /dev/null; then
    echo "Usando psql direto..."
    PGPASSWORD=formulado_pass psql -h localhost -U formulado_user -d formulado_db <<EOF
UPDATE users SET role = 'admin' WHERE email = '$EMAIL';
SELECT email, username, role FROM users WHERE email = '$EMAIL';
EOF
else
    echo "❌ PostgreSQL não encontrado!"
    echo ""
    echo "Execute manualmente via SQL:"
    echo "UPDATE users SET role = 'admin' WHERE email = '$EMAIL';"
    exit 1
fi

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Usuário '$EMAIL' promovido a administrador!"
else
    echo ""
    echo "❌ Erro ao atualizar usuário"
    exit 1
fi

