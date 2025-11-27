# 🚀 Guia de Deploy - FormuladoBolso

Deploy gratuito/barato em provedores modernos.

## 📊 Provedores Escolhidos

### Frontend: **Vercel** (Gratuito)
- ✅ Deploy automático do Next.js
- ✅ HTTPS automático
- ✅ CDN global
- ✅ Domínio gratuito (.vercel.app)
- ✅ Deploy em segundos

### Backend: **Render** (Gratuito com limites)
- ✅ PostgreSQL gratuito (90 dias, depois $7/mês)
- ✅ Redis opcional (pago)
- ✅ HTTPS automático
- ✅ Deploy automático via Git
- ✅ Alternativa: Railway (também gratuito)

## 🚀 Deploy Rápido

### Opção 1: Automático (Recomendado)

```bash
# Deploy completo
make deploy

# Ou apenas frontend
make deploy-front

# Ou apenas backend
make deploy-back
```

### Opção 2: Manual

#### Frontend (Vercel)

```bash
# 1. Instalar Vercel CLI
npm install -g vercel

# 2. Login
vercel login

# 3. Deploy
cd front
vercel --prod
```

#### Backend (Render)

1. Acesse: https://render.com
2. Crie uma conta (gratuita)
3. Clique em "New +" > "Web Service"
4. Conecte seu repositório GitHub
5. Configure:
   - **Name**: `formulado-bolso-api`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn src.presentation.api.main:app --host 0.0.0.0 --port $PORT`
   - **Root Directory**: `back`

6. Adicione variáveis de ambiente:
   ```
   DATABASE_URL=<sua_url_postgres>
   REDIS_URL=<sua_url_redis> (opcional)
   JWT_SECRET_KEY=<chave_secreta>
   JWT_REFRESH_SECRET_KEY=<chave_refresh>
   CORS_ORIGINS=https://seu-frontend.vercel.app
   ```

7. Clique em "Create Web Service"

## 📝 Variáveis de Ambiente

### Backend (.env no Render)

```env
DATABASE_URL=postgresql://user:pass@host:5432/dbname
REDIS_URL=redis://host:6379 (opcional)
JWT_SECRET_KEY=sua_chave_secreta_aqui
JWT_REFRESH_SECRET_KEY=sua_chave_refresh_aqui
CORS_ORIGINS=https://formulado-bolso.vercel.app
DEBUG=False
```

### Frontend (.env.local na Vercel)

```env
NEXT_PUBLIC_API_URL=https://seu-backend.onrender.com
```

## 🗄️ Banco de Dados

### Opção 1: Render PostgreSQL (Gratuito 90 dias)

1. No Render, clique em "New +" > "PostgreSQL"
2. Configure:
   - **Name**: `formulado-bolso-db`
   - **Plan**: Free (90 dias)
3. Copie a **Internal Database URL**
4. Use no `DATABASE_URL` do backend

### Opção 2: Supabase (Gratuito permanente)

1. Acesse: https://supabase.com
2. Crie um projeto
3. Vá em Settings > Database
4. Copie a **Connection String**
5. Use no `DATABASE_URL`

### Opção 3: Railway (Gratuito com créditos)

1. Acesse: https://railway.app
2. Crie um projeto
3. Adicione PostgreSQL
4. Copie a URL de conexão

## 🔄 Deploy Automático

### GitHub Actions (Opcional)

Crie `.github/workflows/deploy.yml`:

```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: amondnet/vercel-action@v20
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
          working-directory: ./front
```

## 💰 Custos

### Plano Gratuito

- **Vercel**: Gratuito (ilimitado para projetos pessoais)
- **Render**: Gratuito (com limites)
  - Web Service: Gratuito (dorme após 15min de inatividade)
  - PostgreSQL: Gratuito 90 dias, depois $7/mês
  - Redis: Pago ($10/mês)

### Plano Barato (Recomendado)

- **Vercel**: Gratuito
- **Render**: $7/mês (PostgreSQL)
- **Total**: ~$7/mês (~R$ 35/mês)

### Alternativas Gratuitas

- **Supabase**: PostgreSQL gratuito permanente
- **Railway**: $5 créditos grátis/mês
- **Fly.io**: Gratuito com limites

## 🔧 Troubleshooting

### Backend não inicia
- Verificar variáveis de ambiente
- Verificar logs no Render
- Verificar se `DATABASE_URL` está correto

### Frontend não conecta com API
- Verificar `NEXT_PUBLIC_API_URL`
- Verificar CORS no backend
- Verificar se backend está rodando

### Erro de migração
- Executar migrações manualmente:
  ```bash
  cd back
  alembic upgrade head
  ```

## 📚 Links Úteis

- Vercel: https://vercel.com
- Render: https://render.com
- Supabase: https://supabase.com
- Railway: https://railway.app

---

**FormuladoBolso** - Deploy simples e barato! 💰

