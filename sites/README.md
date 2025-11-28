# Sites de Vendas

Esta pasta contém todos os sites de vendas do projeto.

## Estrutura

```
sites/
├── formula-bolso/          # Site de marketing do FormuladoBolso
├── loja-exemplo/            # Template para novos sites
└── README.md               # Este arquivo
```

## Como Adicionar um Novo Site de Vendas

### 1. Criar a Estrutura do Site

```bash
# Copiar o template
cp -r sites/loja-exemplo sites/nome-da-sua-loja

# Ou criar do zero usando Next.js
cd sites
npx create-next-app@latest nome-da-sua-loja --typescript --tailwind --app
```

### 2. Configurar o Dockerfile

Cada site precisa de um `Dockerfile` na raiz do diretório. Use o template:

```dockerfile
FROM node:20-slim AS base

# Instalar dependências
FROM base AS deps
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm install --legacy-peer-deps

# Build da aplicação
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY package.json package-lock.json* ./
COPY tsconfig.json next.config.js tailwind.config.ts postcss.config.js ./
COPY src ./src
RUN mkdir -p public
RUN rm -rf .next
RUN npm run build

# Imagem de produção
FROM base AS runner
WORKDIR /app
ENV NODE_ENV=production
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs
COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static
USER nextjs
EXPOSE 3002  # Use portas diferentes para cada site (3001, 3002, 3003...)
ENV PORT=3002
ENV HOSTNAME="0.0.0.0"
CMD ["node", "server.js"]
```

**Importante:** Configure `output: 'standalone'` no `next.config.js`:

```javascript
const nextConfig = {
  output: 'standalone',
  // ... outras configurações
}
```

### 3. Adicionar ao docker-compose.prod.yml

Adicione um novo serviço no `docker-compose.prod.yml`:

```yaml
  nome-da-loja:
    image: ${DOCKER_USERNAME:-faquim}/formulado-loja-nome:${IMAGE_TAG:-latest}
    container_name: formulado_loja_nome
    ports:
      - "3002:3002"  # Use uma porta diferente
    environment:
      - NODE_ENV=production
    networks:
      - formulado_network
    restart: unless-stopped
```

### 4. Configurar Nginx

Adicione uma rota no `nginx/nginx.conf`:

**Opção A: Usando Path (ex: `/loja1`)**

```nginx
# Loja de Vendas - /loja1
location /loja1 {
    proxy_pass http://nome-da-loja;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection 'upgrade';
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_cache_bypass $http_upgrade;
}
```

**Opção B: Usando Subdomínio (ex: `loja1.formuladobolso.com`)**

```nginx
server {
    listen 80;
    server_name loja1.formuladobolso.com;
    
    location / {
        proxy_pass http://nome-da-loja;
        # ... configurações de proxy
    }
}
```

### 5. Atualizar Scripts de Deploy

Adicione o novo site ao `deploy-build-push.ps1`:

```powershell
# Adicionar na lista de serviços válidos
if ($service -notin @("api", "front", "marketing", "loja-nome", "all")) {
    # ...
}

# Adicionar build do novo site
if ($buildLojaNome) {
    Write-Host "Buildando Loja Nome..." -ForegroundColor Yellow
    docker build -t ${DOCKER_USERNAME}/formulado-loja-nome:${IMAGE_TAG} -f sites/nome-da-loja/Dockerfile sites/nome-da-loja/
    # ... push
}
```

### 6. Build e Deploy

```powershell
# Build e push
powershell -ExecutionPolicy Bypass -File .\deploy-build-push.ps1 loja-nome

# Deploy
powershell -ExecutionPolicy Bypass -File .\deploy-server.ps1 all
```

## Portas Disponíveis

- `3000` - Frontend (dashboard)
- `3001` - Marketing (formula-bolso)
- `3002` - Loja 1
- `3003` - Loja 2
- `3004` - Loja 3
- ... (continue a sequência)

## Convenções de Nomenclatura

- **Diretório:** `sites/nome-da-loja` (kebab-case)
- **Container:** `formulado_loja_nome` (snake_case)
- **Imagem Docker:** `formulado-loja-nome` (kebab-case)
- **Porta:** Sequencial (3002, 3003, 3004...)

## Checklist para Novo Site

- [ ] Criar diretório em `sites/`
- [ ] Criar `Dockerfile` com porta única
- [ ] Configurar `next.config.js` com `output: 'standalone'`
- [ ] Adicionar serviço no `docker-compose.prod.yml`
- [ ] Adicionar rota no `nginx/nginx.conf`
- [ ] Atualizar `deploy-build-push.ps1`
- [ ] Atualizar `deploy-server.ps1` (se necessário)
- [ ] Fazer build e push da imagem
- [ ] Fazer deploy no servidor
- [ ] Testar acesso

## Exemplo Completo

Veja `sites/formula-bolso/` como referência de um site completo funcionando.

