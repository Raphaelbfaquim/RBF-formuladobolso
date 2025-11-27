# 📧 Como Configurar Email - FormuladoBolso

## ⚠️ Problema Atual

O Gmail está retornando o erro: **"Application-specific password required"**

Isso significa que você precisa usar uma **Senha de App** do Gmail, não a senha normal da conta.

## ✅ Solução Rápida (Agora)

**Use este link para redefinir sua senha agora:**
```
http://localhost:3000/reset-password?token=Xt889BD8sg2FMXrnzk_7_wNrCJCq8MH7tXo7lDPaozM
```

Este link é válido por **1 hora**.

## 🔧 Configuração Permanente (Para envio automático)

### Passo 1: Ativar Verificação em Duas Etapas

1. Acesse: https://myaccount.google.com/security
2. Procure por "Verificação em duas etapas"
3. Se não estiver ativada, ative agora
4. Siga as instruções para configurar

### Passo 2: Gerar Senha de App

1. Acesse: https://myaccount.google.com/apppasswords
2. Se não aparecer a opção, você precisa ativar a verificação em duas etapas primeiro
3. Selecione:
   - **App**: Email
   - **Dispositivo**: Outro (nome personalizado)
   - Digite: **FormuladoBolso**
4. Clique em **"Gerar"**
5. **Copie a senha gerada** (16 caracteres, formato: `xxxx xxxx xxxx xxxx`)

### Passo 3: Atualizar arquivo .env

```bash
cd back
nano .env
```

Edite a linha `SMTP_PASSWORD`:

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=efaquim@gmail.com
SMTP_PASSWORD=xxxx xxxx xxxx xxxx
```

**Importante**: 
- Use a senha de app gerada (os 16 caracteres)
- Você pode remover os espaços ou deixar com espaços, ambos funcionam
- NÃO use sua senha normal do Gmail

### Passo 4: Reiniciar Backend

```bash
# Parar o backend atual
pkill -f "uvicorn.*main:app.*8000"

# Iniciar novamente
cd back
source ../venv/bin/activate
uvicorn src.presentation.api.main:app --host 0.0.0.0 --port 8000 --reload
```

### Passo 5: Testar

1. Acesse: http://localhost:3000/forgot-password
2. Digite seu email: efaquim@gmail.com
3. Verifique sua caixa de entrada (ou spam)

## 📝 Notas Importantes

- **Senha de App** é diferente da senha normal
- A senha de app tem 16 caracteres
- Você pode gerar múltiplas senhas de app
- Se perder a senha de app, gere uma nova
- Em desenvolvimento, o link aparece no console do backend se o email falhar

## 🔍 Verificar se está funcionando

Após configurar, os logs do backend devem mostrar:
```
✅ Autenticação SMTP bem-sucedida
✅ Email de recuperação enviado com sucesso para efaquim@gmail.com
```

Se aparecer erros, verifique:
- Se a verificação em duas etapas está ativada
- Se a senha de app foi copiada corretamente
- Se não há espaços extras no .env

