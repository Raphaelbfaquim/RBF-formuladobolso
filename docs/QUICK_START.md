# 🚀 Quick Start - FormuladoBolso

Guia rápido para executar o sistema completo.

## 📋 Pré-requisitos

### Backend
- Python 3.12+
- PostgreSQL
- Redis (opcional, mas recomendado)

### Frontend
- Node.js 18+ (LTS recomendado)
- npm ou yarn

## 🔧 Instalação Rápida

### 1. Backend

```bash
# Navegar para pasta do backend
cd back

# Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou: venv\Scripts\activate  # Windows

# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
cp env.example .env
# Editar .env com suas configurações

# Executar migrações
alembic upgrade head

# Iniciar servidor
uvicorn src.presentation.api.main:app --reload --host 0.0.0.0 --port 8000
```

Backend estará em: **http://localhost:8000**
Documentação: **http://localhost:8000/docs**

### 2. Frontend

#### Instalar Node.js (se não tiver)

**Linux (NVM - Recomendado):**
```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
source ~/.bashrc
nvm install --lts
nvm use --lts
```

**Linux (APT):**
```bash
sudo apt update
sudo apt install nodejs npm
```

**Windows/Mac:**
- Baixar de https://nodejs.org/ (versão LTS)

#### Instalar e Executar

```bash
# Navegar para pasta do frontend
cd front

# Instalar dependências
npm install

# Criar arquivo de ambiente
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# Iniciar servidor de desenvolvimento
npm run dev
```

Frontend estará em: **http://localhost:3000**

## 🎯 Verificar se está funcionando

### Backend
```bash
# Testar API
curl http://localhost:8000/health

# Ou abrir no navegador
# http://localhost:8000/docs
```

### Frontend
```bash
# Abrir no navegador
# http://localhost:3000
```

## 🐳 Docker (Alternativa)

Se preferir usar Docker:

```bash
# Backend
cd back
docker-compose up -d

# Frontend (precisa instalar Node.js mesmo assim)
cd front
npm install
npm run dev
```

## 📝 Estrutura do Projeto

```
FormuladoBolso/
├── back/          # Backend Python/FastAPI
│   ├── src/
│   ├── alembic/
│   └── ...
│
└── front/         # Frontend Next.js/React
    ├── src/
    └── ...
```

## 🔍 Troubleshooting

### Backend não inicia
- Verificar se PostgreSQL está rodando
- Verificar variáveis de ambiente no `.env`
- Verificar se a porta 8000 está livre

### Frontend não inicia
- Verificar se Node.js está instalado: `node --version`
- Verificar se npm está instalado: `npm --version`
- Deletar `node_modules` e reinstalar: `rm -rf node_modules && npm install`

### Erro de conexão com API
- Verificar se backend está rodando
- Verificar `NEXT_PUBLIC_API_URL` no `.env.local`
- Verificar CORS no backend

## 📚 Mais Informações

- [Planejamento do Frontend](./docs/FRONTEND_PLANNING.md)
- [Setup Detalhado do Frontend](./front/SETUP.md)
- [Análise do Sistema](./docs/SYSTEM_ANALYSIS.md)

---

**FormuladoBolso** - Gestão Financeira Inteligente 💰

