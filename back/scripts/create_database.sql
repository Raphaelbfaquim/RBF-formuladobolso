-- Script para criar o banco de dados FormuladoBolso
-- Execute como superusuário (postgres)

-- Criar banco de dados
CREATE DATABASE formulado_db
    WITH 
    OWNER = raphael
    ENCODING = 'UTF8'
    LC_COLLATE = 'pt_BR.UTF-8'
    LC_CTYPE = 'pt_BR.UTF-8'
    TEMPLATE = template0;

-- Conceder todas as permissões ao usuário
GRANT ALL PRIVILEGES ON DATABASE formulado_db TO raphael;

-- Conectar ao banco e conceder permissões no schema public
\c formulado_db

-- Conceder permissões no schema public
GRANT ALL ON SCHEMA public TO raphael;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO raphael;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO raphael;

