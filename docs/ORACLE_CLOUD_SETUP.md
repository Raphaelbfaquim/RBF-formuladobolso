# ☁️ Configuração Inicial da Instância Oracle Cloud

Guia específico para configurar sua instância Oracle Linux 9 na Oracle Cloud.

## 📋 Informações da Sua Instância

- **Sistema Operacional**: Oracle Linux 9
- **Usuário**: `opc`
- **Região**: sa-saopaulo-1 (São Paulo)
- **Forma**: VM.Standard.E2.1.Micro (Always Free)
- **VCN**: vcn-20251126-0905
- **OCID**: ocid1.instance.oc1.sa-saopaulo-1.antxeljrhi5kvwqcsmzssim3x75rlpw22oyxvskeyezaosyqchp6byb6wkxq

## 🔧 Passo 1: Configurar IP Público

### Opção A: IP Público Temporário (Ephemeral)

1. No Oracle Cloud Console, vá em **Compute** > **Instances**
2. Clique na sua instância: `instance-20251126-0900`
3. Na seção **Attached VNICs**, clique no link da VNIC
4. Clique em **IPv4 Addresses**
5. Clique nos **3 pontos** ao lado do IP privado
6. Selecione **Edit**
7. Marque **Assign a public IPv4 address**
8. Selecione **Ephemeral Public IP**
9. Clique em **Update**
10. **Anote o IP público** que foi atribuído

### Opção B: IP Público Reservado (Recomendado)

1. Vá em **Networking** > **IP Reservations**
2. Clique em **Create Reserved Public IP**
3. Configure:
   - **Name**: `formulado-bolso-ip`
   - **Type**: **Reserved**
   - **Compartment**: Seu compartimento
4. Clique em **Create**
5. Volte para a VNIC da instância
6. Edite o IPv4 Address
7. Selecione **Assign a public IPv4 address**
8. Selecione o IP reservado que você criou
9. Clique em **Update**

## 🔒 Passo 2: Configurar Security List (Firewall)

1. Vá em **Networking** > **Virtual Cloud Networks**
2. Selecione: `vcn-20251126-0905`
3. Clique em **Security Lists**
4. Selecione **Default Security List**
5. Clique em **Add Ingress Rules**

### Regra 1: SSH (Porta 22)

- **Source Type**: CIDR
- **Source CIDR**: `0.0.0.0/0` (ou seu IP específico para mais segurança)
- **IP Protocol**: TCP
- **Destination Port Range**: `22`
- **Description**: `SSH Access`
- Clique em **Add Ingress Rules**

### Regra 2: Backend API (Porta 8000)

- **Source Type**: CIDR
- **Source CIDR**: `0.0.0.0/0` (ou apenas IPs que precisam acessar)
- **IP Protocol**: TCP
- **Destination Port Range**: `8000`
- **Description**: `Backend API`
- Clique em **Add Ingress Rules**

### Regra 3: HTTP (Porta 80) - Opcional

Se quiser usar Nginx como proxy reverso:

- **Source Type**: CIDR
- **Source CIDR**: `0.0.0.0/0`
- **IP Protocol**: TCP
- **Destination Port Range**: `80`
- **Description**: `HTTP`
- Clique em **Add Ingress Rules**

### Regra 4: HTTPS (Porta 443) - Opcional

- **Source Type**: CIDR
- **Source CIDR**: `0.0.0.0/0`
- **IP Protocol**: TCP
- **Destination Port Range**: `443`
- **Description**: `HTTPS`
- Clique em **Add Ingress Rules**

## 🔑 Passo 3: Obter Chave SSH

Se você ainda não tem a chave SSH:

1. No Oracle Cloud Console, vá na sua instância
2. Na seção **Instance Access**, você verá informações sobre SSH
3. Se você criou a instância com uma chave, baixe ela
4. Se não, você precisa adicionar uma chave SSH:

### Adicionar Chave SSH Existente

1. Vá em **Compute** > **Instances** > Sua instância
2. Clique em **Edit**
3. Na seção **Add SSH Keys**, cole sua chave pública SSH
4. Clique em **Save Changes**

### Gerar Nova Chave SSH (Windows)

```powershell
# No PowerShell do Windows
ssh-keygen -t rsa -b 4096 -f ~/.ssh/oracle_key

# Ver a chave pública (para adicionar no Oracle Cloud)
cat ~/.ssh/oracle_key.pub

# Ver a chave privada (para usar no GitHub Secrets)
cat ~/.ssh/oracle_key
```

## 🚀 Passo 4: Conectar na Instância

```bash
# No Windows (PowerShell ou Git Bash)
ssh -i ~/.ssh/oracle_key opc@<IP_PUBLICO>
```

Substitua `<IP_PUBLICO>` pelo IP que você configurou no Passo 1.

## 📦 Passo 5: Instalar Dependências

Conectado na instância, execute:

```bash
# Atualizar sistema
sudo dnf update -y

# Instalar Git
sudo dnf install -y git

# Instalar Docker
sudo dnf install -y docker
sudo systemctl enable docker
sudo systemctl start docker
sudo usermod -aG docker opc

# Verificar Docker
docker --version

# Instalar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verificar Docker Compose
docker-compose --version

# Instalar dependências adicionais
sudo dnf install -y curl wget nano
```

## 📥 Passo 6: Clonar Repositório

```bash
cd ~
git clone https://github.com/Raphaelbfaquim/RBF-formuladobolso.git
cd RBF-formuladobolso/back
```

## ⚙️ Passo 7: Configurar Ambiente

```bash
# Criar arquivo .env
cp env.example .env

# Editar .env
nano .env
```

Configure as variáveis de ambiente necessárias. Veja `docs/DEPLOY_ORACLE.md` para detalhes.

## 🐳 Passo 8: Testar Docker

```bash
# Fazer logout e login novamente para aplicar grupo docker
exit

# Reconectar
ssh -i ~/.ssh/oracle_key opc@<IP_PUBLICO>

# Testar Docker (sem sudo)
docker ps

# Se funcionar, está tudo certo!
```

## ✅ Passo 9: Deploy Inicial

```bash
cd ~/RBF-formuladobolso/back

# Build e iniciar containers
docker-compose up -d --build

# Aguardar serviços iniciarem
sleep 15

# Executar migrações
docker-compose exec -T api alembic upgrade head

# Verificar status
docker-compose ps

# Ver logs
docker-compose logs -f api
```

## 🔍 Verificar se Está Funcionando

```bash
# Verificar saúde da API
curl http://localhost:8000/health

# Verificar de fora (use o IP público)
curl http://<IP_PUBLICO>:8000/health
```

## 🔐 Configurar Firewall Local (Opcional)

Oracle Linux 9 usa `firewalld`:

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

## 📝 Comandos Úteis

```bash
# Ver IP público da instância
curl ifconfig.me

# Ver informações do sistema
uname -a
cat /etc/oracle-release

# Ver espaço em disco
df -h

# Ver memória
free -h

# Ver processos Docker
docker ps
docker stats

# Reiniciar instância (via console)
# Oracle Cloud Console > Instances > Instance Actions > Reboot
```

## 🚨 Troubleshooting

### Problema: Não consigo conectar via SSH

**Soluções:**
1. Verifique se o IP público está configurado
2. Verifique se a Security List permite porta 22
3. Verifique se a chave SSH está correta
4. Teste de outro local/IP

### Problema: Docker requer sudo

**Solução:**
```bash
sudo usermod -aG docker opc
# Fazer logout e login novamente
exit
```

### Problema: Porta 8000 não acessível externamente

**Soluções:**
1. Verifique Security List (porta 8000 permitida)
2. Verifique firewalld (se estiver usando)
3. Verifique se o container está rodando:
   ```bash
   docker-compose ps
   ```

## 📚 Próximos Passos

1. Configure o GitHub Actions (veja `docs/GITHUB_ACTIONS_SETUP.md`)
2. Configure domínio e HTTPS (opcional)
3. Configure backups automáticos

---

**Instância configurada e pronta!** 🎉

