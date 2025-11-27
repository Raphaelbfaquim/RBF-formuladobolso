# 🔄 Automação de Deploy com Make.com

Guia passo a passo para configurar automação de deploy na Oracle Cloud usando Make.com.

## 📋 Pré-requisitos

1. **Conta Make.com** (gratuita)
   - Acesse: https://www.make.com
   - Crie uma conta gratuita (até 1000 operações/mês)

2. **Instância Oracle Cloud configurada**
   - SSH funcionando
   - Docker e Docker Compose instalados
   - Repositório clonado na instância

3. **Chave SSH privada**
   - Você precisa da chave privada (.pem) para acessar a instância

## 🎯 Configuração do Cenário Make.com

### Passo 1: Criar Novo Cenário

1. Acesse https://www.make.com
2. Clique em **"Create a new scenario"**
3. Dê um nome: `Deploy FormuladoBolso - Oracle Cloud`

### Passo 2: Configurar Webhook (Trigger)

1. Clique em **"+"** para adicionar módulo
2. Procure por **"Webhooks"**
3. Selecione **"Custom webhook"**
4. Clique em **"Add"**
5. Configure:
   - **Webhook name**: `GitHub Push Webhook`
   - **Data structure**: Deixe vazio (será criado automaticamente)
6. Clique em **"Save"**
7. **Copie a URL do webhook** (você precisará dela no GitHub)

### Passo 3: Adicionar Filtro (Opcional)

Para deploy apenas quando houver push na branch `main`:

1. Clique em **"+"** após o webhook
2. Procure por **"Router"**
3. Selecione **"Router"**
4. Configure:
   - **Label**: `Filter main branch`
   - **Condition**: `ref` contém `refs/heads/main`
5. Clique em **"Save"**

### Passo 4: Configurar SSH

1. Clique em **"+"** após o filtro (ou webhook se não usou filtro)
2. Procure por **"SSH"**
3. Selecione **"Execute a command"**
4. Configure:

#### Aba "Connection"
- **Host**: `<IP_PUBLICO_DA_INSTANCIA_ORACLE>`
  - Exemplo: `129.213.xxx.xxx`
- **Port**: `22`
- **Username**: `ubuntu` (ou `opc` se usar Oracle Linux)
- **Authentication**: `Private key`
- **Private key**: Cole sua chave privada SSH completa
  ```bash
  -----BEGIN RSA PRIVATE KEY-----
  ...
  -----END RSA PRIVATE KEY-----
  ```

#### Aba "Command"
- **Command**: Cole o seguinte script:

```bash
cd ~/RBF-formuladobolso && \
git pull origin main && \
cd back && \
docker-compose down && \
docker-compose up -d --build && \
sleep 10 && \
docker-compose exec -T postgres pg_isready -U formulado_user || sleep 5 && \
docker-compose exec -T api alembic upgrade head && \
docker-compose ps
```

**Explicação do comando:**
- `cd ~/RBF-formuladobolso` - Navega para o diretório do projeto
- `git pull origin main` - Atualiza o código da branch main
- `cd back` - Entra na pasta do backend
- `docker-compose down` - Para os containers atuais
- `docker-compose up -d --build` - Reconstrói e inicia os containers
- `sleep 10` - Aguarda serviços iniciarem
- `docker-compose exec -T postgres pg_isready` - Verifica se PostgreSQL está pronto
- `docker-compose exec -T api alembic upgrade head` - Executa migrações
- `docker-compose ps` - Mostra status dos containers

5. Clique em **"Save"**

### Passo 5: Adicionar Notificação (Opcional)

Para receber email quando o deploy for concluído:

1. Clique em **"+"** após o módulo SSH
2. Procure por **"Email"**
3. Selecione **"Send an email"**
4. Configure:
   - **To**: Seu email
   - **Subject**: `Deploy FormuladoBolso - {{execution.status}}`
   - **Content type**: `HTML`
   - **Message**: 
   ```html
   <h2>Deploy do FormuladoBolso</h2>
   <p><strong>Status:</strong> {{execution.status}}</p>
   <p><strong>Data:</strong> {{execution.finishedAt}}</p>
   <p><strong>Branch:</strong> {{webhook.ref}}</p>
   <p><strong>Commit:</strong> {{webhook.head_commit.message}}</p>
   ```
5. Clique em **"Save"**

### Passo 6: Testar o Cenário

1. Clique em **"Run once"** no canto inferior direito
2. Isso executará o cenário manualmente
3. Verifique os logs de cada módulo
4. Se houver erros, ajuste as configurações

### Passo 7: Ativar o Cenário

1. Clique no botão **"Inactive"** no topo
2. Mude para **"Active"**
3. O cenário agora está ativo e responderá aos webhooks

## 🔗 Configurar Webhook no GitHub

### Passo 1: Acessar Configurações do Repositório

1. Acesse: https://github.com/Raphaelbfaquim/RBF-formuladobolso
2. Vá em **Settings** (Configurações)
3. Clique em **Webhooks** no menu lateral

### Passo 2: Adicionar Webhook

1. Clique em **"Add webhook"**
2. Configure:

#### Payload URL
- Cole a URL do webhook do Make.com (copiada no Passo 2)

#### Content type
- Selecione: `application/json`

#### Secret (Opcional)
- Deixe vazio ou crie um secret para segurança adicional

#### Which events would you like to trigger this webhook?
- Selecione: **Just the push event**
  - Isso fará deploy apenas quando houver push

#### Active
- ✅ Marque a opção

3. Clique em **"Add webhook"**

### Passo 3: Testar Webhook

1. Faça um pequeno commit e push:
   ```bash
   git commit --allow-empty -m "Test webhook"
   git push origin main
   ```

2. Volte ao Make.com
3. Verifique se o cenário foi executado
4. Veja os logs de cada módulo

## 🔧 Configurações Avançadas

### Deploy Apenas em Mudanças Específicas

Se quiser fazer deploy apenas quando houver mudanças no backend:

1. Adicione um filtro após o Router:
   - **Module**: Router
   - **Condition**: `commits[].modified` contém `back/`

### Deploy em Múltiplas Instâncias

Para fazer deploy em múltiplas instâncias Oracle Cloud:

1. Duplique o módulo SSH
2. Configure com IPs diferentes
3. Use um módulo **"Set multiple variables"** para definir IPs

### Rollback Automático em Caso de Erro

1. Adicione um módulo **"Router"** após o SSH
2. Configure rota de erro
3. Adicione outro módulo SSH com comando de rollback:
   ```bash
   cd ~/RBF-formuladobolso && \
   git reset --hard HEAD~1 && \
   cd back && \
   docker-compose down && \
   docker-compose up -d --build
   ```

## 📊 Monitoramento

### Ver Histórico de Execuções

1. No Make.com, vá em **"Scenarios"**
2. Clique no seu cenário
3. Veja a aba **"Executions"**
4. Clique em uma execução para ver detalhes

### Logs Detalhados

1. Clique em uma execução
2. Veja os logs de cada módulo
3. Verifique erros e warnings
4. Use para debugging

## 🚨 Troubleshooting

### Problema: Webhook não está sendo acionado

**Soluções:**
1. Verifique se o webhook está ativo no GitHub
2. Verifique se o cenário está ativo no Make.com
3. Teste o webhook manualmente no GitHub (botão "Redeliver")
4. Verifique os logs do webhook no GitHub

### Problema: Erro de conexão SSH

**Soluções:**
1. Verifique se o IP está correto
2. Verifique se a chave privada está completa (incluindo headers)
3. Verifique se o usuário está correto (`ubuntu` ou `opc`)
4. Teste conexão manual:
   ```bash
   ssh -i ~/.ssh/oracle_key.pem ubuntu@<IP>
   ```

### Problema: Comando SSH falha

**Soluções:**
1. Verifique se o caminho do projeto está correto
2. Verifique se Docker está instalado na instância
3. Verifique se o usuário tem permissões Docker
4. Teste o comando manualmente na instância

### Problema: Deploy muito lento

**Soluções:**
1. Use `docker-compose pull` antes de `up` para cache
2. Remova `--build` se não houver mudanças no Dockerfile
3. Use build cache do Docker

## 📝 Variáveis de Ambiente no Make.com

Para usar variáveis diferentes por ambiente:

1. No Make.com, vá em **"Variables"**
2. Crie variáveis:
   - `ORACLE_IP` - IP da instância
   - `ORACLE_USER` - Usuário SSH
   - `ORACLE_SSH_KEY` - Chave privada
3. Use nos módulos: `{{variables.ORACLE_IP}}`

## 🔐 Segurança

### Boas Práticas

1. **Não commite chaves SSH** no repositório
2. **Use secrets do Make.com** para armazenar chaves
3. **Limite IPs** que podem acessar a instância
4. **Use HTTPS** para webhooks (Make.com usa por padrão)
5. **Monitore execuções** regularmente

### Secret no GitHub Webhook

1. Gere um secret forte:
   ```bash
   openssl rand -hex 32
   ```
2. Configure no GitHub webhook
3. Use no Make.com para validar requests

## 📚 Recursos Adicionais

- **Make.com Docs**: https://www.make.com/en/help
- **GitHub Webhooks**: https://docs.github.com/en/developers/webhooks-and-events/webhooks
- **SSH Module**: https://www.make.com/en/help/tools/ssh

---

**Automação configurada!** 🎉

Agora cada push na branch `main` fará deploy automático na sua instância Oracle Cloud!

