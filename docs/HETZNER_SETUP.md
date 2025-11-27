# 🚀 Deploy no Hetzner Cloud - FormuladoBolso

Guia completo para configurar e fazer deploy na Hetzner Cloud (servidores baratos com mais RAM).

## 💰 Por que Hetzner?

- **Servidores baratos**: A partir de €3/mês (~R$ 16/mês)
- **Mais RAM**: 2GB+ (vs 503MB da Oracle Free Tier)
- **Melhor performance**: Instalação de Docker funciona sem problemas
- **Localização**: Servidores na Europa (baixa latência)

## 📋 Passo 1: Criar Conta no Hetzner

1. Acesse: https://console.hetzner.com
2. Clique em **"Sign up"** ou **"Registrar"**
3. Preencha seus dados
4. Verifique seu email
5. Faça login

## 🖥️ Passo 2: Criar Servidor Cloud

1. No painel, clique em **"Add Server"** ou **"Adicionar Servidor"**
2. Configure:

### Localização
- Escolha: **Falkenstein** (Alemanha) ou **Nuremberg** (Alemanha)
- Ou **Helsinki** (Finlândia) se quiser mais próximo

### Imagem
- **Image**: Ubuntu 22.04 (ou 24.04)
- Ou **Debian 12** se preferir

### Tipo
- **CX11**: 1 vCPU, 2GB RAM, 20GB SSD - **€3.29/mês** (~R$ 18/mês) ✅ Recomendado
- **CX21**: 2 vCPU, 4GB RAM, 40GB SSD - **€5.83/mês** (~R$ 32/mês) (melhor performance)

### SSH Keys
- Clique em **"Add SSH Key"**
- Cole sua chave pública SSH (ou gere uma nova)
- Ou deixe em branco e use senha (menos seguro)

### Nome do Servidor
- **Name**: `formulado-bolso` ou `formulado-bolso-backend`

3. Clique em **"Create & Buy Now"**
4. Aguarde criação (30-60 segundos)

## 🔑 Passo 3: Obter IP e Credenciais

1. Após criar, você verá:
   - **IP Público**: Anote este IP (ex: `123.45.67.89`)
   - **Usuário**: `root` (Ubuntu/Debian)
   - **Senha**: Se não usou SSH key, a senha será exibida

## 🔐 Passo 4: Conectar no Servidor

### Se você usou SSH Key:

```bash
ssh root@<IP_PUBLICO>
```

### Se você usou senha:

```bash
ssh root@<IP_PUBLICO>
# Digite a senha quando solicitado
```

## 📦 Passo 5: Configurar Servidor

Conectado no servidor, execute:

```bash
# 1. Atualizar sistema
apt update && apt upgrade -y

# 2. Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# 3. Instalar Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# 4. Instalar Git
apt install -y git

# 5. Verificar instalação
docker --version
git --version
docker-compose --version
```

## 📥 Passo 6: Clonar e Configurar Projeto

```bash
# 1. Clonar repositório
cd /root
git clone https://github.com/Raphaelbfaquim/RBF-formuladobolso.git
cd RBF-formuladobolso/back

# 2. Criar arquivo .env
cp env.example .env
nano .env  # Edite com suas configurações
```

## 🐳 Passo 7: Deploy Inicial

```bash
# 1. Build e iniciar containers
docker-compose up -d --build

# 2. Aguardar serviços iniciarem
sleep 15

# 3. Executar migrações
docker-compose exec -T api alembic upgrade head

# 4. Verificar status
docker-compose ps

# 5. Ver logs
docker-compose logs -f api
```

## 🔒 Passo 8: Configurar Firewall (Opcional)

Hetzner tem firewall integrado. Configure no painel:

1. Vá em **"Firewalls"** no painel
2. Crie uma nova regra ou edite a padrão
3. Adicione regras:
   - **SSH (22)**: Permitir do seu IP
   - **API (8000)**: Permitir de qualquer lugar (0.0.0.0/0)
   - **HTTP (80)**: Permitir de qualquer lugar (se usar Nginx)
   - **HTTPS (443)**: Permitir de qualquer lugar (se usar HTTPS)

## 🔄 Passo 9: Configurar GitHub Actions

Atualize os secrets no GitHub:

1. Vá em **Settings** > **Secrets and variables** > **Actions**
2. Atualize:
   - `ORACLE_HOST` → `HETZNER_HOST`: IP do servidor Hetzner
   - `ORACLE_USER` → `HETZNER_USER`: `root`
   - `ORACLE_SSH_PRIVATE_KEY` → `HETZNER_SSH_PRIVATE_KEY`: Sua chave privada SSH

3. Atualize o workflow `.github/workflows/deploy-oracle.yml`:
   - Mude `ORACLE_HOST` para `HETZNER_HOST`
   - Mude `ORACLE_USER` para `HETZNER_USER` (ou crie um novo workflow)

## 💰 Custos

### CX11 (Recomendado)
- **€3.29/mês** (~R$ 18/mês)
- 1 vCPU, 2GB RAM, 20GB SSD
- Suficiente para o projeto

### CX21 (Melhor Performance)
- **€5.83/mês** (~R$ 32/mês)
- 2 vCPU, 4GB RAM, 40GB SSD
- Melhor para produção

## 🔍 Verificar se Está Funcionando

```bash
# Verificar saúde da API
curl http://localhost:8000/health

# Verificar de fora (use o IP público)
curl http://<IP_PUBLICO>:8000/health
```

## 📚 Próximos Passos

1. Configure domínio (opcional)
2. Configure HTTPS com Let's Encrypt (opcional)
3. Configure backups automáticos
4. Configure monitoramento

## 🚨 Troubleshooting

### Problema: Não consigo conectar via SSH

**Soluções:**
1. Verifique se o firewall permite SSH
2. Verifique se o IP está correto
3. Teste com: `ping <IP_PUBLICO>`

### Problema: Docker não instala

**Solução:**
- O script oficial do Docker funciona perfeitamente no Hetzner
- Se der erro, tente: `apt install -y docker.io docker-compose`

### Problema: Porta 8000 não acessível

**Soluções:**
1. Verifique firewall no painel Hetzner
2. Verifique se o container está rodando: `docker-compose ps`
3. Verifique logs: `docker-compose logs api`

---

**Deploy no Hetzner configurado!** 🎉

Muito mais fácil que a Oracle Free Tier com apenas 503MB de RAM!

