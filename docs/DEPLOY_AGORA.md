# 🚀 Deploy Agora - Passo a Passo

## ⚡ Deploy em 5 minutos - 100% GRATUITO

### Passo 1: Database (Supabase) - 2 minutos

1. Acesse: **https://supabase.com**
2. Clique em **"Start your project"**
3. Faça login com **GitHub**
4. Clique em **"New Project"**
5. Configure:
   - **Name**: `formulado-bolso`
   - **Database Password**: (ANOTE ESTA SENHA!)
   - **Region**: South America (São Paulo)
6. Aguarde 2-3 minutos
7. Vá em **Settings** > **Database**
8. Copie a **Connection String** (URI)
   - Exemplo: `postgresql://postgres.xxx:senha@aws-0-sa-east-1.pooler.supabase.com:6543/postgres`

✅ **Anote esta URL!** Você vai usar no próximo passo.

---

### Passo 2: Backend (Railway) - 2 minutos

1. Acesse: **https://railway.app**
2. Faça login com **GitHub**
3. Clique em **"New Project"**
4. Selecione **"Deploy from GitHub repo"**
5. Escolha seu repositório **FormuladoBolso**
6. Railway detectará Python automaticamente
7. Configure:
   - **Root Directory**: `back`
   - **Start Command**: (deixe vazio, Railway detecta automaticamente)
8. Vá em **Variables** e adicione:

```
DATABASE_URL=<cole_a_url_do_supabase_aqui>
JWT_SECRET_KEY=<gere_uma_chave_aleatoria_32_chars>
JWT_REFRESH_SECRET_KEY=<gere_outra_chave_aleatoria_32_chars>
CORS_ORIGINS=https://formulado-bolso.vercel.app,http://localhost:3000
DEBUG=False
```

**Para gerar chaves secretas:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

9. Clique em **"Deploy"**
10. Aguarde deploy (2-3 minutos)
11. Anote a URL do backend (ex: `https://formulado-bolso-production.up.railway.app`)

✅ **Backend no ar!**

---

### Passo 3: Frontend (Vercel) - 1 minuto

```bash
# No terminal, execute:
cd front
npm install -g vercel
vercel login
vercel --prod
```

Ou use o comando make:
```bash
make deploy-front
```

1. Vercel vai perguntar algumas coisas:
   - **Link to existing project?** → N (não)
   - **Project name?** → `formulado-bolso` (ou deixe padrão)
   - **Directory?** → `./` (pressione Enter)
   - **Override settings?** → N (não)

2. Vercel vai fazer deploy automaticamente
3. Anote a URL do frontend (ex: `https://formulado-bolso.vercel.app`)

✅ **Frontend no ar!**

---

### Passo 4: Configurar CORS

1. Volte no **Railway**
2. Vá em **Variables**
3. Atualize `CORS_ORIGINS` com a URL do Vercel:
```
CORS_ORIGINS=https://formulado-bolso.vercel.app,http://localhost:3000
```
4. Railway vai reiniciar automaticamente

---

### Passo 5: Configurar Frontend

1. No **Vercel**, vá em **Settings** > **Environment Variables**
2. Adicione:
```
NEXT_PUBLIC_API_URL=https://seu-backend.railway.app
```
3. Vercel vai fazer redeploy automaticamente

---

## ✅ Pronto!

Acesse:
- **Frontend**: https://formulado-bolso.vercel.app
- **Backend**: https://seu-backend.railway.app
- **API Docs**: https://seu-backend.railway.app/docs

## 💰 Custo

**R$ 0,00 / mês** 🎉

- Railway: $5 créditos grátis/mês (suficiente)
- Vercel: Gratuito ilimitado
- Supabase: Gratuito permanente

## 🔄 Deploy Automático

Agora, a cada push no GitHub:
- **Railway** faz deploy automático do backend
- **Vercel** faz deploy automático do frontend

## 📝 Comandos Úteis

```bash
# Ver logs do backend (Railway)
# Acesse Railway > seu projeto > Deployments > View Logs

# Ver logs do frontend (Vercel)
# Acesse Vercel > seu projeto > Deployments > View Logs

# Redeploy manual
make deploy-free
```

---

**Sistema no ar e 100% gratuito!** 🚀

