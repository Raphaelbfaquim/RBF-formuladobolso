# Template para Novo Site de Vendas

Este é um guia rápido para criar um novo site de vendas.

## Passos Rápidos

### 1. Criar o Projeto Next.js

```bash
cd sites
npx create-next-app@latest nome-da-loja --typescript --tailwind --app
cd nome-da-loja
```

### 2. Configurar next.config.js

```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone', // OBRIGATÓRIO para Docker
  images: {
    domains: ['3.238.162.190'],
  },
}

module.exports = nextConfig
```

### 3. Criar Dockerfile

Copie o Dockerfile de `sites/formula-bolso/Dockerfile` e ajuste a porta:

```dockerfile
# ... (copiar de formula-bolso/Dockerfile)
EXPOSE 3002  # MUDAR PARA PORTA ÚNICA DO SEU SITE
ENV PORT=3002
```

### 4. Adicionar ao docker-compose.prod.yml

```yaml
  nome-loja:
    image: ${DOCKER_USERNAME:-faquim}/formulado-loja-nome:${IMAGE_TAG:-latest}
    container_name: formulado_loja_nome
    ports:
      - "3002:3002"
    environment:
      - NODE_ENV=production
    networks:
      - formulado_network
    restart: unless-stopped
```

### 5. Adicionar Rota no Nginx

```nginx
# Antes da rota "/" (marketing)
location /loja-nome {
    proxy_pass http://nome-loja;
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

### 6. Deploy

```powershell
# Build e push
powershell -ExecutionPolicy Bypass -File .\deploy-build-push.ps1 loja-nome

# Deploy
powershell -ExecutionPolicy Bypass -File .\deploy-server.ps1 all
```

## Estrutura Mínima

```
nome-da-loja/
├── Dockerfile
├── next.config.js
├── package.json
├── tailwind.config.ts
├── tsconfig.json
└── src/
    └── app/
        ├── layout.tsx
        └── page.tsx
```

## Dicas

- Use Tailwind CSS para estilização rápida
- Configure `basePath` no `next.config.js` se usar path no nginx (ex: `/loja1`)
- Teste localmente com `npm run dev` antes de fazer deploy
- Use portas sequenciais (3002, 3003, 3004...)

