# 📚 O que é Alembic e Migrações?

## 🤔 O que é Alembic?

**Alembic** é uma ferramenta de migração de banco de dados para SQLAlchemy. É como um "controle de versão" para seu banco de dados!

## 🎯 Por que é importante?

### Sem Alembic (Ruim):
- Você cria tabelas manualmente no banco
- Se mudar algo, precisa alterar manualmente
- Em produção, fica difícil sincronizar
- Não tem histórico de mudanças

### Com Alembic (Bom):
- ✅ Cria todas as tabelas automaticamente
- ✅ Versiona mudanças no banco
- ✅ Pode fazer rollback se necessário
- ✅ Sincroniza desenvolvimento e produção
- ✅ Histórico completo de mudanças

## 📝 Como Funciona?

### 1. Criar Migração
```bash
alembic revision --autogenerate -m "descrição"
```
Isso cria um arquivo Python com as mudanças necessárias.

### 2. Aplicar Migração
```bash
alembic upgrade head
```
Isso aplica todas as migrações pendentes no banco.

### 3. Reverter Migração
```bash
alembic downgrade -1
```
Isso reverte a última migração.

## 🔍 O que foi criado?

Criei o arquivo `alembic/versions/001_initial_migration.py` que contém:

- ✅ Criação de TODAS as 25+ tabelas
- ✅ Todos os relacionamentos (foreign keys)
- ✅ Todos os índices
- ✅ Todos os enums (tipos especiais)
- ✅ Todas as constraints

## 🚀 Como Usar?

### 1. Iniciar Banco de Dados
```bash
docker-compose up -d
```

### 2. Aplicar Migração
```bash
# Se tiver ambiente virtual ativado
alembic upgrade head

# Ou com python
python3 -m alembic upgrade head
```

### 3. Verificar
```bash
# Conectar no PostgreSQL e verificar tabelas
docker-compose exec postgres psql -U formulado_user -d formulado_db -c "\dt"
```

## 📊 O que será criado no banco?

A migração criará **25+ tabelas**:

1. `users` - Usuários
2. `families` - Famílias
3. `family_members` - Membros da família
4. `accounts` - Contas financeiras
5. `categories` - Categorias
6. `transactions` - Transações
7. `receipts` - Notas fiscais
8. `plannings` - Planejamentos
9. `monthly_plannings` - Planejamentos mensais
10. `weekly_plannings` - Planejamentos semanais
11. `daily_plannings` - Planejamentos diários
12. `annual_plannings` - Planejamentos anuais
13. `quarterly_goals` - Metas trimestrais
14. `goals` - Metas e sonhos
15. `goal_contributions` - Contribuições para metas
16. `badges` - Badges disponíveis
17. `user_badges` - Badges dos usuários
18. `user_levels` - Níveis dos usuários
19. `challenges` - Desafios
20. `user_challenges` - Desafios dos usuários
21. `bills` - Contas a pagar/receber
22. `investment_accounts` - Contas de investimento
23. `investment_transactions` - Transações de investimento
24. `bank_connections` - Conexões Open Banking
25. `educational_content` - Conteúdo educativo
26. `user_progress` - Progresso educacional
27. `quizzes` - Quizzes
28. `quiz_attempts` - Tentativas de quiz
29. `family_chat_messages` - Mensagens do chat familiar
30. `family_approvals` - Aprovações familiares
31. `two_factor_auth` - Autenticação de dois fatores
32. `audit_logs` - Logs de auditoria
33. `security_alerts` - Alertas de segurança

## ⚠️ Importante

- **Nunca edite migrações já aplicadas** em produção
- **Sempre teste** migrações em desenvolvimento primeiro
- **Faça backup** antes de aplicar em produção
- **Use `--autogenerate`** com cuidado (pode não detectar tudo)

## 🎯 Próximos Passos

1. Aplicar a migração: `alembic upgrade head`
2. Verificar se todas as tabelas foram criadas
3. Testar a API
4. Começar a usar! 🚀

---

**Alembic = Controle de Versão para Banco de Dados! 📦**

