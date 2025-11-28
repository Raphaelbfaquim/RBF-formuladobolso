# 🧪 Teste Local - FormuladoBolso

Guia rápido para testar o sistema localmente antes de fazer deploy.

## 🚀 Opção 1: Docker Compose (Mais Fácil)

### 1. Configurar variáveis de ambiente

Crie o arquivo `back/.env`:

```bash
cd back
cp env.example .env
```

Edite o `.env` com:
```env
DATABASE_URL=postgresql+asyncpg://formulado_user:formulado_pass@postgres:5432/formulado_db
DATABASE_SYNC_URL=postgresql://formulado_user:formulado_pass@postgres:5432/formulado_db
REDIS_HOST=redis
REDIS_PORT=6379
SECRET_KEY=sua-chave-secreta-aqui-mude-em-producao
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
ENVIRONMENT=development
```

### 2. Iniciar com Docker Compose

```bash
# Na raiz do projeto
docker-compose up -d
```

Isso vai iniciar:
- PostgreSQL (porta 5432)
- Redis (porta 6379)
- API (porta 8000)
- Frontend (porta 3000)

### 3. Executar migrações

```bash
docker-compose exec api alembic upgrade head
```

### 4. Acessar

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Docs API: http://localhost:8000/docs

---

## 🚀 Opção 2: Desenvolvimento Manual (Mais Controle)

### Backend

```bash
cd back

# Criar ambiente virtual (se não tiver)
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Configurar .env (copiar de env.example e editar)
cp env.example .env
# Editar .env com:
# DATABASE_URL=postgresql+asyncpg://formulado_user:formulado_pass@localhost:5432/formulado_db
# DATABASE_SYNC_URL=postgresql://formulado_user:formulado_pass@localhost:5432/formulado_db
# SECRET_KEY=sua-chave-secreta
# CORS_ORIGINS=http://localhost:3000

# Iniciar PostgreSQL e Redis (via Docker)
docker-compose up -d postgres redis

# Executar migrações
alembic upgrade head

# Iniciar servidor
uvicorn src.presentation.api.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd front

# Instalar dependências
npm install

# Criar .env.local
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# Iniciar servidor de desenvolvimento
npm run dev
```

### Acessar

- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- Docs: http://localhost:8000/docs

---

## 🧪 Testar o 2FA no Registro

1. Acesse: http://localhost:3000/register
2. Preencha o formulário
3. Abra o console do navegador (F12)
4. Veja os logs:
   - `📤 Enviando requisição de registro...`
   - `📥 Resposta recebida:`
   - `✅ 2FA data recebido:`
5. O QR code deve aparecer na tela

---

## 🛑 Parar o Sistema

### Docker Compose:
```bash
docker-compose down
```

### Manual:
- Backend: Ctrl+C no terminal
- Frontend: Ctrl+C no terminal
- PostgreSQL/Redis: `docker-compose down postgres redis`

---

## 🔍 Verificar Logs

### Docker Compose:
```bash
# Ver logs de todos os serviços
docker-compose logs -f

# Ver logs apenas da API
docker-compose logs -f api

# Ver logs apenas do frontend
docker-compose logs -f frontend
```

### Manual:
- Backend: logs aparecem no terminal
- Frontend: logs aparecem no terminal

---

## ⚠️ Troubleshooting

### Erro: "Port already in use"
```bash
# Verificar o que está usando a porta
# Windows:
netstat -ano | findstr :8000
netstat -ano | findstr :3000

# Linux/Mac:
lsof -i :8000
lsof -i :3000
```

### Erro: "Database connection failed"
- Verifique se PostgreSQL está rodando: `docker-compose ps`
- Verifique as credenciais no `.env`

### Erro: "Module not found"
- Reinstale as dependências:
  ```bash
  # Backend
  pip install -r requirements.txt
  
  # Frontend
  rm -rf node_modules package-lock.json
  npm install
  ```

