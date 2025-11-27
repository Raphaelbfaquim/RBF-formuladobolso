# 🚀 Deploy Simples na AWS - GUIA COMPLETO

## ⚡ COMANDO ÚNICO (MAIS FÁCIL!)

```powershell
# Execute isso no PowerShell na pasta do projeto:
.\scripts\deploy-tudo.ps1
```

**Pronto!** Isso faz tudo automaticamente:
1. ✅ Build das imagens
2. ✅ Push para Docker Hub
3. ✅ Deploy na AWS

---

## 📋 O QUE VOCÊ PRECISA TER

### 1. Conta no Docker Hub (GRATUITA)
- Acesse: https://hub.docker.com
- Crie uma conta (se não tiver)
- Seu username: **faquim**
- Anote sua senha

### 2. Docker instalado
- Se não tiver, baixe: https://www.docker.com/products/docker-desktop

### 3. SSH configurado para AWS
- A chave SSH já está em: `C:\Users\rapha\.ssh\LightsailDefaultKey-us-east-1.pem`

---

## 🔐 PRIMEIRA VEZ - Fazer Login no Docker Hub

**Só precisa fazer UMA VEZ:**

```powershell
docker login -u faquim
```

Ele vai pedir sua senha do Docker Hub. Digite e pronto!

---

## 🚀 DEPLOY (DEPOIS DO LOGIN)

Depois de fazer login uma vez, sempre use:

```powershell
.\scripts\deploy-tudo.ps1
```

Ou se preferir fazer passo a passo:

```powershell
# 1. Build das imagens
docker build -t faquim/formulado-api:latest -f back/Dockerfile back/
docker build -t faquim/formulado-frontend:latest -f front/Dockerfile --build-arg NEXT_PUBLIC_API_URL=http://3.238.162.190 front/

# 2. Push para Docker Hub
docker push faquim/formulado-api:latest
docker push faquim/formulado-frontend:latest

# 3. Deploy na AWS
powershell -ExecutionPolicy Bypass -File .\scripts\deploy-aws-images.ps1
```

---

## ❓ PERGUNTAS FREQUENTES

### "Onde faço login no Docker Hub?"
- No PowerShell, execute: `docker login -u faquim`
- Digite sua senha quando pedir
- Só precisa fazer uma vez!

### "Qual é minha senha do Docker Hub?"
- É a senha da sua conta no https://hub.docker.com
- Se esqueceu, recupere em: https://hub.docker.com/forgot-password

### "Onde executo os comandos?"
- No PowerShell
- Na pasta do projeto: `C:\Users\rapha\OneDrive\Documents\src\RBF-formuladobolso`

### "Preciso fazer login toda vez?"
- **NÃO!** Só precisa fazer login uma vez
- Depois disso, o Docker lembra suas credenciais

---

## 🎯 RESUMO

1. **Primeira vez:** `docker login -u faquim` (digite sua senha)
2. **Sempre:** `.\scripts\deploy-tudo.ps1`
3. **Pronto!** Acesse: http://3.238.162.190

---

## 🆘 PROBLEMAS?

### "docker: command not found"
- Instale o Docker Desktop: https://www.docker.com/products/docker-desktop

### "unauthorized: incorrect username or password"
- Faça login novamente: `docker login -u faquim`

### "Permission denied (publickey)"
- Verifique se a chave SSH está em: `C:\Users\rapha\.ssh\LightsailDefaultKey-us-east-1.pem`

