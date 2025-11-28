# 🔧 Troubleshooting - Deploy e Atualizações

## Problema: Atualizações não refletem no servidor

Se você fez alterações no código, configurações ou parte admin, mas elas não aparecem no servidor, siga este guia.

---

## ✅ Soluções

### Opção 1: Deploy Melhorado (Recomendado)

O script `deploy-aws.ps1` foi melhorado para:
- ✅ Fazer build **sem cache** (garante código atualizado)
- ✅ Limpar imagens antigas antes de carregar novas
- ✅ Forçar recriação dos containers
- ✅ Executar migrações automaticamente
- ✅ Verificar status após deploy

**Como usar:**
```powershell
# Deploy completo (API + Frontend)
.\deploy-aws.ps1

# Deploy apenas da API
.\deploy-aws.ps1 api

# Deploy apenas do Frontend
.\deploy-aws.ps1 front
```

---

### Opção 2: Build Direto no Servidor (Mais Confiável)

Este método faz o build **diretamente no servidor**, garantindo que o código mais recente do repositório seja usado.

**Vantagens:**
- ✅ Usa código atualizado do repositório
- ✅ Não depende de imagens locais
- ✅ Mais confiável para garantir atualizações

**Como usar:**
```powershell
# Deploy completo (API + Frontend)
.\scripts\deploy-build-server.ps1

# Deploy apenas da API
.\scripts\deploy-build-server.ps1 api

# Deploy apenas do Frontend
.\scripts\deploy-build-server.ps1 front
```

---

## 🔍 Verificações Manuais

Se ainda não funcionar, verifique manualmente:

### 1. Verificar se o código está atualizado no servidor

```bash
ssh -i ~/.ssh/LightsailDefaultKey-us-east-1.pem ubuntu@3.238.162.190
cd ~/RBF-formuladobolso
git pull origin main
git log -1  # Ver último commit
```

### 2. Verificar containers em execução

```bash
cd ~/RBF-formuladobolso
docker-compose -f docker-compose.prod.yml ps
```

### 3. Ver logs dos containers

```bash
# Logs da API
docker-compose -f docker-compose.prod.yml logs api

# Logs do Frontend
docker-compose -f docker-compose.prod.yml logs frontend

# Logs de todos
docker-compose -f docker-compose.prod.yml logs -f
```

### 4. Forçar rebuild completo

```bash
cd ~/RBF-formuladobolso

# Parar tudo
docker-compose -f docker-compose.prod.yml down

# Limpar imagens antigas
docker rmi efaquim/formulado-api:latest efaquim/formulado-frontend:latest 2>/dev/null || true
docker system prune -f

# Atualizar código
git pull origin main

# Build sem cache
docker build --no-cache -t efaquim/formulado-api:latest -f back/docker/Dockerfile back/
docker build --no-cache -t efaquim/formulado-frontend:latest -f front/Dockerfile --build-arg NEXT_PUBLIC_API_URL=http://3.238.162.190 front/

# Iniciar
export DOCKER_USERNAME=faquim
export IMAGE_TAG=latest
docker-compose -f docker-compose.prod.yml up -d --force-recreate

# Executar migrações
docker-compose -f docker-compose.prod.yml exec -T api alembic upgrade head
```

---

## 🛡️ Problemas Específicos

### Admin não aparece

1. **Verificar se o usuário é admin no banco:**
```bash
# Conectar no banco
docker-compose -f docker-compose.prod.yml exec postgres psql -U formulado_user -d formulado_db

# Verificar usuários
SELECT email, username, role, is_active FROM users;

# Tornar admin (se necessário)
UPDATE users SET role = 'ADMIN' WHERE email = 'seu-email@exemplo.com';
```

2. **Verificar se o frontend tem as rotas admin:**
```bash
# Verificar se o arquivo existe
docker-compose -f docker-compose.prod.yml exec frontend ls -la /app/src/app/admin
```

3. **Limpar cache do navegador:**
- Pressione `Ctrl+Shift+R` (ou `Cmd+Shift+R` no Mac) para hard refresh
- Ou limpe o cache do navegador completamente

### Configurações não atualizam

1. **Verificar variáveis de ambiente:**
```bash
# Ver variáveis da API
docker-compose -f docker-compose.prod.yml exec api env | grep -E "(DATABASE|REDIS|SECRET)"

# Ver variáveis do Frontend
docker-compose -f docker-compose.prod.yml exec frontend env | grep NEXT_PUBLIC
```

2. **Verificar arquivo .env no servidor:**
```bash
cd ~/RBF-formuladobolso
cat back/.env  # Se existir
```

3. **Reiniciar containers após mudar .env:**
```bash
docker-compose -f docker-compose.prod.yml restart api frontend
```

### Código não atualiza

1. **Verificar se o commit foi feito:**
```bash
# No servidor
cd ~/RBF-formuladobolso
git log -5  # Ver últimos 5 commits
git status  # Ver se há mudanças não commitadas
```

2. **Forçar pull:**
```bash
git fetch origin
git reset --hard origin/main
```

3. **Verificar se o build incluiu as mudanças:**
```bash
# Ver quando a imagem foi criada
docker images | grep formulado

# Ver conteúdo do container
docker-compose -f docker-compose.prod.yml exec api ls -la /app/src/
```

---

## 🚀 Deploy Rápido (Um Comando)

Para fazer deploy completo com todas as garantias:

```powershell
# No Windows (PowerShell)
.\scripts\deploy-build-server.ps1 all
```

Isso vai:
1. ✅ Atualizar código no servidor
2. ✅ Limpar imagens antigas
3. ✅ Build sem cache
4. ✅ Recriar containers
5. ✅ Executar migrações
6. ✅ Verificar status

---

## 📝 Checklist de Deploy

Antes de fazer deploy, certifique-se:

- [ ] Código commitado e pushado para o repositório
- [ ] Migrações do banco criadas (se houver mudanças no schema)
- [ ] Variáveis de ambiente atualizadas (se necessário)
- [ ] Testes locais passando
- [ ] Chave SSH configurada corretamente

Após o deploy:

- [ ] Verificar logs: `docker-compose -f docker-compose.prod.yml logs`
- [ ] Testar endpoints da API
- [ ] Testar frontend no navegador
- [ ] Verificar se migrações foram executadas
- [ ] Limpar cache do navegador se necessário

---

## 💡 Dicas

1. **Sempre use `--no-cache` em builds de produção** para garantir código atualizado
2. **Use `--force-recreate`** ao iniciar containers para garantir nova instância
3. **Verifique logs após deploy** para identificar problemas rapidamente
4. **Faça deploy em horários de baixo tráfego** se possível
5. **Mantenha backups** antes de deploys grandes

---

## 🆘 Ainda com problemas?

Se nada funcionar:

1. Verifique os logs detalhados:
```bash
docker-compose -f docker-compose.prod.yml logs --tail=100
```

2. Verifique se os containers estão rodando:
```bash
docker-compose -f docker-compose.prod.yml ps
```

3. Reinicie tudo do zero:
```bash
docker-compose -f docker-compose.prod.yml down
docker system prune -a -f
# Depois execute o deploy novamente
```

4. Verifique recursos do servidor:
```bash
df -h  # Espaço em disco
free -h  # Memória
docker stats  # Uso de recursos dos containers
```

