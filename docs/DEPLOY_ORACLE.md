# 🚀 Deploy na Oracle Cloud - FormuladoBolso

Guia completo para deploy na Oracle Cloud Free Tier e automação via Make.com.

## 📋 Pré-requisitos

1. **Conta Oracle Cloud** (Free Tier)
   - Acesse: https://www.oracle.com/cloud/free/
   - Crie uma conta gratuita
   - Tenha créditos disponíveis (sempre free tier)

2. **Instância Compute criada**
   - Nome: `instance-20251126-0900` (ou similar)
   - Shape: VM.Standard.E2.1.Micro (Always Free)
   - OS: Ubuntu 22.04 ou Oracle Linux 8

3. **Chave SSH configurada**
   - Você deve ter a chave privada (.pem) para acessar a instância

4. **Make.com** (opcional, para automação)
   - Conta gratuita: https://www.make.com

## 🔧 Configuração Inicial da Instância

### 1. Conectar na Instância

```bash
# Exemplo (ajuste o IP e caminho da chave)
# Para Oracle Linux, o usuário é 'opc' (não 'ubuntu')
ssh -i ~/.ssh/oracle_key.pem opc@<IP_PUBLICO_DA_INSTANCIA>
```

### 2. Atualizar Sistema

```bash
sudo apt update && sudo apt upgrade -y
```

### 3. Instalar Dependências

**Para Oracle Linux 9:**

```bash
# Atualizar sistema
sudo dnf update -y

# Docker
sudo dnf install -y docker
sudo systemctl enable docker
sudo systemctl start docker
sudo usermod -aG docker opc

# Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Git e utilitários
sudo dnf install -y git curl wget nano

# Logout e login novamente para aplicar grupo docker
exit
```

**Nota**: No Oracle Linux, o usuário padrão é `opc` (não `ubuntu`).

### 4. Configurar Firewall Local (Opcional)

**Oracle Linux 9 usa `firewalld`:**

```bash
# Instalar firewalld (se não estiver instalado)
sudo dnf install -y firewalld
sudo systemctl enable firewalld
sudo systemctl start firewalld

# Permitir portas
sudo firewall-cmd --permanent --add-port=22/tcp   # SSH
sudo firewall-cmd --permanent --add-port=8000/tcp  # API
sudo firewall-cmd --permanent --add-port=80/tcp   # HTTP (opcional)
sudo firewall-cmd --permanent --add-port=443/tcp   # HTTPS (opcional)

# Recarregar firewall
sudo firewall-cmd --reload

# Verificar regras
sudo firewall-cmd --list-all
```

**Nota**: A configuração principal do firewall é feita na Security List do Oracle Cloud (veja Passo 5).

### 5. Configurar Security List na Oracle Cloud

1. Acesse: **Networking** > **Virtual Cloud Networks**
2. Selecione sua VCN
3. Vá em **Security Lists**
4. Edite a **Default Security List**
5. Adicione **Ingress Rules**:
   - **Source Type**: CIDR
   - **Source CIDR**: `0.0.0.0/0` (ou seu IP específico)
   - **IP Protocol**: TCP
   - **Destination Port Range**: `8000` (backend)
   - **Description**: Backend API

## 🐳 Deploy com Docker

### Opção 1: Deploy Manual

```bash
# 1. Clonar repositório
cd ~
git clone https://github.com/Raphaelbfaquim/RBF-formuladobolso.git
cd RBF-formuladobolso/back

# 2. Criar arquivo .env
cp env.example .env
nano .env  # Editar com suas configurações

# 3. Build e iniciar containers
docker-compose up -d --build

# 4. Executar migrações
docker-compose exec api alembic upgrade head

# 5. Verificar logs
docker-compose logs -f api
```

### Opção 2: Deploy com Script Automatizado

```bash
# Usar o script de deploy
cd ~/RBF-formuladobolso
chmod +x scripts/deploy-oracle.sh
./scripts/deploy-oracle.sh
```

## 🔄 Automação com Make.com

### Configuração do Cenário Make.com

1. **Acesse Make.com**: https://www.make.com
2. **Crie um novo cenário**
3. **Configure os módulos**:

#### Módulo 1: Webhook (Trigger)
- **Tipo**: Webhook > Custom webhook
- **Nome**: "GitHub Push"
- **Copie a URL do webhook** (será usada no GitHub)

#### Módulo 2: Filtro (Opcional)
- **Tipo**: Flow control > Router
- **Condição**: `{{body.ref}}` contém `refs/heads/main`
- (Apenas deploy quando push na branch main)

#### Módulo 3: SSH
- **Tipo**: Tools > SSH
- **Ação**: Execute a command
- **Configuração**:
  - **Host**: `<IP_PUBLICO_DA_INSTANCIA>`
  - **Port**: `22`
  - **Username**: `ubuntu` (ou `opc` para Oracle Linux)
  - **Authentication**: Private key
  - **Private key**: Cole sua chave privada SSH
  - **Command**: 
  ```bash
  cd ~/RBF-formuladobolso && \
  git pull origin main && \
  cd back && \
  docker-compose down && \
  docker-compose up -d --build && \
  docker-compose exec -T api alembic upgrade head
  ```

#### Módulo 4: Notificação (Opcional)
- **Tipo**: Email > Send an email
- **Para**: Seu email
- **Assunto**: "Deploy concluído - FormuladoBolso"
- **Corpo**: Status do deploy

### Configurar Webhook no GitHub

1. Acesse seu repositório no GitHub
2. Vá em **Settings** > **Webhooks**
3. Clique em **Add webhook**
4. Configure:
   - **Payload URL**: Cole a URL do webhook do Make.com
   - **Content type**: `application/json`
   - **Events**: Selecione **Just the push event**
   - **Active**: ✅
5. Clique em **Add webhook**

## 📝 Variáveis de Ambiente

Crie o arquivo `.env` na pasta `back/`:

```env
# Aplicação
APP_NAME=FormuladoBolso
APP_VERSION=0.1.0
DEBUG=False
ENVIRONMENT=production

# API
API_V1_PREFIX=/api/v1
SECRET_KEY=<gere_uma_chave_secreta_forte>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Banco de Dados
# Opção 1: PostgreSQL na própria instância (Docker)
DATABASE_URL=postgresql+asyncpg://formulado_user:formulado_pass@postgres:5432/formulado_db
DATABASE_SYNC_URL=postgresql://formulado_user:formulado_pass@postgres:5432/formulado_db

# Opção 2: Oracle Autonomous Database (Free Tier)
# DATABASE_URL=postgresql+asyncpg://user:pass@adb.region.oraclecloud.com:1521/dbname
# DATABASE_SYNC_URL=postgresql://user:pass@adb.region.oraclecloud.com:1521/dbname

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

# CORS
CORS_ORIGINS=["https://seu-frontend.vercel.app","http://localhost:3000"]

# Logging
LOG_LEVEL=INFO

# Email (SMTP)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=seu-email@gmail.com
SMTP_PASSWORD=sua-senha-app

# IA (Opcional)
OPENAI_API_KEY=sk-your-key
# ou
ANTHROPIC_API_KEY=sk-ant-your-key
```

## 🌐 Configurar Domínio (Opcional)

### Com Nginx Reverse Proxy

```bash
# Instalar Nginx
sudo apt install -y nginx

# Criar configuração
sudo nano /etc/nginx/sites-available/formulado-bolso
```

Conteúdo do arquivo:

```nginx
server {
    listen 80;
    server_name seu-dominio.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Ativar site
sudo ln -s /etc/nginx/sites-available/formulado-bolso /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Instalar Certbot para HTTPS
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d seu-dominio.com
```

## 🔍 Verificação e Monitoramento

### Verificar Status

```bash
# Status dos containers
docker-compose ps

# Logs do backend
docker-compose logs -f api

# Logs do banco
docker-compose logs -f postgres

# Verificar saúde da API
curl http://localhost:8000/health
```

### Comandos Úteis

```bash
# Reiniciar serviços
docker-compose restart

# Parar serviços
docker-compose down

# Ver logs em tempo real
docker-compose logs -f

# Executar migrações
docker-compose exec api alembic upgrade head

# Criar nova migração
docker-compose exec api alembic revision --autogenerate -m "descricao"

# Acessar shell do container
docker-compose exec api bash

# Backup do banco
docker-compose exec postgres pg_dump -U formulado_user formulado_db > backup.sql
```

## 🚨 Troubleshooting

### Problema: Container não inicia

```bash
# Verificar logs
docker-compose logs api

# Verificar se porta está em uso
sudo netstat -tulpn | grep 8000

# Verificar configurações
docker-compose config
```

### Problema: Erro de conexão com banco

```bash
# Verificar se PostgreSQL está rodando
docker-compose ps postgres

# Verificar logs do PostgreSQL
docker-compose logs postgres

# Testar conexão
docker-compose exec api python -c "from sqlalchemy import create_engine; engine = create_engine('postgresql://formulado_user:formulado_pass@postgres:5432/formulado_db'); print('OK' if engine.connect() else 'ERRO')"
```

### Problema: Make.com não conecta via SSH

1. Verificar se a chave SSH está correta
2. Verificar se o IP público está correto
3. Verificar Security List na Oracle Cloud
4. Testar conexão manual:
   ```bash
   ssh -i ~/.ssh/oracle_key.pem ubuntu@<IP>
   ```

### Problema: API não responde externamente

1. Verificar firewall local:
   ```bash
   sudo ufw status
   ```

2. Verificar Security List na Oracle Cloud
3. Verificar se o container está escutando em `0.0.0.0`:
   ```bash
   docker-compose exec api netstat -tulpn
   ```

## 📊 Recursos Oracle Cloud Free Tier

### Compute Instance
- **Shape**: VM.Standard.E2.1.Micro
- **OCPU**: 1/8 OCPU
- **RAM**: 1 GB
- **Armazenamento**: 50 GB
- **Bandwidth**: 10 TB/mês

### Autonomous Database (Opcional)
- **Storage**: 2 TB
- **OCPU**: 2
- **Sempre gratuito** (com limites)

## 🔐 Segurança

1. **Mude as senhas padrão** no `.env`
2. **Use HTTPS** com Let's Encrypt (Certbot)
3. **Configure firewall** adequadamente
4. **Mantenha o sistema atualizado**:
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```
5. **Faça backups regulares** do banco de dados
6. **Use variáveis de ambiente** seguras (não commite `.env`)

## 📚 Links Úteis

- Oracle Cloud Console: https://cloud.oracle.com
- Make.com: https://www.make.com
- Docker Docs: https://docs.docker.com
- Nginx Docs: https://nginx.org/en/docs/

---

**Deploy automatizado na Oracle Cloud!** 🎉

