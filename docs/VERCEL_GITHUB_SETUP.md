# 🔄 Deploy Automático Frontend via GitHub

Guia para configurar deploy automático do frontend via GitHub Actions ou Vercel conectado ao GitHub.

## 🎯 Duas Opções

### Opção 1: Vercel Conectada ao GitHub (Mais Simples) ⭐ RECOMENDADO

A Vercel faz deploy automático quando você conecta o repositório. É a forma mais fácil!

#### Passo 1: Conectar Repositório na Vercel

1. Acesse: https://vercel.com
2. Faça login com GitHub
3. Clique em **"Add New..."** > **"Project"**
4. Selecione o repositório: `Raphaelbfaquim/RBF-formuladobolso`
5. Configure:
   - **Root Directory**: Clique em "Edit" > Selecione `front`
   - **Framework Preset**: Next.js (detecta automaticamente)
6. Adicione variável de ambiente:
   - **Name**: `NEXT_PUBLIC_API_URL`
   - **Value**: `http://3.238.162.190:8000`
7. Clique em **"Deploy"**

#### Pronto! 🎉

Agora a Vercel faz deploy automático a cada push em `front/**`!

### Opção 2: GitHub Actions com Vercel CLI

Se você quiser controlar tudo via GitHub Actions.

#### Passo 1: Obter Tokens da Vercel

1. Acesse: https://vercel.com/account/tokens
2. Clique em **"Create Token"**
3. **Name**: `github-actions`
4. Clique em **"Create"**
5. **Copie o token** (você só verá uma vez!)

#### Passo 2: Obter Org ID e Project ID

1. Faça deploy manual uma vez na Vercel (para criar o projeto)
2. No painel da Vercel, vá no seu projeto
3. Vá em **"Settings"** > **"General"**
4. Você verá:
   - **Team ID** (ou Org ID)
   - **Project ID**

#### Passo 3: Adicionar Secrets no GitHub

1. Acesse: https://github.com/Raphaelbfaquim/RBF-formuladobolso/settings/secrets/actions
2. Adicione os secrets:

**Secret 1: `VERCEL_TOKEN`**
- Name: `VERCEL_TOKEN`
- Secret: Cole o token que você criou

**Secret 2: `VERCEL_ORG_ID`**
- Name: `VERCEL_ORG_ID`
- Secret: Cole o Team ID/Org ID

**Secret 3: `VERCEL_PROJECT_ID`**
- Name: `VERCEL_PROJECT_ID`
- Secret: Cole o Project ID

#### Passo 4: Workflow Já Está Criado!

O arquivo `.github/workflows/deploy-frontend.yml` já está criado e configurado!

Agora, a cada push em `front/**`, o GitHub Actions fará deploy na Vercel automaticamente.

## 🔄 Como Funciona

### Com Vercel Conectada ao GitHub (Opção 1)
- Push em `front/**` → Vercel detecta → Deploy automático
- Sem configuração adicional necessária

### Com GitHub Actions (Opção 2)
- Push em `front/**` → GitHub Actions executa → Deploy via Vercel CLI
- Mais controle, mas requer tokens

## 📝 Variáveis de Ambiente

Certifique-se de configurar na Vercel:

- **Name**: `NEXT_PUBLIC_API_URL`
- **Value**: `http://3.238.162.190:8000`
- **Environment**: Production, Preview, Development

## 🔒 Atualizar CORS no Backend

Depois que o frontend estiver deployado:

1. Anote a URL da Vercel (ex: `https://rbf-formuladobolso.vercel.app`)
2. Conecte na AWS:
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

## 🎯 Recomendação

**Use a Opção 1** (Vercel conectada ao GitHub):
- Mais simples
- Menos configuração
- Funciona perfeitamente
- Preview deployments automáticos

A Opção 2 (GitHub Actions) é útil se você quiser mais controle ou integrar com outros processos.

---

**Deploy automático configurado!** 🎉

Escolha a opção que preferir e siga os passos!

