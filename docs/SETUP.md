# 🚀 Setup do Frontend

## Pré-requisitos

Você precisa ter Node.js e npm instalados.

### Instalar Node.js (Linux)

#### Opção 1: Usando nvm (Recomendado)
```bash
# Instalar nvm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash

# Recarregar terminal
source ~/.bashrc

# Instalar Node.js LTS
nvm install --lts
nvm use --lts

# Verificar instalação
node --version
npm --version
```

#### Opção 2: Usando apt (Ubuntu/Debian)
```bash
# Atualizar repositórios
sudo apt update

# Instalar Node.js e npm
sudo apt install nodejs npm

# Verificar versões
node --version
npm --version
```

#### Opção 3: Usando snap
```bash
sudo snap install node --classic
```

### Instalar Node.js (Windows/Mac)

- **Windows**: Baixar de https://nodejs.org/ (versão LTS)
- **Mac**: `brew install node` ou baixar de https://nodejs.org/

## Instalação do Projeto

```bash
# Navegar para a pasta do frontend
cd front

# Instalar dependências
npm install

# Criar arquivo .env.local
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
```

## Executar

```bash
# Modo desenvolvimento
npm run dev

# O frontend estará disponível em:
# http://localhost:3000
```

## Comandos Disponíveis

```bash
# Desenvolvimento
npm run dev

# Build para produção
npm run build

# Executar produção
npm start

# Verificar tipos TypeScript
npm run type-check

# Linting
npm run lint
```

## Troubleshooting

### Erro: "npm não encontrado"
- Instale Node.js seguindo as instruções acima

### Erro: "Port 3000 already in use"
- Pare o processo na porta 3000 ou use outra porta:
  ```bash
  PORT=3001 npm run dev
  ```

### Erro de dependências
- Delete `node_modules` e `package-lock.json` e reinstale:
  ```bash
  rm -rf node_modules package-lock.json
  npm install
  ```

