# 🐳 Deploy usando Docker Hub (Build Local)

Esta é a **melhor abordagem** para deploy: você builda as imagens na sua máquina (mais rápida) e apenas faz pull na instância AWS.

## ✅ Vantagens

- ⚡ **Build mais rápido** - Sua máquina tem mais recursos que a instância AWS
- 💰 **Economia de recursos** - Instância AWS não fica lenta durante build
- 🔄 **Reutilização** - Imagens podem ser usadas em múltiplos ambientes
- 🚀 **Deploy rápido** - Apenas pull e run na instância

## 📋 Pré-requisitos

1. **Conta no Docker Hub** (gratuita): https://hub.docker.com
2. **Docker instalado** na sua máquina local
3. **SSH configurado** para a instância AWS

## 🚀 Passo a Passo

### 1. Login no Docker Hub

```bash
docker login
# Digite seu username e password do Docker Hub
```

### 2. Buildar e fazer push das imagens

```bash
# Opção 1: Usando Makefile
make docker-build

# Opção 2: Direto
bash scripts/build-and-push.sh
```

Isso vai:
- Buildar a imagem da API
- Buildar a imagem do Frontend
- Fazer push para Docker Hub

**Tempo estimado:** 5-10 minutos (depende da sua conexão)

### 3. Configurar variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto (ou exporte as variáveis):

```bash
export DOCKER_USERNAME=seu-usuario-docker-hub
export DOCKER_PASSWORD=sua-senha-docker-hub
export IMAGE_TAG=latest
export AWS_HOST=ubuntu@3.238.162.190
export AWS_SSH_KEY=~/.ssh/LightsailDefaultKey-us-east-1.pem
```

### 4. Deploy na AWS

```bash
# Opção 1: Usando Makefile
make docker-deploy

# Opção 2: Direto
bash scripts/deploy-aws-images.sh
```

Isso vai:
- Conectar na instância AWS
- Fazer pull das imagens do Docker Hub
- Iniciar os containers
- Executar migrações

**Tempo estimado:** 2-3 minutos (muito mais rápido!)

## 🔄 Workflow Completo

```bash
# 1. Fazer alterações no código
# ... editar arquivos ...

# 2. Commit e push
git add .
git commit -m "Minhas alterações"
git push origin main

# 3. Buildar e fazer push das imagens
make docker-build

# 4. Deploy na AWS
make docker-deploy
```

## 📝 Configuração Avançada

### Usar tags diferentes

```bash
export IMAGE_TAG=v1.0.0
make docker-build
make docker-deploy
```

### Usar Docker Hub privado

Edite `scripts/build-and-push.sh` e `scripts/deploy-aws-images.sh` para usar seu registry privado.

### Automatizar com GitHub Actions

Veja `.github/workflows/docker-build-push.yml` (criar se necessário).

## 🆚 Comparação: Build Local vs Build na Instância

| Aspecto | Build Local (Docker Hub) | Build na Instância |
|---------|-------------------------|-------------------|
| **Velocidade** | ⚡ Rápido (5-10 min) | 🐌 Lento (15-30 min) |
| **Recursos** | 💪 Sua máquina | 💸 Instância AWS |
| **Instância lenta?** | ❌ Não | ✅ Sim |
| **Reutilização** | ✅ Sim | ❌ Não |
| **Complexidade** | 🟡 Média | 🟢 Simples |

## 🐛 Troubleshooting

### Erro: "permission denied" no Docker Hub

```bash
docker login
# Verifique username e password
```

### Erro: "image not found" na instância

```bash
# Verifique se o push foi feito corretamente
docker images | grep formulado

# Verifique se está logado na instância
ssh ubuntu@3.238.162.190
docker login
```

### Imagens muito grandes

```bash
# Use .dockerignore para excluir arquivos desnecessários
# Veja: front/.dockerignore e back/.dockerignore
```

## 💡 Dicas

1. **Use tags semânticas** para versionamento: `v1.0.0`, `v1.0.1`, etc.
2. **Limpe imagens antigas** periodicamente no Docker Hub
3. **Use GitHub Actions** para automatizar build e push
4. **Monitore o uso** do Docker Hub (plano gratuito tem limites)

## 📚 Próximos Passos

- [ ] Configurar GitHub Actions para build automático
- [ ] Usar tags semânticas para versionamento
- [ ] Configurar CI/CD completo
- [ ] Considerar AWS ECR (se usar muito)

