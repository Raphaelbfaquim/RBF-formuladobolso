#!/bin/bash

# Script para criar o banco de dados FormuladoBolso
# Execute como superusuário do PostgreSQL

echo "Criando banco de dados formulado_db..."

# Opção 1: Se você tem acesso como postgres
sudo -u postgres psql << EOF
CREATE DATABASE formulado_db
    WITH 
    OWNER = raphael
    ENCODING = 'UTF8'
    TEMPLATE = template0;

GRANT ALL PRIVILEGES ON DATABASE formulado_db TO raphael;
EOF

# Conectar ao banco e conceder permissões
sudo -u postgres psql -d formulado_db << EOF
GRANT ALL ON SCHEMA public TO raphael;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO raphael;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO raphael;
EOF

echo "Banco de dados criado com sucesso!"
echo "Agora você pode aplicar as migrações com: alembic upgrade head"

