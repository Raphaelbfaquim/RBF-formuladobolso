# 🗄️ Configuração do Banco de Dados

## ✅ Usuário Criado

Você já criou o usuário:
- **Usuário:** `raphael`
- **Senha:** `Q1w2e3r4@@`

## 📝 Criar o Banco de Dados

Você precisa criar o banco de dados. Escolha uma das opções:

### Opção 1: Via SQL (Recomendado)

Conecte como superusuário (postgres) e execute:

```bash
sudo -u postgres psql
```

Dentro do psql, execute:

```sql
CREATE DATABASE formulado_db
    WITH 
    OWNER = raphael
    ENCODING = 'UTF8'
    TEMPLATE = template0;

GRANT ALL PRIVILEGES ON DATABASE formulado_db TO raphael;

\c formulado_db

GRANT ALL ON SCHEMA public TO raphael;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO raphael;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO raphael;

\q
```

### Opção 2: Via Script SQL

Execute o script SQL fornecido:

```bash
sudo -u postgres psql -f scripts/create_database.sql
```

### Opção 3: Via Script Bash

Execute o script bash:

```bash
./scripts/setup_database.sh
```

## ⚙️ Configuração da Aplicação

A aplicação já está configurada para usar:
- **Host:** `localhost`
- **Porta:** `5432`
- **Usuário:** `raphael`
- **Senha:** `Q1w2e3r4@@`
- **Banco:** `formulado_db`

As configurações estão em:
- `env.example` (exemplo)
- Você precisa criar um arquivo `.env` com essas configurações

## 🚀 Aplicar Migrações

Depois de criar o banco, aplique as migrações:

```bash
# Se tiver ambiente virtual
source venv/bin/activate  # ou .venv/bin/activate

# Aplicar migrações
alembic upgrade head

# Ou com Python diretamente
python3 -m alembic upgrade head
```

## ✅ Verificar

Para verificar se tudo está funcionando:

```bash
# Conectar no banco
PGPASSWORD='Q1w2e3r4@@' psql -U raphael -h localhost -d formulado_db

# Listar tabelas
\dt

# Sair
\q
```

## 📋 Resumo

1. ✅ Usuário criado: `raphael`
2. ⏳ Criar banco: `formulado_db` (execute um dos comandos acima)
3. ⏳ Criar arquivo `.env` (copie do `env.example` e ajuste)
4. ⏳ Aplicar migrações: `alembic upgrade head`
5. ✅ Pronto para usar!

---

**Nota:** Se você não tem acesso como `postgres`, peça para o administrador do PostgreSQL executar os comandos de criação do banco.

