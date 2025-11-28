# ✅ Correções de Deploy - Resumo

## 🔧 Problema Identificado

As atualizações no código, configurações e parte admin não estavam refletindo no servidor devido a:

1. **Cache do Docker** - Imagens antigas sendo reutilizadas
2. **Containers não recriados** - Containers antigos continuavam rodando
3. **Código desatualizado** - Build local não garantia código atualizado no servidor
4. **Migrações não executadas** - Mudanças no banco não eram aplicadas

---

## ✅ Soluções Implementadas

### 1. Script de Deploy Melhorado (`deploy-aws.ps1`)

**Melhorias:**
- ✅ Build **sem cache** (`--no-cache`) para garantir código atualizado
- ✅ Limpa imagens antigas antes de carregar novas
- ✅ Força recriação dos containers (`--force-recreate`)
- ✅ Executa migrações automaticamente após deploy da API
- ✅ Verifica status dos containers após deploy

**Como usar:**
```powershell
.\deploy-aws.ps1          # Deploy completo
.\deploy-aws.ps1 api      # Apenas API
.\deploy-aws.ps1 front    # Apenas Frontend
```

---

### 2. Novo Script: Build no Servidor (`deploy-build-server.ps1`)

**Vantagens:**
- ✅ Faz build **diretamente no servidor**
- ✅ Usa código atualizado do repositório (git pull)
- ✅ Não depende de imagens locais
- ✅ Mais confiável para garantir atualizações

**Como usar:**
```powershell
.\scripts\deploy-build-server.ps1          # Deploy completo
.\scripts\deploy-build-server.ps1 api     # Apenas API
.\scripts\deploy-build-server.ps1 front   # Apenas Frontend
```

**Recomendado quando:**
- Atualizações não aparecem mesmo após deploy normal
- Quer garantir que o código mais recente do repositório seja usado
- Prefere build no servidor em vez de enviar imagens

---

## 📋 O Que Foi Corrigido

### Scripts Atualizados:
1. ✅ `scripts/deploy-direto-aws.ps1` - Melhorado com build sem cache e força recriação
2. ✅ `scripts/deploy-build-server.ps1` - NOVO script para build no servidor
3. ✅ `deploy-aws.ps1` - Atualizado para usar script melhorado

### Documentação Criada:
1. ✅ `docs/TROUBLESHOOTING_DEPLOY.md` - Guia completo de troubleshooting
2. ✅ `README-DEPLOY.md` - Atualizado com novas opções

### Correções Técnicas:
1. ✅ Consistência do nome Docker (`efaquim` em todos os lugares)
2. ✅ Limpeza de imagens antigas antes de deploy
3. ✅ Execução automática de migrações
4. ✅ Verificação de status após deploy

---

## 🚀 Próximos Passos

### Para aplicar as correções AGORA:

**Opção 1 - Deploy Melhorado (Recomendado):**
```powershell
.\deploy-aws.ps1 all
```

**Opção 2 - Build no Servidor (Mais Confiável):**
```powershell
.\scripts\deploy-build-server.ps1 all
```

### Verificar se funcionou:

1. **Ver logs:**
```powershell
ssh -i ~/.ssh/LightsailDefaultKey-us-east-1.pem ubuntu@3.238.162.190
cd ~/RBF-formuladobolso
docker-compose -f docker-compose.prod.yml logs -f
```

2. **Verificar status:**
```bash
docker-compose -f docker-compose.prod.yml ps
```

3. **Testar no navegador:**
- Frontend: http://3.238.162.190
- API: http://3.238.162.190/api
- Admin: http://3.238.162.190/admin (se for admin)

---

## 🛡️ Para Problemas com Admin

Se a área admin ainda não aparecer:

1. **Verificar se o usuário é admin:**
```bash
# No servidor
docker-compose -f docker-compose.prod.yml exec postgres psql -U formulado_user -d formulado_db
SELECT email, username, role FROM users;
```

2. **Tornar usuário admin:**
```bash
# No servidor
cd ~/RBF-formuladobolso
python scripts/make-admin.py seu-email@exemplo.com
```

3. **Limpar cache do navegador:**
- Pressione `Ctrl+Shift+R` (hard refresh)
- Ou limpe o cache completamente

---

## 📚 Documentação

- 📖 [README-DEPLOY.md](README-DEPLOY.md) - Guia de deploy atualizado
- 📖 [docs/TROUBLESHOOTING_DEPLOY.md](docs/TROUBLESHOOTING_DEPLOY.md) - Troubleshooting completo
- 📖 [ADMIN_SETUP.md](ADMIN_SETUP.md) - Configuração de admin

---

## 💡 Dicas

1. **Sempre use `--no-cache` em builds de produção** (já incluído nos scripts)
2. **Use `--force-recreate` ao iniciar containers** (já incluído nos scripts)
3. **Verifique logs após deploy** para identificar problemas
4. **Faça deploy em horários de baixo tráfego** se possível
5. **Mantenha backups** antes de deploys grandes

---

## ✅ Checklist de Deploy

Antes de fazer deploy:
- [ ] Código commitado e pushado para o repositório
- [ ] Migrações do banco criadas (se houver mudanças no schema)
- [ ] Variáveis de ambiente atualizadas (se necessário)
- [ ] Testes locais passando

Após o deploy:
- [ ] Verificar logs: `docker-compose -f docker-compose.prod.yml logs`
- [ ] Testar endpoints da API
- [ ] Testar frontend no navegador
- [ ] Verificar se migrações foram executadas
- [ ] Limpar cache do navegador se necessário

---

**Pronto! Agora seus deploys devem funcionar corretamente! 🎉**

