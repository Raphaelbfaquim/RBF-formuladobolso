# 🚀 Deploy do Frontend na Vercel

Guia completo para fazer deploy do frontend Next.js na Vercel (100% gratuito).

## 💰 Por que Vercel?

- **100% Gratuito** para projetos pessoais
- **Deploy automático** do Next.js
- **HTTPS automático**
- **CDN global** (sites rápidos em todo mundo)
- **Domínio gratuito** (.vercel.app)
- **Preview deployments** para cada PR

## 📋 Passo 1: Criar Conta na Vercel

1. Acesse: https://vercel.com
2. Clique em **"Sign Up"** ou **"Registrar"**
3. Escolha **"Continue with GitHub"** (recomendado)
4. Autorize a Vercel a acessar seu GitHub

## 🚀 Passo 2: Deploy do Projeto

### Opção A: Via Interface Web (Recomendado)

1. Após fazer login, clique em **"Add New..."** > **"Project"**
2. Selecione o repositório: `Raphaelbfaquim/RBF-formuladobolso`
3. Configure o projeto:

#### Configurações do Projeto

**Framework Preset:**
- Deve detectar automaticamente: **Next.js**

**Root Directory:**
- Clique em **"Edit"**
- Selecione: `front`
- Clique em **"Continue"**

**Build and Output Settings:**
- **Build Command**: `npm run build` (já vem preenchido)
- **Output Directory**: `.next` (já vem preenchido)
- **Install Command**: `npm install` (já vem preenchido)

**Environment Variables:**
- Clique em **"Add"** para adicionar variáveis
- Adicione:
  - **Name**: `NEXT_PUBLIC_API_URL`
  - **Value**: `http://3.238.162.190:8000`
  - Clique em **"Add"**

4. Clique em **"Deploy"**
5. Aguarde o build (2-5 minutos)

### Opção B: Via Vercel CLI

```bash
# Instalar Vercel CLI
npm install -g vercel

# Login
vercel login

# Navegar para pasta do frontend
cd front

# Deploy
vercel

# Seguir as instruções:
# - Set up and deploy? Y
# - Which scope? (seu usuário)
# - Link to existing project? N
# - Project name? formulado-bolso (ou deixe padrão)
# - Directory? ./
# - Override settings? N

# Adicionar variável de ambiente
vercel env add NEXT_PUBLIC_API_URL
# Digite: http://3.238.162.190:8000
# Environment: Production, Preview, Development (selecione todos)

# Deploy para produção
vercel --prod
```

## ⚙️ Passo 3: Configurar Variáveis de Ambiente

Se você fez deploy via interface web, já configurou. Se fez via CLI, adicione:

1. No painel da Vercel, vá no seu projeto
2. Clique em **"Settings"** > **"Environment Variables"**
3. Adicione:
   - **Name**: `NEXT_PUBLIC_API_URL`
   - **Value**: `http://3.238.162.190:8000`
   - **Environment**: Marque todas (Production, Preview, Development)
4. Clique em **"Save"**

## 🔄 Passo 4: Deploy Automático

A Vercel já faz deploy automático quando você faz push na branch `main`!

### Configurar Branch Principal

1. Vá em **"Settings"** > **"Git"**
2. Verifique se a **Production Branch** está como `main`
3. Se não estiver, altere para `main`

## 🔒 Passo 5: Atualizar CORS no Backend

O backend precisa permitir requisições do frontend na Vercel.

1. Conecte na instância AWS:
```bash
ssh -i "C:\Users\rapha\.ssh\LightsailDefaultKey-us-east-1.pem" ubuntu@3.238.162.190
```

2. Edite o arquivo `.env`:
```bash
cd ~/RBF-formuladobolso/back
nano .env
```

3. Atualize o `CORS_ORIGINS`:
```env
CORS_ORIGINS=["https://seu-projeto.vercel.app","http://localhost:3000"]
```

Substitua `seu-projeto.vercel.app` pela URL que a Vercel deu (algo como `rbf-formuladobolso.vercel.app`).

4. Salve: `Ctrl+O`, Enter, `Ctrl+X`

5. Reinicie os containers:
```bash
sudo docker-compose restart api
```

## 🌐 Passo 6: Verificar Deploy

1. Após o deploy, você receberá uma URL tipo:
   - `https://rbf-formuladobolso.vercel.app`
   - Ou `https://rbf-formuladobolso-[hash].vercel.app`

2. Acesse a URL no navegador

3. Teste se está conectando com a API:
   - Abra o console do navegador (F12)
   - Veja se há erros de CORS
   - Teste fazer login

## 🔄 Deploy Automático com GitHub Actions (Opcional)

Se quiser automatizar também o deploy do frontend via GitHub Actions, podemos criar um workflow. Mas a Vercel já faz isso automaticamente!

## 📝 Variáveis de Ambiente na Vercel

### Produção
```
NEXT_PUBLIC_API_URL=http://3.238.162.190:8000
```

### Preview/Development
```
NEXT_PUBLIC_API_URL=http://3.238.162.190:8000
```

**Nota**: Use `http://` por enquanto. Se quiser usar HTTPS depois, precisará configurar um domínio e certificado SSL no backend.

## 🚨 Troubleshooting

### Problema: Erro de CORS

**Solução:**
1. Verifique se o `CORS_ORIGINS` no backend inclui a URL da Vercel
2. Reinicie o container da API: `sudo docker-compose restart api`

### Problema: API não conecta

**Soluções:**
1. Verifique se a variável `NEXT_PUBLIC_API_URL` está configurada na Vercel
2. Verifique se o backend está rodando: `curl http://3.238.162.190:8000/health`
3. Verifique o console do navegador (F12) para ver erros

### Problema: Build falha

**Soluções:**
1. Verifique os logs de build na Vercel
2. Verifique se todas as dependências estão no `package.json`
3. Tente fazer build localmente: `cd front && npm run build`

## 📚 Links Úteis

- Vercel Dashboard: https://vercel.com/dashboard
- Vercel Docs: https://vercel.com/docs
- Next.js Deploy: https://nextjs.org/docs/deployment

---

**Frontend deployado na Vercel!** 🎉

Agora você tem:
- ✅ Backend: http://3.238.162.190:8000
- ✅ Frontend: https://seu-projeto.vercel.app
- ✅ Deploy automático em ambos!

