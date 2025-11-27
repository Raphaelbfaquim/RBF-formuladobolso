# 🚀 Automação de Deploy com GitHub Actions

Guia para configurar deploy automático na Oracle Cloud usando GitHub Actions (nativo do GitHub, gratuito).

## 🎯 Como Funciona

Quando você faz `git push origin main`, o GitHub Actions:
1. Detecta o push na branch `main`
2. Conecta via SSH na sua instância Oracle Cloud
3. Atualiza o código (`git pull`)
4. Reconstrói e reinicia os containers Docker
5. Executa migrações do banco de dados
6. Verifica se tudo está funcionando

## 📋 Pré-requisitos

1. **Instância Oracle Cloud configurada**
   - Docker e Docker Compose instalados
   - Repositório clonado (ou será clonado automaticamente)
   - SSH funcionando

2. **Chave SSH privada**
   - A chave que você usa para conectar na instância

3. **IP público da instância**
   - Você pode ver no Oracle Cloud Console

## 🔧 Configuração (5 minutos)

### Passo 1: Adicionar Secrets no GitHub

1. Acesse seu repositório: https://github.com/Raphaelbfaquim/RBF-formuladobolso
2. Vá em **Settings** (Configurações)
3. No menu lateral, clique em **Secrets and variables** > **Actions**
4. Clique em **New repository secret**
5. Adicione os seguintes secrets:

#### Secret 1: `ORACLE_HOST`
- **Name**: `ORACLE_HOST`
- **Value**: IP público da sua instância Oracle Cloud
  - Exemplo: `129.213.xxx.xxx`
- Clique em **Add secret**

#### Secret 2: `ORACLE_USER`
- **Name**: `ORACLE_USER`
- **Value**: `opc` (usuário padrão do Oracle Linux)
- Clique em **Add secret**

#### Secret 3: `ORACLE_SSH_PRIVATE_KEY`
- **Name**: `ORACLE_SSH_PRIVATE_KEY`
- **Value**: Cole sua chave privada SSH completa
  ```bash
  -----BEGIN RSA PRIVATE KEY-----
  MIIEpAIBAAKCAQEA...
  (todo o conteúdo da chave)
  ...
  -----END RSA PRIVATE KEY-----
  ```
- Clique em **Add secret**

### Passo 2: Verificar Workflow

O arquivo `.github/workflows/deploy-oracle.yml` já está criado e configurado!

### Passo 3: Configurar IP Público na Oracle Cloud

**IMPORTANTE**: Antes de conectar, você precisa configurar um IP público:

1. No Oracle Cloud Console, vá em **Networking** > **Virtual Cloud Networks**
2. Selecione sua VCN: `vcn-20251126-0905`
3. Vá em **Subnets** e selecione a subnet da sua instância
4. Vá em **Security Lists** > **Default Security List**
5. Adicione **Ingress Rules**:
   - **Source Type**: CIDR
   - **Source CIDR**: `0.0.0.0/0` (ou seu IP específico para mais segurança)
   - **IP Protocol**: TCP
   - **Destination Port Range**: `22` (SSH)
   - **Description**: SSH Access
6. Adicione outra regra para a API:
   - **Destination Port Range**: `8000` (Backend API)

7. Volte para sua instância e configure o IP público:
   - Vá em **Networking** > **IP Reservations**
   - Clique em **Create Reserved Public IP**
   - Selecione **Ephemeral** ou **Reserved** (reserved é melhor)
   - Anote o IP público atribuído

### Passo 4: Configurar Instância Oracle Cloud (Primeira vez)

Conecte na sua instância e configure:

```bash
# Conectar (use o IP público que você configurou)
ssh -i ~/.ssh/sua_chave.pem opc@<IP_PUBLICO>

# Atualizar sistema (Oracle Linux 9)
sudo dnf update -y

# Instalar Git (se não estiver instalado)
sudo dnf install -y git

# Instalar Docker
sudo dnf install -y docker
sudo systemctl enable docker
sudo systemctl start docker
sudo usermod -aG docker opc

# Instalar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Instalar dependências adicionais (para Docker)
sudo dnf install -y curl

# Clonar repositório
cd ~
git clone https://github.com/Raphaelbfaquim/RBF-formuladobolso.git
cd RBF-formuladobolso/back

# Criar .env (IMPORTANTE!)
cp env.example .env
nano .env  # Edite com suas configurações

# Fazer logout e login novamente para aplicar grupo docker
exit
```

**Nota**: No Oracle Linux, o usuário padrão é `opc` (não `ubuntu`).

### Passo 5: Testar

Faça um commit e push:

```bash
git commit --allow-empty -m "Test GitHub Actions deploy"
git push origin main
```

### Passo 6: Verificar Deploy

1. No GitHub, vá em **Actions** (aba no topo)
2. Clique no workflow **"Deploy to Oracle Cloud"**
3. Veja os logs em tempo real
4. Se tudo der certo, verá ✅ verde

## 🔍 Como Funciona o Workflow

O workflow está configurado para:

- **Trigger**: Push na branch `main` quando há mudanças em `back/**`
- **Execução manual**: Também pode ser executado manualmente (Actions > Run workflow)
- **Steps**:
  1. Checkout do código
  2. Setup SSH
  3. Deploy na Oracle Cloud
  4. Verificação do deploy

## 📝 Comandos Executados no Deploy

O workflow executa automaticamente:

```bash
cd ~/RBF-formuladobolso
git pull origin main
cd back
docker-compose down
docker-compose up -d --build
# Aguarda PostgreSQL
docker-compose exec -T api alembic upgrade head
# Verifica saúde
curl http://localhost:8000/health
```

## 🚨 Troubleshooting

### Problema: Workflow falha no SSH

**Soluções:**
1. Verifique se `ORACLE_HOST` está correto (IP público configurado)
2. Verifique se `ORACLE_USER` está correto (`opc` para Oracle Linux)
3. Verifique se `ORACLE_SSH_PRIVATE_KEY` está completa (incluindo headers)
4. Verifique se o IP público está configurado na instância
5. Verifique se a Security List permite SSH (porta 22)
6. Teste conexão manual:
   ```bash
   ssh -i ~/.ssh/sua_chave.pem opc@<IP_PUBLICO>
   ```

### Problema: Erro "docker-compose: command not found"

**Solução:**
- Docker Compose não está instalado na instância
- Execute na instância (Oracle Linux):
  ```bash
  sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
  sudo chmod +x /usr/local/bin/docker-compose
  ```
  
### Problema: Erro "Docker não está rodando"

**Solução:**
- Inicie o serviço Docker:
  ```bash
  sudo systemctl start docker
  sudo systemctl enable docker
  ```

### Problema: Erro "permission denied" no Docker

**Solução:**
- Usuário não está no grupo docker
- Execute na instância:
  ```bash
  sudo usermod -aG docker $USER
  # Faça logout e login novamente
  ```

### Problema: Arquivo .env não encontrado

**Solução:**
- O workflow cria automaticamente a partir do `env.example`
- **IMPORTANTE**: Configure o `.env` na instância antes do próximo deploy
- Conecte na instância e edite:
  ```bash
  ssh -i ~/.ssh/sua_chave.pem ubuntu@<IP>
  cd ~/RBF-formuladobolso/back
  nano .env
  ```

### Problema: Deploy muito lento

**Soluções:**
1. O primeiro deploy é mais lento (build das imagens)
2. Deploys seguintes são mais rápidos (cache do Docker)
3. Se quiser acelerar, remova `--build` do workflow (só rebuilda se necessário)

## 🔐 Segurança

### Boas Práticas

1. **Nunca commite secrets** no código
2. **Use GitHub Secrets** para dados sensíveis
3. **Limite acesso SSH** na instância (firewall)
4. **Monitore os logs** do workflow regularmente
5. **Use chaves SSH** ao invés de senhas

### Rotacionar Chave SSH

Se precisar trocar a chave SSH:

1. Gere nova chave na instância:
   ```bash
   ssh-keygen -t rsa -b 4096 -f ~/.ssh/new_key
   ```
2. Adicione a chave pública ao `authorized_keys`
3. Atualize o secret `ORACLE_SSH_PRIVATE_KEY` no GitHub

## 📊 Monitoramento

### Ver Histórico de Deploys

1. No GitHub, vá em **Actions**
2. Veja todos os workflows executados
3. Clique em um para ver detalhes e logs

### Notificações

Você pode configurar notificações por email:
1. GitHub Settings > Notifications
2. Marque "Actions" para receber emails

## 🎯 Execução Manual

Você pode executar o workflow manualmente:

1. Vá em **Actions** no GitHub
2. Clique em **"Deploy to Oracle Cloud"**
3. Clique em **"Run workflow"**
4. Selecione a branch (`main`)
5. Clique em **"Run workflow"**

## 🔄 Deploy Apenas em Mudanças Específicas

O workflow já está configurado para executar apenas quando há mudanças em:
- `back/**` (qualquer arquivo na pasta back)
- `.github/workflows/deploy-oracle.yml` (o próprio workflow)

Se quiser mudar, edite o arquivo `.github/workflows/deploy-oracle.yml`:

```yaml
on:
  push:
    branches: [main]
    paths:
      - 'back/**'  # Apenas mudanças no backend
      # Adicione outros paths se necessário
```

## 📚 Recursos

- **GitHub Actions Docs**: https://docs.github.com/en/actions
- **Workflow Syntax**: https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions

---

**Pronto!** Agora cada `git push origin main` faz deploy automático! 🚀

