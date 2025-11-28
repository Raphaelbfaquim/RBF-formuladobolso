# Script para adicionar um novo site de vendas
# Uso: .\scripts\add-new-site.ps1 nome-do-site [porta]

param(
    [Parameter(Mandatory=$true)]
    [string]$siteName,
    
    [Parameter(Mandatory=$false)]
    [int]$port = 0
)

$ErrorActionPreference = "Stop"

# Validar nome do site (kebab-case)
if ($siteName -notmatch '^[a-z0-9-]+$') {
    Write-Host "Erro: Nome do site deve estar em kebab-case (apenas letras minúsculas, números e hífens)" -ForegroundColor Red
    exit 1
}

# Calcular porta se não fornecida
if ($port -eq 0) {
    # Encontrar a próxima porta disponível
    $existingPorts = @(3001) # marketing já usa 3001
    $port = 3001
    do {
        $port++
    } while ($existingPorts -contains $port)
}

$sitePath = "sites\$siteName"
$dockerImageName = "formulado-$siteName"
$containerName = "formulado_$($siteName.Replace('-', '_'))"

Write-Host "=== ADICIONANDO NOVO SITE ===" -ForegroundColor Cyan
Write-Host "Nome: $siteName" -ForegroundColor Yellow
Write-Host "Porta: $port" -ForegroundColor Yellow
Write-Host "Caminho: $sitePath" -ForegroundColor Yellow
Write-Host "Imagem Docker: $dockerImageName" -ForegroundColor Yellow
Write-Host "Container: $containerName" -ForegroundColor Yellow
Write-Host ""

# Verificar se já existe
if (Test-Path $sitePath) {
    Write-Host "Erro: O diretório $sitePath já existe!" -ForegroundColor Red
    exit 1
}

# Criar estrutura básica
Write-Host "Criando estrutura do site..." -ForegroundColor Yellow
New-Item -ItemType Directory -Path "$sitePath\src\app" -Force | Out-Null
New-Item -ItemType Directory -Path "$sitePath\src\components" -Force | Out-Null
New-Item -ItemType Directory -Path "$sitePath\src\styles" -Force | Out-Null

# Criar package.json
$packageJson = @{
    name = $siteName
    version = "1.0.0"
    private = $true
    scripts = @{
        dev = "next dev"
        build = "next build"
        start = "next start"
        lint = "next lint"
    }
    dependencies = @{
        next = "14.2.5"
        react = "^18.3.1"
        "react-dom" = "^18.3.1"
    }
    devDependencies = @{
        "@types/node" = "^20.14.10"
        "@types/react" = "^18.3.3"
        "@types/react-dom" = "^18.3.0"
        autoprefixer = "^10.4.19"
        postcss = "^8.4.39"
        tailwindcss = "^3.4.4"
        typescript = "^5.5.3"
    }
} | ConvertTo-Json -Depth 10

$packageJson | Out-File -FilePath "$sitePath\package.json" -Encoding UTF8

# Criar next.config.js
$nextConfig = @"
/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  images: {
    domains: ['3.238.162.190'],
  },
}

module.exports = nextConfig
"@
$nextConfig | Out-File -FilePath "$sitePath\next.config.js" -Encoding UTF8

# Criar tsconfig.json
$tsconfig = @{
    compilerOptions = @{
        target = "ES2017"
        lib = @("dom", "dom.iterable", "esnext")
        allowJs = $true
        skipLibCheck = $true
        strict = $true
        noEmit = $true
        esModuleInterop = $true
        module = "esnext"
        moduleResolution = "bundler"
        resolveJsonModule = $true
        isolatedModules = $true
        jsx = "preserve"
        incremental = $true
        plugins = @(
            @{
                name = "next"
            }
        )
        paths = @{
            "@/*" = @("./src/*")
        }
    }
    include = @("next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts")
    exclude = @("node_modules")
} | ConvertTo-Json -Depth 10

$tsconfig | Out-File -FilePath "$sitePath\tsconfig.json" -Encoding UTF8

# Criar tailwind.config.ts
$tailwindConfig = @"
import type { Config } from "tailwindcss"

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
export default config
"@
$tailwindConfig | Out-File -FilePath "$sitePath\tailwind.config.ts" -Encoding UTF8

# Criar postcss.config.js
$postcssConfig = @"
module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
"@
$postcssConfig | Out-File -FilePath "$sitePath\postcss.config.js" -Encoding UTF8

# Criar Dockerfile
$dockerfile = @"
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
EXPOSE $port
ENV PORT=$port
ENV HOSTNAME="0.0.0.0"
CMD ["node", "server.js"]
"@
$dockerfile | Out-File -FilePath "$sitePath\Dockerfile" -Encoding UTF8

# Criar página inicial básica
$pageContent = @"
export default function Home() {
  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          Bem-vindo ao $siteName
        </h1>
        <p className="text-gray-600">
          Seu site de vendas está pronto para ser customizado!
        </p>
      </div>
    </div>
  )
}
"@
$pageContent | Out-File -FilePath "$sitePath\src\app\page.tsx" -Encoding UTF8

# Criar layout básico
$layoutContent = @"
import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: '$siteName',
  description: 'Site de vendas',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="pt-BR">
      <body>{children}</body>
    </html>
  )
}
"@
$layoutContent | Out-File -FilePath "$sitePath\src\app\layout.tsx" -Encoding UTF8

# Criar globals.css
$globalsCss = @"
@tailwind base;
@tailwind components;
@tailwind utilities;
"@
$globalsCss | Out-File -FilePath "$sitePath\src\app\globals.css" -Encoding UTF8

# Criar README.md
$readme = @"
# $siteName

Site de vendas criado automaticamente.

## Desenvolvimento

\`\`\`bash
npm install
npm run dev
\`\`\`

## Build e Deploy

Siga as instruções em \`sites/README.md\` para fazer o deploy deste site.
"@
$readme | Out-File -FilePath "$sitePath\README.md" -Encoding UTF8

Write-Host ""
Write-Host "✅ Estrutura do site criada com sucesso!" -ForegroundColor Green
Write-Host ""
Write-Host "PRÓXIMOS PASSOS:" -ForegroundColor Cyan
Write-Host "1. Adicione o serviço ao docker-compose.prod.yml:" -ForegroundColor Yellow
Write-Host "   $containerName:" -ForegroundColor Gray
Write-Host "     image: \`${DOCKER_USERNAME:-faquim}/$dockerImageName:\`${IMAGE_TAG:-latest}" -ForegroundColor Gray
Write-Host "     container_name: $containerName" -ForegroundColor Gray
Write-Host "     ports:" -ForegroundColor Gray
Write-Host "       - `"$port`:$port`"" -ForegroundColor Gray
Write-Host "     environment:" -ForegroundColor Gray
Write-Host "       - NODE_ENV=production" -ForegroundColor Gray
Write-Host "     networks:" -ForegroundColor Gray
Write-Host "       - formulado_network" -ForegroundColor Gray
Write-Host "     restart: unless-stopped" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Adicione rota no nginx/nginx.conf:" -ForegroundColor Yellow
Write-Host "   location /$siteName {" -ForegroundColor Gray
Write-Host "     proxy_pass http://$containerName;" -ForegroundColor Gray
Write-Host "     # ... (copiar configuração de proxy do marketing)" -ForegroundColor Gray
Write-Host "   }" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Instale as dependências:" -ForegroundColor Yellow
Write-Host "   cd $sitePath" -ForegroundColor Gray
Write-Host "   npm install" -ForegroundColor Gray
Write-Host ""
Write-Host "4. Desenvolva seu site e faça deploy:" -ForegroundColor Yellow
Write-Host "   # Adicione '$siteName' aos scripts de deploy" -ForegroundColor Gray
Write-Host "   powershell -ExecutionPolicy Bypass -File .\deploy-build-push.ps1 $siteName" -ForegroundColor Gray
Write-Host ""

