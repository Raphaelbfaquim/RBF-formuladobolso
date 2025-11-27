# 🚀 Deploy Completo na AWS (Backend + Frontend)

Guia para fazer deploy completo do sistema na mesma instância AWS Lightsail.

## 📊 Arquitetura

```
┌─────────────────────────────────────────┐
│         AWS Lightsail Instance          │
│         (3.238.162.190)                  │
│                                          │
│  ┌──────────┐  ┌──────────┐           │
│  │  Nginx    │  │ Frontend │           │
│  │  :80      │  │  :3000   │           │
│  └─────┬─────┘  └────┬─────┘           │
│        │             │                  │
│        └─────┬───────┘                  │
│              │                          │
│         ┌────▼─────┐                    │
│         │   API    │                    │
│         │   :8000  │                    │
│         └────┬─────┘                    │
│              │                          │
│    ┌─────────┴─────────┐               │
│    │                   │               │
│  ┌─▼───┐          ┌───▼──┐            │
│  │PostgreSQL│      │Redis │            │
│  │  :5432   │      │:6379 │            │
│  └─────────┘      └──────┘            │
└─────────────────────────────────────────┘
```

## 🎯 Como Funciona

- **Nginx** (porta 80): Reverse proxy
  - `/` → Frontend (Next.js)
  - `/api` → Backend (FastAPI)
- **Frontend** (porta 3000): Next.js em produção
- **Backend** (porta 8000): FastAPI
- **PostgreSQL** (porta 5432): Banco de dados
- **Redis** (porta 6379): Cache

## 📋 Pré-requisitos

- ✅ Instância AWS Lightsail configurada
- ✅ Docker e Docker Compose instalados
- ✅ Repositório clonado
- ✅ Arquivo `.env` configurado no backend

## 🚀 Deploy Inicial

### Passo 1: Conectar na Instância

```bash
ssh -i "C:\Users\rapha\.ssh\LightsailDefaultKey-us-east-1.pem" ubuntu@3.238.162.190
```

### Passo 2: Ir para Raiz do Projeto

```bash
cd ~/RBF-formuladobolso
```

### Passo 3: Verificar Estrutura

```bash
ls -la
# Deve mostrar: back/, front/, docker-compose.yml, nginx/
```

### Passo 4: Configurar Frontend

O frontend precisa saber a URL da API. Edite o arquivo `.env` do frontend (ou configure no docker-compose):

```bash
# Criar .env.local no frontend (opcional, já está no docker-compose)
cd front
echo "NEXT_PUBLIC_API_URL=http://3.238.162.190:8000" > .env.local
cd ..
```

### Passo 5: Deploy Completo

```bash
# Build e iniciar todos os containers
sudo docker-compose up -d --build
```

Isso vai:
1. Buildar backend
2. Buildar frontend
3. Iniciar PostgreSQL
4. Iniciar Redis
5. Iniciar API
6. Iniciar Frontend
7. Iniciar Nginx

### Passo 6: Aguardar e Verificar

```bash
# Aguardar serviços iniciarem
sleep 30

# Verificar status
sudo docker-compose ps

# Ver logs
sudo docker-compose logs -f
```

### Passo 7: Executar Migrações

```bash
sudo docker-compose exec -T api alembic upgrade head
```

## 🌐 Acessar o Sistema

Após o deploy:

- **Frontend**: http://3.238.162.190
- **API**: http://3.238.162.190/api
- **Health Check**: http://3.238.162.190/health

## 🔄 Deploy Automático via GitHub Actions

O workflow `.github/workflows/deploy-aws.yml` já está configurado para fazer deploy de tudo automaticamente!

A cada push em `back/**`, `front/**` ou `docker-compose.yml`:
1. GitHub Actions detecta
2. Conecta na AWS
3. Atualiza código
4. Reconstrói containers
5. Reinicia tudo

## 🔧 Comandos Úteis

```bash
# Ver status de todos os containers
sudo docker-compose ps

# Ver logs de todos os serviços
sudo docker-compose logs -f

# Ver logs de um serviço específico
sudo docker-compose logs -f frontend
sudo docker-compose logs -f api
sudo docker-compose logs -f nginx

# Reiniciar um serviço
sudo docker-compose restart frontend
sudo docker-compose restart api

# Parar tudo
sudo docker-compose down

# Rebuild e reiniciar
sudo docker-compose up -d --build

# Executar migrações
sudo docker-compose exec -T api alembic upgrade head
```

## 🚨 Troubleshooting

### Problema: Frontend não carrega

**Soluções:**
1. Verifique logs: `sudo docker-compose logs frontend`
2. Verifique se build foi feito: `sudo docker-compose ps frontend`
3. Verifique Nginx: `sudo docker-compose logs nginx`

### Problema: Erro de CORS

**Solução:**
1. Atualize `CORS_ORIGINS` no `back/.env`:
```env
CORS_ORIGINS=["http://3.238.162.190","http://localhost:3000"]
```
2. Reinicie API: `sudo docker-compose restart api`

### Problema: Nginx não inicia

**Soluções:**
1. Verifique se o arquivo `nginx/nginx.conf` existe
2. Verifique logs: `sudo docker-compose logs nginx`
3. Teste configuração: `sudo docker-compose exec nginx nginx -t`

## 📝 Atualizar CORS

Edite `back/.env`:

```env
CORS_ORIGINS=["http://3.238.162.190","http://localhost:3000"]
```

Reinicie API:
```bash
sudo docker-compose restart api
```

## 🔒 Configurar HTTPS (Opcional)

1. Instale Certbot na instância
2. Configure certificado SSL
3. Descomente seção HTTPS no `nginx/nginx.conf`
4. Reinicie Nginx

---

**Sistema completo deployado na AWS!** 🎉

Tudo em uma única instância, deploy automático via GitHub Actions!

