# Estrutura do Banco de Dados

Este documento descreve a estrutura completa do banco de dados do FormuladoBolso.

## 📊 Diagrama de Entidades

```
┌─────────────┐
│    User     │
└──────┬──────┘
       │
       ├───┐
       │   │
       │   ├──────────────┐
       │   │              │
       ▼   ▼              ▼
┌─────────────┐   ┌──────────────┐   ┌──────────────┐
│   Family    │   │   Account    │   │ Transaction  │
└──────┬──────┘   └──────┬───────┘   └──────┬───────┘
       │                 │                  │
       │                 │                  │
       ▼                 │                  │
┌─────────────┐         │                  │
│FamilyMember │         │                  │
└─────────────┘         │                  │
                        │                  │
                        ▼                  ▼
                 ┌──────────────┐   ┌──────────────┐
                 │   Category   │   │   Receipt    │
                 └──────────────┘   └──────────────┘
                        │
                        │
                        ▼
                 ┌──────────────┐
                 │   Planning   │
                 └──────┬───────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
        ▼               ▼               ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│MonthlyPlan   │ │WeeklyPlan    │ │DailyPlan     │
└──────────────┘ └──────────────┘ └──────────────┘
        │
        ▼
┌──────────────┐
│AnnualPlan    │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│QuarterlyGoal │
└──────────────┘

┌──────────────────┐
│InvestmentAccount │
└────────┬─────────┘
         │
         ▼
┌──────────────────────┐
│InvestmentTransaction │
└──────────────────────┘
```

## 📋 Tabelas

### 1. users
Armazena os usuários do sistema.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | UUID | Identificador único |
| email | String(255) | Email único do usuário |
| username | String(100) | Nome de usuário único |
| hashed_password | String(255) | Senha criptografada |
| full_name | String(255) | Nome completo |
| is_active | Boolean | Se o usuário está ativo |
| is_verified | Boolean | Se o email foi verificado |
| role | Enum | Role do usuário (admin/user) |
| created_at | DateTime | Data de criação |
| updated_at | DateTime | Data de atualização |

### 2. families
Armazena grupos familiares.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | UUID | Identificador único |
| name | String(255) | Nome da família |
| description | String(500) | Descrição |
| created_by | UUID | ID do usuário criador |
| created_at | DateTime | Data de criação |
| updated_at | DateTime | Data de atualização |

### 3. family_members
Relaciona usuários com famílias.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | UUID | Identificador único |
| family_id | UUID | ID da família |
| user_id | UUID | ID do usuário |
| role | Enum | Role na família (owner/admin/member/viewer) |
| joined_at | DateTime | Data de entrada |

### 4. accounts
Armazena contas financeiras.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | UUID | Identificador único |
| name | String(255) | Nome da conta |
| description | String(500) | Descrição |
| account_type | Enum | Tipo (checking/savings/credit_card/cash/other) |
| balance | Decimal(15,2) | Saldo atual |
| initial_balance | Decimal(15,2) | Saldo inicial |
| currency | String(3) | Moeda (BRL) |
| bank_name | String(255) | Nome do banco |
| account_number | String(100) | Número da conta |
| is_active | Boolean | Se está ativa |
| owner_id | UUID | ID do dono (opcional) |
| family_id | UUID | ID da família (opcional) |
| created_at | DateTime | Data de criação |
| updated_at | DateTime | Data de atualização |

### 5. categories
Armazena categorias de transações.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | UUID | Identificador único |
| name | String(255) | Nome da categoria |
| description | String(500) | Descrição |
| category_type | Enum | Tipo (income/expense/transfer) |
| icon | String(50) | Ícone |
| color | String(7) | Cor em hex |
| is_active | Boolean | Se está ativa |
| user_id | UUID | ID do usuário (opcional) |
| family_id | UUID | ID da família (opcional) |
| parent_id | UUID | ID da categoria pai (para subcategorias) |
| created_at | DateTime | Data de criação |
| updated_at | DateTime | Data de atualização |

### 6. transactions
Armazena transações financeiras.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | UUID | Identificador único |
| description | String(500) | Descrição |
| amount | Decimal(15,2) | Valor |
| transaction_type | Enum | Tipo (income/expense/transfer) |
| status | Enum | Status (pending/completed/cancelled) |
| transaction_date | DateTime | Data da transação |
| notes | Text | Observações |
| user_id | UUID | ID do usuário |
| account_id | UUID | ID da conta |
| category_id | UUID | ID da categoria (opcional) |
| receipt_id | UUID | ID da nota fiscal (opcional) |
| created_at | DateTime | Data de criação |
| updated_at | DateTime | Data de atualização |

### 7. plannings
Armazena planejamentos financeiros.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | UUID | Identificador único |
| name | String(255) | Nome do planejamento |
| description | Text | Descrição |
| planning_type | Enum | Tipo (monthly/weekly/daily/annual) |
| start_date | DateTime | Data de início |
| end_date | DateTime | Data de fim |
| target_amount | Decimal(15,2) | Valor alvo |
| actual_amount | Decimal(15,2) | Valor atual alcançado |
| is_active | Boolean | Se está ativo |
| user_id | UUID | ID do usuário |
| category_id | UUID | ID da categoria (opcional) |
| created_at | DateTime | Data de criação |
| updated_at | DateTime | Data de atualização |

### 8. monthly_plannings
Detalhes de planejamentos mensais.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | UUID | Identificador único |
| planning_id | UUID | ID do planejamento |
| month | Integer | Mês (1-12) |
| year | Integer | Ano |
| target_amount | Decimal(15,2) | Valor alvo |
| actual_amount | Decimal(15,2) | Valor atual |

### 9. weekly_plannings
Detalhes de planejamentos semanais.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | UUID | Identificador único |
| planning_id | UUID | ID do planejamento |
| week_number | Integer | Semana do ano (1-52) |
| year | Integer | Ano |
| start_date | DateTime | Data de início |
| end_date | DateTime | Data de fim |
| target_amount | Decimal(15,2) | Valor alvo |
| actual_amount | Decimal(15,2) | Valor atual |

### 10. daily_plannings
Detalhes de planejamentos diários.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | UUID | Identificador único |
| planning_id | UUID | ID do planejamento |
| date | DateTime | Data |
| target_amount | Decimal(15,2) | Valor alvo |
| actual_amount | Decimal(15,2) | Valor atual |

### 11. annual_plannings
Detalhes de planejamentos anuais.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | UUID | Identificador único |
| planning_id | UUID | ID do planejamento |
| year | Integer | Ano |
| target_amount | Decimal(15,2) | Valor alvo |
| actual_amount | Decimal(15,2) | Valor atual |

### 12. quarterly_goals
Metas trimestrais dentro de planejamentos anuais.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | UUID | Identificador único |
| annual_planning_id | UUID | ID do planejamento anual |
| quarter | Integer | Trimestre (1-4) |
| target_amount | Decimal(15,2) | Valor alvo |
| actual_amount | Decimal(15,2) | Valor atual |
| description | Text | Descrição da meta |

### 13. receipts
Armazena notas fiscais cadastradas.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | UUID | Identificador único |
| qr_code_data | Text | Dados do QR Code |
| access_key | String(44) | Chave de acesso da NFe |
| number | String(20) | Número da nota |
| series | String(10) | Série da nota |
| issuer_cnpj | String(14) | CNPJ do emitente |
| issuer_name | String(255) | Nome do emitente |
| total_amount | Decimal(15,2) | Valor total |
| issue_date | DateTime | Data de emissão |
| items_data | JSONB | Dados dos itens (JSON) |
| raw_data | JSONB | Dados brutos (JSON completo) |
| notes | Text | Observações |
| is_processed | Boolean | Se já foi processada |
| user_id | UUID | ID do usuário |
| created_at | DateTime | Data de criação |
| updated_at | DateTime | Data de atualização |

### 14. investment_accounts
Armazena contas de investimento.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | UUID | Identificador único |
| name | String(255) | Nome da conta |
| description | Text | Descrição |
| account_type | Enum | Tipo (stock_broker/bank/crypto_exchange/etc) |
| institution_name | String(255) | Nome da instituição |
| account_number | String(100) | Número da conta |
| current_balance | Decimal(15,2) | Saldo atual |
| initial_balance | Decimal(15,2) | Saldo inicial |
| currency | String(3) | Moeda |
| is_active | Boolean | Se está ativa |
| user_id | UUID | ID do usuário |
| created_at | DateTime | Data de criação |
| updated_at | DateTime | Data de atualização |

### 15. investment_transactions
Armazena transações de investimento.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | UUID | Identificador único |
| investment_type | Enum | Tipo (stock/bond/fund/crypto/etc) |
| transaction_type | Enum | Tipo (buy/sell/dividend/interest/fee/transfer) |
| symbol | String(20) | Símbolo do ativo |
| quantity | Decimal(15,6) | Quantidade |
| unit_price | Decimal(15,6) | Preço unitário |
| total_amount | Decimal(15,2) | Valor total |
| fees | Decimal(15,2) | Taxas |
| transaction_date | DateTime | Data da transação |
| notes | Text | Observações |
| account_id | UUID | ID da conta de investimento |
| created_at | DateTime | Data de criação |
| updated_at | DateTime | Data de atualização |

## 🔗 Relacionamentos

- **User** → **FamilyMember** → **Family**
- **User** → **Account** (1:N)
- **User** → **Transaction** (1:N)
- **User** → **Planning** (1:N)
- **User** → **Receipt** (1:N)
- **User** → **InvestmentAccount** (1:N)
- **Family** → **Account** (1:N)
- **Account** → **Transaction** (1:N)
- **Category** → **Transaction** (1:N)
- **Category** → **Category** (auto-relacionamento para subcategorias)
- **Planning** → **MonthlyPlanning** (1:N)
- **Planning** → **WeeklyPlanning** (1:N)
- **Planning** → **DailyPlanning** (1:N)
- **Planning** → **AnnualPlanning** (1:N)
- **AnnualPlanning** → **QuarterlyGoal** (1:N)
- **Receipt** → **Transaction** (1:N)
- **InvestmentAccount** → **InvestmentTransaction** (1:N)

## 📈 Índices

- `users.email` (unique)
- `users.username` (unique)
- `receipts.access_key` (unique)
- `family_members.family_id` + `family_members.user_id` (composto)

## 🔒 Constraints

- Valores monetários usam `Decimal(15,2)` para precisão
- Datas são armazenadas com timezone (UTC)
- UUIDs são usados como chaves primárias
- Soft deletes podem ser implementados via `is_active`

