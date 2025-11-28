FROM node:20-slim AS base

# Instalar dependências
FROM base AS deps
WORKDIR /app

# Copiar arquivos de dependências
COPY package.json package-lock.json* ./
RUN npm install --legacy-peer-deps

# Build da aplicação
FROM base AS builder
WORKDIR /app

# Copiar node_modules do stage deps
COPY --from=deps /app/node_modules ./node_modules

# Copiar arquivos de configuração
COPY package.json package-lock.json* ./
COPY tsconfig.json next.config.js tailwind.config.ts postcss.config.js ./

# Copiar código fonte
COPY src ./src

# Criar diretório public (Next.js precisa)
# Se o diretório public existir, será copiado, senão será criado vazio
RUN mkdir -p public

# Limpar cache e build
RUN rm -rf .next
RUN npm run build

# Imagem de produção
FROM base AS runner
WORKDIR /app

ENV NODE_ENV=production

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# Copiar arquivos necessários
COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3001

ENV PORT=3001
ENV HOSTNAME="0.0.0.0"

# Usar o servidor standalone do Next.js
CMD ["node", "server.js"]

