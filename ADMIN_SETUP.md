# 🛡️ Guia Rápido - Área do Administrador

## 📋 Passo 1: Tornar um Usuário Administrador

### Opção 1: Via Script Python
```bash
# Listar usuários
python scripts/list-users.py

# Tornar usuário admin
python scripts/make-admin.py seu-email@exemplo.com
```

### Opção 2: Via Script PowerShell
```powershell
# Listar usuários
python scripts/list-users.py

# Tornar usuário admin
.\scripts\make-admin.ps1 seu-email@exemplo.com
```

### Opção 3: Via Banco de Dados (SQL)
```sql
-- Listar usuários
SELECT email, username, role, is_active FROM users;

-- Tornar usuário admin
UPDATE users 
SET role = 'admin' 
WHERE email = 'seu-email@exemplo.com';
```

### Opção 4: Via API (após ter um admin)
```bash
# Fazer login como admin primeiro
# Depois usar o endpoint:
POST /api/v1/admin/users/{user_id}/make-admin
```

---

## 🚀 Passo 2: Acessar a Área Admin

1. **Faça login** com uma conta de administrador
2. **Acesse** `http://3.238.162.190/admin`
3. **Ou clique** no menu "🛡️ Admin" no sidebar (só aparece para admins)

---

## 📊 Funcionalidades Disponíveis

### Dashboard
- Estatísticas gerais do sistema
- Novos usuários
- Volume financeiro
- Alertas de segurança

### Gerenciamento de Usuários
- Listar todos os usuários
- Buscar e filtrar
- Ativar/Desativar usuários
- Tornar/Remover admin
- Ver detalhes completos

### Segurança
- Logs de auditoria
- Alertas de segurança
- (Famílias e Relatórios em desenvolvimento)

---

## ⚠️ Importante

- Apenas usuários com `role = 'admin'` podem acessar `/admin`
- O menu Admin no sidebar só aparece para admins
- Todas as ações administrativas são logadas
- Não é possível remover seu próprio acesso de admin

---

## 🔧 Troubleshooting

### "Acesso negado" ao acessar /admin
- Verifique se o usuário tem `role = 'admin'` no banco
- Use o script `make-admin.py` para tornar admin

### Menu Admin não aparece
- Verifique se o usuário logado é admin
- Recarregue a página
- Verifique o console do navegador

### Erro ao executar scripts
- Certifique-se de estar na raiz do projeto
- Verifique se o `.env` está configurado corretamente
- Verifique se o banco de dados está acessível

