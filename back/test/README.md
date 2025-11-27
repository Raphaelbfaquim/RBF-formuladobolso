# Testes da API FormuladoBolso

## Estrutura de Testes

Os testes estão organizados por módulo da API:

- `test_auth.py` - Testes de autenticação (register, login)
- `test_users.py` - Testes de usuários
- `test_accounts.py` - Testes de contas
- `test_transactions.py` - Testes de transações

## Executar Testes

```bash
# Todos os testes
cd back && source ../venv/bin/activate
pytest test/ -v

# Teste específico
pytest test/test_auth.py::TestRegister::test_register_success -v

# Com cobertura
pytest test/ --cov=src --cov-report=html
```

## Dados de Teste

Os testes usam dados reais:
- Email: `usuario@teste.com.br`
- Username: `teste`
- Password: `senha123456`

## Nota sobre JSONB

O modelo `Receipt` usa JSONB (específico do PostgreSQL). Para testes com SQLite, é necessário:
1. Substituir JSONB por JSON nos modelos, OU
2. Usar PostgreSQL também nos testes

