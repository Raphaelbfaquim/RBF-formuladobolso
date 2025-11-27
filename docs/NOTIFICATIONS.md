# Sistema de Notificações

O FormuladoBolso possui um sistema completo de notificações que alerta os usuários sobre o status de seus planejamentos financeiros.

## 📧 Funcionalidades

### 1. Notificações por Email
- Envio automático de emails quando o usuário está fora do planejamento
- Emails de incentivo quando está no planejamento
- Templates HTML profissionais e responsivos

### 2. Notificações por WhatsApp
- Mensagens automáticas via WhatsApp
- Suporte a múltiplas APIs (Evolution API, Meta, Twilio)
- Mensagens formatadas e informativas

### 3. Verificação Automática
- Tarefa agendada que verifica planejamentos periodicamente
- Verificação a cada hora
- Verificações diárias às 8h e 20h

## 🎯 Critérios de Notificação

### Quando está FORA do Planejamento
- **Condição**: Gasto ultrapassou 110% do planejado (10% de tolerância)
- **Ação**: Envia alerta por email e WhatsApp
- **Conteúdo**: 
  - Valor da meta vs. gasto real
  - Porcentagem ultrapassada
  - Recomendações para ajustar

### Quando está NO Planejamento
- **Condição**: Gasto está dentro ou abaixo do planejado
- **Ação**: Envia mensagem de incentivo
- **Conteúdo**:
  - Parabéns pelo controle financeiro
  - Estatísticas do progresso
  - Dicas para continuar no caminho certo
- **Frequência**: Notifica em marcos importantes (50%, 75%, 90%, 100%)

## ⚙️ Configuração

### 1. Configurar Email (SMTP)

Adicione no arquivo `.env`:

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=seu-email@gmail.com
SMTP_PASSWORD=sua-senha-app
```

**Para Gmail:**
1. Ative a verificação em duas etapas
2. Gere uma "Senha de app" em: https://myaccount.google.com/apppasswords
3. Use a senha de app no `SMTP_PASSWORD`

### 2. Configurar WhatsApp

Escolha uma das opções abaixo:

#### Opção 1: Evolution API (Recomendado)
```env
WHATSAPP_API_URL=https://api.evolution.com
WHATSAPP_API_TOKEN=seu-token
WHATSAPP_PHONE_NUMBER_ID=seu-instance-id
```

#### Opção 2: WhatsApp Business API (Meta)
```env
WHATSAPP_API_URL=https://graph.facebook.com/v18.0
WHATSAPP_API_TOKEN=seu-access-token
WHATSAPP_PHONE_NUMBER_ID=seu-phone-number-id
```

#### Opção 3: Twilio
```env
WHATSAPP_API_URL=https://api.twilio.com
WHATSAPP_API_TOKEN=seu-account-sid
TWILIO_AUTH_TOKEN=seu-auth-token
WHATSAPP_PHONE_NUMBER_ID=seu-whatsapp-number
```

### 3. Adicionar Telefone do Usuário

O sistema precisa do número de telefone do usuário para enviar WhatsApp. Adicione o campo `phone_number` ao cadastrar/atualizar usuário:

```json
{
  "phone_number": "5511999999999"
}
```

## 📱 Uso da API

### Verificar Planejamento Manualmente

```bash
POST /api/v1/notifications/planning/{planning_id}/check
Authorization: Bearer <token>

Query Parameters:
- threshold: float (padrão: 10.0) - Limite de tolerância em %
- force: bool (padrão: false) - Forçar notificação mesmo se não atender critérios
```

**Exemplo:**
```bash
curl -X POST "http://localhost:8000/api/v1/notifications/planning/{planning_id}/check?threshold=10.0" \
  -H "Authorization: Bearer <token>"
```

**Resposta:**
```json
{
  "notified": true,
  "notification_result": {
    "email_sent": true,
    "whatsapp_sent": true,
    "is_over_budget": false,
    "is_on_track": true
  },
  "percentage": 85.5,
  "is_over_budget": false,
  "is_on_track": true
}
```

## 🔄 Verificação Automática

A verificação automática é iniciada quando a API é iniciada. Ela:

1. **Verifica a cada hora** (minuto 0)
2. **Verifica diariamente** às 8h e 20h
3. **Processa todos os planejamentos ativos**
4. **Envia notificações** quando necessário

### Desabilitar Verificação Automática

Para desabilitar, comente a linha no `src/presentation/api/main.py`:

```python
# planning_checker.start()
```

## 📝 Templates de Mensagens

### Email - Fora do Planejamento
- Design profissional com cores de alerta
- Estatísticas visuais (meta, gasto, excesso)
- Recomendações práticas
- Responsivo para mobile

### Email - No Planejamento
- Design celebratório
- Estatísticas de sucesso
- Dicas motivacionais
- Responsivo para mobile

### WhatsApp - Fora do Planejamento
- Mensagem formatada com emojis
- Informações resumidas
- Recomendações rápidas

### WhatsApp - No Planejamento
- Mensagem de parabéns
- Estatísticas do progresso
- Dicas para continuar

## 🛡️ Prevenção de Spam

O sistema possui proteções contra spam:

1. **Notificações de alerta**: Só envia se ultrapassou 5% desde a última notificação
2. **Notificações de incentivo**: Só envia em marcos específicos (50%, 75%, 90%, 100%)
3. **Verificação periódica**: Limita frequência de verificações

## 🧪 Testando

### Teste Manual

1. Crie um planejamento
2. Adicione transações que ultrapassem o limite
3. Chame o endpoint de verificação manual
4. Verifique email e WhatsApp

### Teste Automático

A verificação automática roda em background. Para ver logs:

```bash
# Os logs aparecerão no console da aplicação
[2024-01-15 10:00:00] Verificando 5 planejamentos...
[2024-01-15 10:00:01] Notificação enviada para planejamento abc-123 (Porcentagem: 115.50%)
```

## 🔧 Troubleshooting

### Email não está sendo enviado
1. Verifique credenciais SMTP no `.env`
2. Para Gmail, use senha de app
3. Verifique firewall/antivírus
4. Veja logs de erro no console

### WhatsApp não está funcionando
1. Verifique configuração da API escolhida
2. Confirme que o número está no formato correto (5511999999999)
3. Verifique token e permissões da API
4. Veja logs de erro no console

### Notificações não estão sendo enviadas
1. Verifique se o planejamento está ativo
2. Confirme que o usuário tem email e telefone cadastrados
3. Verifique se os critérios de notificação estão sendo atendidos
4. Use `force=true` para testar

## 📊 Monitoramento

Para monitorar notificações:

1. **Logs da aplicação**: Veja mensagens no console
2. **Endpoint de verificação**: Retorna status de cada envio
3. **Banco de dados**: Pode adicionar tabela de histórico (futuro)

## 🚀 Melhorias Futuras

- [ ] Histórico de notificações enviadas
- [ ] Preferências de notificação por usuário
- [ ] Notificações push (mobile)
- [ ] Dashboard de notificações
- [ ] Templates customizáveis
- [ ] Agendamento personalizado por usuário

---

**Sistema de Notificações - FormuladoBolso**

