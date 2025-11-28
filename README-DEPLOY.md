# 🚀 Guia de Deploy - FormuladoBolso

## 📋 Opções de Deploy

Você tem **três opções** para fazer deploy na AWS:

### 1️⃣ Deploy Direto (Recomendado - Mais Rápido) ⚡
- **Não usa Docker Hub**
- Build local → Envia imagens via SCP → Deploy
- Mais rápido para desenvolvimento
- ✅ **MELHORADO**: Agora faz build sem cache e força atualização

### 2️⃣ Deploy com Build no Servidor (Mais Confiável) 🔒
- **Build diretamente no servidor**
- Atualiza código do repositório → Build no servidor → Deploy
- Garante que o código mais recente seja usado
- ✅ **NOVO**: Script `deploy-build-server.ps1`

### 3️⃣ Deploy via Docker Hub
- **Usa Docker Hub como intermediário**
- Build local → Push para Docker Hub → Pull no servidor → Deploy
- Mais flexível, imagens ficam disponíveis publicamente

---

## 🔧 Como Executar

### Deploy Direto (Melhorado)

```powershell
# Deploy de ambos (API + Frontend)
.\deploy-aws.ps1

# Deploy apenas da API
.\deploy-aws.ps1 api

# Deploy apenas do Frontend
.\deploy-aws.ps1 front
```

**Melhorias:**
- ✅ Build sem cache (garante código atualizado)
- ✅ Limpa imagens antigas automaticamente
- ✅ Força recriação dos containers
- ✅ Executa migrações automaticamente
- ✅ Verifica status após deploy

### Deploy com Build no Servidor (NOVO - Mais Confiável)

```powershell
# Deploy de ambos (API + Frontend)
.\scripts\deploy-build-server.ps1

# Deploy apenas da API
.\scripts\deploy-build-server.ps1 api

# Deploy apenas do Frontend
.\scripts\deploy-build-server.ps1 front
```

**Vantagens:**
- ✅ Usa código atualizado do repositório
- ✅ Build diretamente no servidor
- ✅ Não depende de imagens locais
- ✅ Mais confiável para garantir atualizações

### Docker Hub - Build e Push

```powershell
# Build e push de ambos
powershell -ExecutionPolicy Bypass -File .\build-push-dockerhub.ps1

# Build e push apenas da API
powershell -ExecutionPolicy Bypass -File .\build-push-dockerhub.ps1 api

# Build e push apenas do Frontend
powershell -ExecutionPolicy Bypass -File .\build-push-dockerhub.ps1 front
```

### Docker Hub - Deploy

```powershell
# Deploy de ambos (puxa do Docker Hub)
powershell -ExecutionPolicy Bypass -File .\deploy-dockerhub.ps1

# Deploy apenas da API
powershell -ExecutionPolicy Bypass -File .\deploy-dockerhub.ps1 api

# Deploy apenas do Frontend
powershell -ExecutionPolicy Bypass -File .\deploy-dockerhub.ps1 front
```

---

## 🔄 Fluxo Completo Docker Hub

### Primeira vez ou quando atualizar imagens:

```powershell
# 1. Build e push para Docker Hub
powershell -ExecutionPolicy Bypass -File .\build-push-dockerhub.ps1
```

### Deploy na AWS:

```powershell
# 2. Deploy usando imagens do Docker Hub
powershell -ExecutionPolicy Bypass -File .\deploy-dockerhub.ps1
```

---

## ⚙️ Configuração Docker Hub (Opcional)

Se quiser usar Docker Hub, configure:

```powershell
# Configurar username do Docker Hub
$env:DOCKER_USERNAME = "efaquim"

# Configurar senha (ou faça login manualmente)
$env:DOCKER_PASSWORD = "sua-senha-docker-hub"

# Ou faça login manualmente:
docker login -u efaquim
```

---

## 📊 Comparação

| Característica | Deploy Direto | Docker Hub |
|---------------|---------------|------------|
| **Velocidade** | ⚡ Mais rápido | 🐢 Mais lento |
| **Docker Hub** | ❌ Não usa | ✅ Usa |
| **Imagens públicas** | ❌ Não | ✅ Sim |
| **Recomendado para** | Desenvolvimento | Produção/CI |

---

## 🆘 Troubleshooting

### Atualizações não aparecem no servidor?

**Solução rápida:**
```powershell
# Use o script de build no servidor (mais confiável)
.\scripts\deploy-build-server.ps1 all
```

**Ou veja o guia completo:**
- 📖 [TROUBLESHOOTING_DEPLOY.md](docs/TROUBLESHOOTING_DEPLOY.md) - Guia completo de troubleshooting

### Erro de execução de scripts

Se aparecer erro de política de execução, use sempre:
```powershell
powershell -ExecutionPolicy Bypass -File .\nome-do-script.ps1
```

### Docker Hub - Login necessário

Se usar Docker Hub, você precisa estar logado:
```powershell
docker login -u efaquim
```

Ou configure a senha:
```powershell
$env:DOCKER_PASSWORD = "sua-senha"
```

### Verificar logs após deploy

```powershell
# Conectar no servidor e ver logs
ssh -i ~/.ssh/LightsailDefaultKey-us-east-1.pem ubuntu@3.238.162.190
cd ~/RBF-formuladobolso
docker-compose -f docker-compose.prod.yml logs -f
```

