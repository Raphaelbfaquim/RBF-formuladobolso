# 🚀 Deploy Completo - FormuladoBolso

Guia resumido para fazer deploy completo (Backend + Frontend).

## 📊 Arquitetura de Deploy

```
┌─────────────────┐         ┌──────────────────┐
│   Frontend      │         │    Backend        │
│   (Vercel)      │ ──────> │  (AWS Lightsail) │
│   Next.js       │         │   FastAPI         │
│   Gratuito      │         │   $7/mês          │
└─────────────────┘         └──────────────────┘
```

## ✅ Checklist de Deploy

### Backend (AWS Lightsail) ✅ CONCLUÍDO
- [x] Instância criada: `3.238.162.190`
- [x] Docker instalado
- [x] Repositório clonado
- [x] Containers rodando
- [x] API funcionando: http://3.238.162.190:8000
- [x] GitHub Actions configurado
- [x] Deploy automático funcionando

### Frontend (Vercel) ⏳ PRÓXIMO PASSO
- [ ] Conta Vercel criada
- [ ] Projeto conectado ao GitHub
- [ ] Variável `NEXT_PUBLIC_API_URL` configurada
- [ ] Deploy realizado
- [ ] CORS atualizado no backend

## 🚀 Passos Rápidos para Frontend

### 1. Criar Conta Vercel (2 min)
1. Acesse: https://vercel.com
2. Clique em **"Sign Up"** > **"Continue with GitHub"**
3. Autorize acesso

### 2. Deploy do Projeto (3 min)
1. Clique em **"Add New..."** > **"Project"**
2. Selecione: `Raphaelbfaquim/RBF-formuladobolso`
3. Configure:
   - **Root Directory**: `front`
   - **Framework**: Next.js (detecta automaticamente)
4. Adicione variável de ambiente:
   - **Name**: `NEXT_PUBLIC_API_URL`
   - **Value**: `http://3.238.162.190:8000`
5. Clique em **"Deploy"**

### 3. Atualizar CORS no Backend (2 min)
1. Anote a URL do frontend (ex: `https://rbf-formuladobolso.vercel.app`)
2. Conecte na instância AWS:
```bash
ssh -i "C:\Users\rapha\.ssh\LightsailDefaultKey-us-east-1.pem" ubuntu@3.238.162.190
```

3. Edite `.env`:
```bash
cd ~/RBF-formuladobolso/back
nano .env
```

4. Atualize `CORS_ORIGINS`:
```env
CORS_ORIGINS=["https://sua-url.vercel.app","http://localhost:3000"]
```

5. Reinicie API:
```bash
sudo docker-compose restart api
```

## 📋 URLs Finais

Após deploy completo:

- **Backend API**: http://3.238.162.190:8000
- **Frontend**: https://seu-projeto.vercel.app
- **API Health**: http://3.238.162.190:8000/health
- **API Docs**: http://3.238.162.190:8000/docs

## 🔄 Deploy Automático

### Backend
- ✅ GitHub Actions configurado
- ✅ Deploy automático a cada push em `back/**`

### Frontend
- ✅ Vercel faz deploy automático a cada push em `front/**`
- ✅ Preview deployments para cada PR

## 💰 Custos

- **Backend (AWS Lightsail)**: $7/mês (90 dias grátis)
- **Frontend (Vercel)**: $0/mês (gratuito)
- **Total**: $7/mês (~R$ 35/mês) após período grátis

## 📚 Documentação Completa

- **Backend AWS**: `docs/AWS_SETUP.md`
- **Frontend Vercel**: `docs/VERCEL_DEPLOY.md`
- **GitHub Actions**: `docs/GITHUB_ACTIONS_SETUP.md`

---

**Pronto para fazer deploy do frontend!** 🎉

Siga o guia em `docs/VERCEL_DEPLOY.md` para deploy na Vercel.

