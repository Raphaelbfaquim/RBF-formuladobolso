# 🆓 Deploy 100% Gratuito - FormuladoBolso

Guia completo para deploy totalmente gratuito usando provedores com planos free generosos.

## 🎯 Stack Gratuita Escolhida

### ✅ Backend: **Railway** 
- **$5 créditos grátis/mês** (suficiente para apps pequenos/médios)
- Deploy automático via GitHub
- HTTPS automático
- Domínio gratuito (.railway.app)
- **Alternativa**: Fly.io (também gratuito)

### ✅ Frontend: **Vercel**
- **Gratuito ilimitado** para projetos pessoais
- Deploy automático do Next.js
- CDN global
- HTTPS automático
- Domínio .vercel.app gratuito

### ✅ Database: **Supabase**
- **Gratuito permanente** (500MB, 2GB bandwidth)
- PostgreSQL completo
- API REST automática
- Dashboard web
- **Alternativa**: Neon (também gratuito)

## 🚀 Deploy Rápido (5 minutos)

### 1️⃣ Database - Supabase (2 min)

1. Acesse: https://supabase.com
2. Clique em "Start your project"
3. Faça login com GitHub
4. Clique em "New Project"
5. Configure:
   - **Name**: `formulado-bolso`
   - **Database Password**: (anote esta senha!)
   - **Region**: Escolha mais próxima (South America)
6. Aguarde criação (2-3 minutos)
7. Vá em **Settings** > **Database**
8. Copie a **Connection String** (URI)
   - Formato: `postgresql://postgres:[PASSWORD]@[HOST]:5432/postgres`

✅ **Pronto!** Database configurado.

### 2️⃣ Backend - Railway (2 min)

1. Acesse: https://railway.app
2. Faça login com GitHub
3. Clique em **"New Project"**
4. Selecione **"Deploy from GitHub repo"**
5. Escolha seu repositório
6. Railway detectará Python automaticamente
7. Configure:
   - **Root Directory**: `back`
   - **Start Command**: (deixe vazio, Railway detecta)
8. Vá em **Variables** e adicione:
   ```
   DATABASE_URL=<cole_a_connection_string_do_supabase>
   JWT_SECRET_KEY=<gere_uma_chave_secreta>
   JWT_REFRESH_SECRET_KEY=<gere_outra_chave>
   CORS_ORIGINS=https://seu-frontend.vercel.app
   DEBUG=False
   ```
9. Clique em **"Deploy"**

✅ **Pronto!** Backend no ar. Anote a URL (.railway.app)

### 3️⃣ Frontend - Vercel (1 min)

```bash
# Instalar Vercel CLI
npm install -g vercel

# Login
vercel login

# Deploy
cd front
vercel --prod
```

Ou use o comando make:
```bash
make deploy-front
```

✅ **Pronto!** Frontend no ar. Anote a URL (.vercel.app)

### 4️⃣ Configurar CORS

No Railway, atualize a variável:
```
CORS_ORIGINS=https://seu-frontend.vercel.app,http://localhost:3000
```

## 💰 Custo Total

### **R$ 0,00 / mês** 🎉

- Railway: $5 créditos grátis/mês (suficiente)
- Vercel: Gratuito ilimitado
- Supabase: Gratuito permanente

## 🔧 Comandos Make

```bash
# Deploy completo gratuito (interativo)
make deploy-free

# Apenas frontend
make deploy-front

# Ver ajuda
make help
```

## 📝 Variáveis de Ambiente

### Railway (Backend)

```env
DATABASE_URL=postgresql://postgres:senha@db.xxx.supabase.co:5432/postgres
JWT_SECRET_KEY=chave_secreta_aqui_32_chars_min
JWT_REFRESH_SECRET_KEY=chave_refresh_aqui_32_chars_min
CORS_ORIGINS=https://formulado-bolso.vercel.app,http://localhost:3000
DEBUG=False
PORT=8000
```

### Vercel (Frontend)

```env
NEXT_PUBLIC_API_URL=https://seu-backend.railway.app
```

## 🎯 Alternativas Gratuitas

### Backend
- **Railway**: $5/mês créditos (recomendado)
- **Fly.io**: Gratuito com limites generosos
- **Render**: Gratuito (dorme após 15min)
- **Heroku**: Não tem mais plano gratuito

### Database
- **Supabase**: Gratuito permanente (recomendado)
- **Neon**: Gratuito permanente
- **Railway PostgreSQL**: Incluído nos créditos
- **ElephantSQL**: Gratuito (limite 20MB)

## 🔄 Deploy Automático

### Railway + GitHub

1. Conecte repositório no Railway
2. Railway faz deploy automático a cada push
3. Atualiza variáveis de ambiente quando necessário

### Vercel + GitHub

1. Conecte repositório na Vercel
2. Vercel faz deploy automático a cada push
3. Preview deployments para cada PR

## 📊 Limites Gratuitos

### Railway
- $5 créditos/mês
- ~500 horas de uso/mês
- Suficiente para apps pequenos/médios

### Vercel
- Bandwidth: 100GB/mês
- Builds: Ilimitados
- Domínios: Ilimitados

### Supabase
- Database: 500MB
- Bandwidth: 2GB/mês
- API requests: Ilimitados
- Suficiente para desenvolvimento e apps pequenos

## 🚨 Troubleshooting

### Backend não inicia
- Verificar logs no Railway
- Verificar DATABASE_URL
- Verificar se porta está correta ($PORT)

### Frontend não conecta
- Verificar NEXT_PUBLIC_API_URL
- Verificar CORS_ORIGINS no backend
- Verificar se backend está rodando

### Database connection error
- Verificar senha do Supabase
- Verificar se IP está liberado (Supabase > Settings > Database)
- Verificar connection string

## 📚 Links Úteis

- Railway: https://railway.app
- Vercel: https://vercel.com
- Supabase: https://supabase.com
- Fly.io: https://fly.io (alternativa)

---

**Deploy 100% Gratuito!** 🎉

