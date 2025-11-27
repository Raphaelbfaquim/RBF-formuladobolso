# Deploy Manual da API na AWS

## Passo a Passo

### 1. Conectar na instância AWS

```bash
ssh -i ~/.ssh/LightsailDefaultKey-us-east-1.pem ubuntu@3.238.162.190
```

### 2. Verificar se o repositório existe

```bash
cd ~
ls -la RBF-formuladobolso
```

Se não existir, clone:
```bash
git clone https://github.com/Raphaelbfaquim/RBF-formuladobolso.git
cd RBF-formuladobolso
```

### 3. Atualizar o código

```bash
cd ~/RBF-formuladobolso
git fetch origin
git reset --hard origin/main
git clean -fd
```

### 4. Fazer login no Docker Hub

```bash
docker login
# Username: faquim
# Password: [sua senha do Docker Hub]
```

### 5. Fazer pull da imagem da API

```bash
docker pull faquim/formulado-api:latest
```

### 6. Parar containers antigos

```bash
cd ~/RBF-formuladobolso
docker-compose -f docker-compose.prod.yml down
docker stop formulado_api formulado_postgres formulado_redis 2>/dev/null || true
docker rm formulado_api formulado_postgres formulado_redis 2>/dev/null || true
```

### 7. Configurar variáveis de ambiente

```bash
export DOCKER_USERNAME=faquim
export IMAGE_TAG=latest
export SECRET_KEY=$(openssl rand -hex 32)
export CORS_ORIGINS="http://3.238.162.190,http://localhost:3000"
```

### 8. Iniciar os serviços

```bash
cd ~/RBF-formuladobolso
docker-compose -f docker-compose.prod.yml up -d postgres redis api
```

### 9. Aguardar PostgreSQL iniciar

```bash
# Verificar se PostgreSQL está pronto
docker-compose -f docker-compose.prod.yml exec -T postgres pg_isready -U formulado_user

# Se não estiver pronto, aguarde alguns segundos e tente novamente
```

### 10. Executar migrações

```bash
docker-compose -f docker-compose.prod.yml exec -T api alembic upgrade head
```

### 11. Verificar status

```bash
docker-compose -f docker-compose.prod.yml ps
docker-compose -f docker-compose.prod.yml logs api
```

### 12. Testar a API

```bash
curl http://localhost:8000/health
curl http://localhost:8000/docs
```

## Verificação Externa

De sua máquina local, teste:

```powershell
# Health check
Invoke-WebRequest -Uri "http://3.238.162.190:8000/health"

# Documentação
Start-Process "http://3.238.162.190:8000/docs"
```

## Troubleshooting

### Se a API não estiver respondendo:

1. Verificar logs:
```bash
docker-compose -f docker-compose.prod.yml logs api
```

2. Verificar se o container está rodando:
```bash
docker ps | grep formulado_api
```

3. Verificar portas:
```bash
sudo netstat -tlnp | grep 8000
```

4. Verificar firewall AWS:
- Acesse o console AWS Lightsail
- Vá em Networking > Firewall
- Certifique-se de que a porta 8000 está aberta

### Se o PostgreSQL não iniciar:

```bash
docker-compose -f docker-compose.prod.yml logs postgres
docker-compose -f docker-compose.prod.yml restart postgres
```

### Se as migrações falharem:

```bash
# Tentar inicializar o banco manualmente
docker-compose -f docker-compose.prod.yml exec -T api python scripts/init_db.py
docker-compose -f docker-compose.prod.yml exec -T api alembic upgrade head
```

