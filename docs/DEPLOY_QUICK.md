# 🚀 Deploy Rápido - FormuladoBolso

## ⚡ Deploy em 5 minutos

### 1️⃣ Frontend (Vercel) - GRATUITO

```bash
# Instalar Vercel CLI
npm install -g vercel

# Login
vercel login

# Deploy
cd front
vercel --prod
```

**Pronto!** Frontend no ar em ~30 segundos.

### 2️⃣ Backend (Render) - GRATUITO (90 dias)

1. Acesse: https://render.com
2. Crie conta (gratuita)
3. "New +" > "Web Service"
4. Conecte GitHub
5. Configure:
   - **Root Directory**: `back`
   - **Build**: `pip install -r requirements.txt`
   - **Start**: `uvicorn src.presentation.api.main:app --host 0.0.0.0 --port $PORT`
6. Adicione variáveis de ambiente
7. Deploy!

### 3️⃣ Banco de Dados (Supabase) - GRATUITO PERMANENTE

1. Acesse: https://supabase.com
2. Crie projeto
3. Settings > Database > Connection String
4. Use no `DATABASE_URL` do Render

## 💰 Custo Total

- **Gratuito**: Vercel + Supabase + Render (com limites)
- **Barato**: ~R$ 35/mês (Render PostgreSQL após 90 dias)

## 🎯 Comando Make

```bash
# Deploy completo (interativo)
make deploy

# Apenas frontend
make deploy-front

# Ver ajuda
make help
```

## 📝 Variáveis de Ambiente

### Backend (Render)
```
DATABASE_URL=postgresql://...
JWT_SECRET_KEY=...
JWT_REFRESH_SECRET_KEY=...
CORS_ORIGINS=https://seu-frontend.vercel.app
```

### Frontend (Vercel)
```
NEXT_PUBLIC_API_URL=https://seu-backend.onrender.com
```

---

**Pronto para produção!** 🚀

