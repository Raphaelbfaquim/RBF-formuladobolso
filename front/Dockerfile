FROM node:20-alpine AS base

# Instalar dependências apenas quando necessário
FROM base AS deps
RUN apk add --no-cache libc6-compat
WORKDIR /app

# Copiar arquivos de dependências
COPY package.json package-lock.json* ./
RUN npm ci

# Build da aplicação
FROM base AS builder
WORKDIR /app

# Copiar node_modules primeiro
COPY --from=deps /app/node_modules ./node_modules

# Copiar todos os arquivos (exceto node_modules que já foi copiado)
COPY package.json package-lock.json* ./
COPY next.config.js tsconfig.json tailwind.config.ts postcss.config.js ./
COPY src ./src

# Criar diretório public (Next.js precisa dele, mesmo que vazio)
RUN mkdir -p public
# Copiar public se existir e tiver arquivos
COPY public ./public

# Variável de ambiente para build (será sobrescrita no docker-compose)
ARG NEXT_PUBLIC_API_URL=http://localhost:8000
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL

# Verificar se arquivos foram copiados
RUN ls -la src/lib/api/ && cat src/lib/api/client.ts | head -5

# Limpar cache do Next.js e build
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

EXPOSE 3000

ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

# Usar o servidor standalone do Next.js
CMD ["node", "server.js"]

