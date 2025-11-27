# ⚡ Quick Start - Oracle Cloud + GitHub Actions

Guia rápido para começar em 5 minutos usando GitHub Actions (nativo do GitHub).

## 🎯 Passos Rápidos

### 1. Configurar IP Público na Oracle Cloud

1. No Oracle Cloud Console, vá na sua instância
2. Na seção **Attached VNICs**, clique no link da VNIC
3. Clique em **IPv4 Addresses** > **Edit**
4. Marque **Assign a public IPv4 address**
5. Selecione **Ephemeral Public IP** ou **Reserved Public IP**
6. **Anote o IP público** atribuído

### 2. Configurar Security List (Firewall)

1. Vá em **Networking** > **Virtual Cloud Networks** > `vcn-20251126-0905`
2. **Security Lists** > **Default Security List** > **Add Ingress Rules**
3. Adicione regras para:
   - Porta **22** (SSH)
   - Porta **8000** (Backend API)

### 3. Configurar Instância Oracle Cloud (5 min)

```bash
# Conectar na instância (usuário é 'opc' no Oracle Linux)
ssh -i ~/.ssh/oracle_key.pem opc@<IP_PUBLICO>

# Atualizar sistema
sudo dnf update -y

# Instalar Docker (Oracle Linux 9)
sudo dnf install -y docker git
sudo systemctl enable docker
sudo systemctl start docker
sudo usermod -aG docker opc

# Instalar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Clonar repositório
cd ~
git clone https://github.com/Raphaelbfaquim/RBF-formuladobolso.git
cd RBF-formuladobolso/back

# Criar .env
cp env.example .env
nano .env  # Editar configurações

# Logout e login para aplicar grupo docker
exit
```

### 4. Configurar GitHub Actions (3 min)

1. **Adicionar Secrets no GitHub**:
   - `ORACLE_HOST`: IP público da instância
   - `ORACLE_USER`: `opc`
   - `ORACLE_SSH_PRIVATE_KEY`: Sua chave privada SSH completa

2. **O workflow já está configurado!** (`.github/workflows/deploy-oracle.yml`)

### 5. Testar

```bash
# Fazer um commit de teste
git commit --allow-empty -m "Test GitHub Actions deploy"
git push origin main
```

Verifique em **Actions** no GitHub se o deploy foi executado!

## 📚 Documentação Completa

- **Setup Inicial**: `docs/ORACLE_CLOUD_SETUP.md`
- **GitHub Actions**: `docs/GITHUB_ACTIONS_SETUP.md`
- **Deploy Oracle Cloud**: `docs/DEPLOY_ORACLE.md`

## 🔧 Comandos Úteis

```bash
# Ver logs
docker-compose logs -f

# Reiniciar
docker-compose restart

# Status
docker-compose ps

# Parar
docker-compose down
```

---

**Pronto!** Agora cada push na `main` faz deploy automático! 🚀

