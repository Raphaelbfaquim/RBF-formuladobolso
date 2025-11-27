# 📝 Fluxo de Criação de Usuário

## 🗄️ Tabela no Banco de Dados

**Tabela:** `users`

**Modelo:** `User`  
**Arquivo:** `back/src/infrastructure/database/models/user.py`

## 🔄 Fluxo Completo

### 1. Endpoint da API
**Arquivo:** `back/src/presentation/api/v1/routes/auth.py`

```python
@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate, ...):
    user = await use_cases.create_user(...)
    return user
```

### 2. Caso de Uso
**Arquivo:** `back/src/application/use_cases/user_use_cases.py`

```python
async def create_user(self, email, username, password, ...):
    # Validações
    # Hash da senha
    user = User(...)  # Cria instância
    return await self.user_repository.create(user)  # Salva no banco
```

### 3. Repositório
**Arquivo:** `back/src/infrastructure/repositories/user_repository.py`

```python
async def create(self, user: User) -> User:
    self.session.add(user)      # Adiciona à sessão
    await self.session.commit()  # Salva no banco
    await self.session.refresh(user)  # Atualiza com dados do banco
    return user
```

### 4. Modelo (Tabela)
**Arquivo:** `back/src/infrastructure/database/models/user.py`

```python
class User(Base):
    __tablename__ = "users"  # ← NOME DA TABELA
    
    id = Column(UUID, primary_key=True)
    email = Column(String(255), unique=True)
    username = Column(String(100), unique=True)
    hashed_password = Column(String(255))
    # ... outros campos
```

## 📊 Estrutura da Tabela `users`

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    phone_number VARCHAR(20),
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    role VARCHAR(20) DEFAULT 'user',
    created_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE
);
```

## 🔍 Verificar no Banco

### Via Script Python
```bash
make check-users
```

### Via SQL Direto
```sql
SELECT * FROM users;
```

### Via psql
```bash
psql -d formuladobolso -c "SELECT id, username, email, created_at FROM users;"
```

## 📝 Campos Criados no Registro

Quando um usuário se registra, os seguintes campos são preenchidos:

- ✅ `id` - UUID gerado automaticamente
- ✅ `email` - Email fornecido
- ✅ `username` - Username fornecido
- ✅ `hashed_password` - Senha criptografada (bcrypt)
- ✅ `full_name` - Nome completo (opcional)
- ✅ `is_active` - `True` (padrão)
- ✅ `is_verified` - `False` (padrão)
- ✅ `role` - `USER` (padrão)
- ✅ `created_at` - Data/hora atual (UTC)
- ✅ `updated_at` - Data/hora atual (UTC)
- ⚪ `phone_number` - `NULL` (pode ser preenchido depois)

## 🔐 Segurança

- Senha é **hasheada** com bcrypt antes de salvar
- Email e username são **únicos** (validação antes de criar)
- Senha nunca é armazenada em texto plano

---

**Tabela:** `users`  
**Banco:** PostgreSQL  
**ORM:** SQLAlchemy

