# ☁️ Deploy na AWS - FormuladoBolso

Guia completo para configurar e fazer deploy na AWS (Amazon Web Services).

## 💰 Opções Mais Baratas na AWS (Sem Free Tier)

### 1. **AWS Lightsail** 💡 MAIS SIMPLES E BARATO ⭐ RECOMENDADO
- **$3.50/mês** (~R$ 18/mês) - 512MB RAM, 1 vCPU
  - ⚠️ Pode ser limitado para Docker
- **$5/mês** (~R$ 25/mês) - 1GB RAM, 1 vCPU ✅ **MELHOR CUSTO-BENEFÍCIO**
- **$10/mês** (~R$ 50/mês) - 2GB RAM, 1 vCPU (melhor performance)
- Interface mais simples que EC2
- Inclui IP estático e firewall
- **Sem surpresas na fatura** (preço fixo)

### 2. **EC2 t2.micro** (pago)
- **~$8-10/mês** (~R$ 40-50/mês)
- 1 vCPU, 1GB RAM
- Mais flexível, mas mais caro que Lightsail

### 3. **EC2 t2.nano** (pago)
- **~$4-5/mês** (~R$ 20-25/mês)
- 0.5 vCPU, 512MB RAM
- Muito limitado (não recomendado)

## 🎯 Recomendação

**Melhor opção**: **AWS Lightsail $5/mês** (1GB RAM)
- Preço fixo, sem surpresas
- Interface simples
- Suficiente para o projeto
- Mais barato que EC2 t2.micro

## 📋 Passo 1: Criar Conta AWS

1. Acesse: https://aws.amazon.com
2. Clique em **"Create an AWS Account"** ou **"Criar uma Conta AWS"**
3. Preencha seus dados
4. Adicione método de pagamento (necessário mesmo para Free Tier)
5. Verifique identidade por telefone
6. Escolha plano: **Basic Support - Free**
7. Aguarde ativação (pode levar algumas horas)

## 🖥️ Opção A: AWS EC2 (Free Tier)

### Passo 1: Criar Instância EC2

1. Acesse: https://console.aws.amazon.com/ec2
2. Clique em **"Launch Instance"** ou **"Iniciar Instância"**

### Passo 2: Configurar Instância

#### Nome e Tags
- **Name**: `formulado-bolso-backend`

#### Imagem (AMI)
- **Amazon Linux 2023** (recomendado, otimizado para AWS)
- Ou **Ubuntu Server 22.04 LTS**

#### Tipo de Instância
- **t2.micro** ou **t3.micro** (Free Tier elegível)
- 1 vCPU, 1GB RAM

#### Par de Chaves (Key Pair)
- Clique em **"Create new key pair"**
- **Name**: `formulado-bolso-key`
- **Key pair type**: RSA
- **Private key file format**: `.pem`
- Clique em **"Create key pair"**
- **Baixe o arquivo .pem** (você precisará dele!)

#### Configurações de Rede
- **VPC**: Deixe padrão
- **Subnet**: Deixe padrão
- **Auto-assign Public IP**: **Enable**
- **Security Group**: Clique em **"Create security group"**
  - **Name**: `formulado-bolso-sg`
  - **Description**: `Security group for FormuladoBolso`
  - Adicione regras:
    - **SSH (22)**: My IP (ou 0.0.0.0/0 se quiser acessar de qualquer lugar)
    - **Custom TCP (8000)**: 0.0.0.0/0 (API Backend)

#### Armazenamento
- **8GB gp3** (Free Tier inclui 30GB/mês)

### Passo 3: Iniciar Instância

1. Clique em **"Launch Instance"**
2. Aguarde criação (1-2 minutos)
3. Clique em **"View all instances"**
4. Anote o **Public IPv4 address**

## 🖥️ Opção B: AWS Lightsail (Mais Simples)

### Passo 1: Criar Instância Lightsail

1. Acesse: https://lightsail.aws.amazon.com
2. Clique em **"Create instance"**

### Passo 2: Configurar

#### Localização
- Escolha região mais próxima (ex: **US East - N. Virginia**)

#### Plataforma
- **Linux/Unix**

#### Imagem
- **Ubuntu 22.04 LTS**

#### Plano
- **$5/mês** - 1GB RAM, 1 vCPU, 40GB SSD ✅ Recomendado
- Ou **$3.50/mês** - 512MB RAM (pode ser limitado)

#### Nome
- **formulado-bolso-backend**

### Passo 3: Criar

1. Clique em **"Create instance"**
2. Aguarde criação (1-2 minutos)
3. Anote o **IP público** (já está configurado!)

### Passo 4: Configurar Firewall (Lightsail)

1. Clique na instância
2. Vá em **"Networking"**
3. Adicione regras:
   - **SSH (22)**: Seu IP
   - **Custom (8000)**: 0.0.0.0/0

## 🔑 Passo 5: Conectar na Instância

### Para EC2:

```bash
# Conectar (ajuste o caminho da chave)
ssh -i ~/Downloads/formulado-bolso-key.pem ec2-user@<IP_PUBLICO>
# ou para Ubuntu:
ssh -i ~/Downloads/formulado-bolso-key.pem ubuntu@<IP_PUBLICO>
```

### Para Lightsail:

1. No Lightsail, clique na instância
2. Clique em **"Connect using SSH"** (abre no navegador)
3. Ou use SSH normal:
```bash
ssh -i ~/Downloads/formulado-bolso-key.pem ubuntu@<IP_PUBLICO>
```

## 📦 Passo 6: Configurar Servidor

### Para Amazon Linux 2023:

```bash
# 1. Atualizar sistema
sudo dnf update -y

# 2. Instalar Docker
sudo dnf install -y docker
sudo systemctl enable docker
sudo systemctl start docker
sudo usermod -aG docker ec2-user

# 3. Instalar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 4. Instalar Git
sudo dnf install -y git

# 5. Logout e login novamente
exit
```

### Para Ubuntu (Lightsail ou EC2):

```bash
# 1. Atualizar sistema
sudo apt update && sudo apt upgrade -y

# 2. Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu

# 3. Instalar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 4. Instalar Git
sudo apt install -y git

# 5. Logout e login novamente
exit
```

## 📥 Passo 7: Clonar e Configurar Projeto

```bash
# Reconectar
ssh -i ~/Downloads/formulado-bolso-key.pem ec2-user@<IP_PUBLICO>
# ou
ssh -i ~/Downloads/formulado-bolso-key.pem ubuntu@<IP_PUBLICO>

# Clonar repositório
cd ~
git clone https://github.com/Raphaelbfaquim/RBF-formuladobolso.git
cd RBF-formuladobolso/back

# Criar .env
cp env.example .env
nano .env  # Edite com suas configurações
```

## 🐳 Passo 8: Deploy Inicial

```bash
# Build e iniciar containers
docker-compose up -d --build

# Aguardar serviços
sleep 15

# Executar migrações
docker-compose exec -T api alembic upgrade head

# Verificar status
docker-compose ps

# Ver logs
docker-compose logs -f api
```

## 🔄 Passo 9: Configurar GitHub Actions

1. No GitHub, vá em **Settings** > **Secrets** > **Actions**
2. Adicione:
   - `AWS_HOST`: IP público da instância
   - `AWS_USER`: `ec2-user` (Amazon Linux) ou `ubuntu` (Ubuntu)
   - `AWS_SSH_PRIVATE_KEY`: Conteúdo do arquivo .pem

3. Use o workflow `.github/workflows/deploy-aws.yml` (vou criar)

## 💰 Custos Estimados (Sem Free Tier)

### Opções Pagas
- **Lightsail $3.50**: $3.50/mês (~R$ 18/mês) - 512MB RAM
- **Lightsail $5**: $5/mês (~R$ 25/mês) - 1GB RAM ✅ Recomendado
- **Lightsail $10**: $10/mês (~R$ 50/mês) - 2GB RAM
- **EC2 t2.micro**: ~$8-10/mês (~R$ 40-50/mês) - 1GB RAM
- **EC2 t2.nano**: ~$4-5/mês (~R$ 20-25/mês) - 512MB RAM

## 🔍 Verificar se Está Funcionando

```bash
# Verificar saúde da API
curl http://localhost:8000/health

# Verificar de fora
curl http://<IP_PUBLICO>:8000/health
```

## 🚨 Troubleshooting

### Problema: Não consigo conectar via SSH

**Soluções:**
1. Verifique Security Group (EC2) ou Firewall (Lightsail)
2. Verifique se o IP está correto
3. Verifique permissões da chave: `chmod 400 formulado-bolso-key.pem`

### Problema: Porta 8000 não acessível

**Soluções:**
1. Verifique Security Group (adicionar regra porta 8000)
2. Verifique se container está rodando: `docker-compose ps`
3. Verifique logs: `docker-compose logs api`

## 📚 Links Úteis

- AWS Console: https://console.aws.amazon.com
- EC2 Console: https://console.aws.amazon.com/ec2
- Lightsail: https://lightsail.aws.amazon.com
- AWS Free Tier: https://aws.amazon.com/free

---

**Deploy na AWS configurado!** 🎉

Recomendo usar **Lightsail $5/mês** - melhor custo-benefício sem free tier!

