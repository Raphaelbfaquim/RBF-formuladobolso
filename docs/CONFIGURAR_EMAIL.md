# 📧 Configuração de Email - FormuladoBolso

## Problema: Email não está sendo enviado

Se você solicitou a recuperação de senha ou convidou um membro mas não recebeu o email, é porque as credenciais SMTP não estão configuradas corretamente.

## ✅ Solução Rápida (Desenvolvimento)

Quando o email não pode ser enviado, o sistema mostra o link no console do backend e também na interface:

### Para Recuperação de Senha:
Procure no console do backend por:
```
🔗 LINK DE RESET:
   http://localhost:3000/reset-password?token=...
```

### Para Convites de Membros:
- O link aparece no console do backend
- O link também é exibido na interface web quando o email falha
- O link é automaticamente copiado para a área de transferência
- Um alerta mostra o link completo para você compartilhar manualmente

Copie o link e compartilhe com o usuário.

## 🔧 Configuração Permanente (Produção)

### Para Gmail

1. **Ative a verificação em duas etapas** na sua conta Google:
   - Acesse: https://myaccount.google.com/security
   - Ative "Verificação em duas etapas"

2. **Gere uma Senha de App**:
   - Acesse: https://myaccount.google.com/apppasswords
   - Selecione "App" → "Email"
   - Selecione "Dispositivo" → "Outro (nome personalizado)"
   - Digite "FormuladoBolso"
   - Clique em "Gerar"
   - **Copie a senha gerada** (16 caracteres, sem espaços)

3. **Configure no arquivo `.env`** do backend:

```bash
cd back
nano .env
```

Adicione ou edite:

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=seu-email@gmail.com
SMTP_PASSWORD=xxxx xxxx xxxx xxxx
```

**Importante**: Use a **Senha de App** gerada, não sua senha normal do Gmail!

4. **Reinicie o backend**:

```bash
# Parar o servidor atual
pkill -f "uvicorn.*main:app"

# Iniciar novamente
cd back
source ../venv/bin/activate
uvicorn src.presentation.api.main:app --host 0.0.0.0 --port 8000 --reload
```

### Para outros provedores

#### Outlook/Hotmail
```env
SMTP_HOST=smtp-mail.outlook.com
SMTP_PORT=587
SMTP_USER=seu-email@outlook.com
SMTP_PASSWORD=sua-senha
```

#### Yahoo
```env
SMTP_HOST=smtp.mail.yahoo.com
SMTP_PORT=587
SMTP_USER=seu-email@yahoo.com
SMTP_PASSWORD=sua-senha-app
```

#### SendGrid (Recomendado para produção)
```env
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=sua-api-key-do-sendgrid
```

## 🧪 Testar o envio de email

Após configurar, teste novamente a recuperação de senha. O email deve chegar na caixa de entrada (ou spam).

## 📝 Notas

- Em desenvolvimento, se o email não for enviado, o link aparece no console do backend
- Em produção, configure sempre o SMTP corretamente
- Para Gmail, sempre use "Senha de App", nunca a senha normal
- Verifique a pasta de spam se o email não aparecer na caixa de entrada

