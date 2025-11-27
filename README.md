# 💰 FormuladoBolso

Sistema completo de gerenciamento financeiro pessoal e familiar com arquitetura moderna e design inovador.

## 🏗️ Arquitetura

O projeto está organizado em duas partes principais:

```
FormuladoBolso/
├── back/          # Backend (Python/FastAPI)
│   ├── src/       # Código fonte
│   ├── alembic/   # Migrações
│   └── ...
│
└── front/         # Frontend (Next.js/React)
    ├── src/       # Código fonte
    └── ...
```

## 🚀 Tecnologias

### Backend
- **Python 3.12+**
- **FastAPI** - Framework web assíncrono
- **PostgreSQL** - Banco de dados
- **Redis** - Cache
- **SQLAlchemy 2.0** - ORM
- **Alembic** - Migrações
- **DDD** - Domain-Driven Design

### Frontend
- **Next.js 14** - Framework React
- **TypeScript** - Type safety
- **Tailwind CSS** - Estilização
- **shadcn/ui** - Componentes
- **Framer Motion** - Animações
- **React Query** - Estado e cache
- **Zustand** - Estado global

## 🎨 Design System

O frontend utiliza um design único e inovador:

- **Glassmorphism** - Efeito de vidro fosco moderno
- **Neumorphism** - Elementos 3D suaves
- **Dark Mode First** - Otimizado para dark mode
- **Gradientes dinâmicos** - Cores que mudam com contexto
- **Micro-interações** - Animações sutis e elegantes

### Paleta de Cores
- **Primary**: Indigo vibrante (#6366f1)
- **Success**: Verde esmeralda (#10b981)
- **Warning**: Âmbar (#f59e0b)
- **Error**: Vermelho coral (#ef4444)
- **Info**: Azul céu (#3b82f6)

## 📋 Funcionalidades

### ✅ Implementadas
- ✅ Autenticação e autorização
- ✅ Gerenciamento de usuários
- ✅ Workspaces/Contextos financeiros
- ✅ Contas financeiras
- ✅ Transações
- ✅ Categorias
- ✅ Planejamentos (mensal, semanal, diário, anual)
- ✅ Metas e sonhos
- ✅ Contas a pagar/receber
- ✅ Notas fiscais (QR Code)
- ✅ Investimentos
- ✅ Gamificação
- ✅ Relatórios
- ✅ Dashboard
- ✅ Chatbot com IA
- ✅ Previsões
- ✅ Insights automáticos
- ✅ Análise de hábitos
- ✅ Open Banking (estrutura)
- ✅ Educação financeira
- ✅ Colaboração familiar
- ✅ Segurança (2FA, logs de auditoria)
- ✅ **Filtros e busca avançada**
- ✅ **Transferências entre contas**
- ✅ **Agendamento de transações**
- ✅ **Calendário financeiro**
- ✅ **Sistema de logs completo**

## 🚀 Deploy na AWS

### Deploy Automático

```bash
# Deploy completo (interativo)
make deploy

# Apenas frontend (AWS Lightsail)
.\scripts\deploy-direto-aws.ps1

# Apenas backend ()
```

**Custo**: Gratuito (AWS Lightsail) ou ~R$ 35/mês (com PostgreSQL pago)

📚 **Guia completo**: [docs/DEPLOY.md](./docs/DEPLOY.md) | [DEPLOY_QUICK.md](./DEPLOY_QUICK.md)

---

## 🚀 Como Executar (Local)

### Backend

```bash
cd back

# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
cp .env.example .env
# Editar .env com suas configurações

# Executar migrações
alembic upgrade head

# Iniciar servidor
uvicorn src.presentation.api.main:app --reload
```

Backend estará disponível em: `http://localhost:8000`
Documentação: `http://localhost:8000/docs`

### Frontend

```bash
cd front

# Instalar dependências
npm install

# Configurar variáveis de ambiente
# Criar .env.local com:
# NEXT_PUBLIC_API_URL=http://localhost:8000

# Iniciar servidor de desenvolvimento
npm run dev
```

Frontend estará disponível em: `http://localhost:3000`

## 📚 Documentação

- [Planejamento do Frontend](./docs/FRONTEND_PLANNING.md)
- [Análise do Sistema](./docs/SYSTEM_ANALYSIS.md)
- [Funcionalidades Faltando](./docs/MISSING_FEATURES.md)

## 🛠️ Desenvolvimento

### Backend
- Estrutura DDD (Domain-Driven Design)
- Testes: `pytest`
- Linting: `ruff` ou `black`
- Type checking: `mypy`

### Frontend
- Type checking: `npm run type-check`
- Linting: `npm run lint`
- Build: `npm run build`

## 📝 Próximos Passos

1. Implementar componentes do frontend
2. Criar páginas de autenticação
3. Implementar dashboard
4. Adicionar gráficos e visualizações
5. Implementar PWA

## 📄 Licença

Este projeto é privado e proprietário.

---

**FormuladoBolso** - Gestão Financeira Inteligente 💰
