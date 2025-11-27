# FormuladoBolso - Frontend

Frontend moderno e inovador para o sistema de gestão financeira FormuladoBolso.

## 🚀 Tecnologias

- **Next.js 14** - Framework React com App Router
- **TypeScript** - Type safety
- **Tailwind CSS** - Estilização
- **shadcn/ui** - Componentes base
- **Framer Motion** - Animações
- **React Query** - Gerenciamento de estado e cache
- **Zustand** - Estado global leve

## 📦 Instalação

```bash
# Instalar dependências
npm install

# Rodar em desenvolvimento
npm run dev

# Build para produção
npm run build

# Rodar produção
npm start
```

## 🎨 Design System

O design utiliza:
- **Glassmorphism** - Efeito de vidro fosco
- **Neumorphism** - Elementos 3D suaves
- **Dark Mode First** - Otimizado para dark mode
- **Gradientes dinâmicos** - Cores que mudam com contexto

## 📁 Estrutura

```
src/
├── app/              # App Router (Next.js 14)
├── components/       # Componentes reutilizáveis
├── lib/              # Utilitários e helpers
├── stores/           # Estado global (Zustand)
├── types/            # TypeScript types
└── styles/           # Estilos globais
```

## 🔗 API

O frontend se conecta ao backend em `http://localhost:8000` por padrão.
Configure via variável de ambiente `NEXT_PUBLIC_API_URL`.

## 📝 Próximos Passos

1. Implementar autenticação
2. Criar dashboard
3. Implementar páginas de transações
4. Adicionar gráficos e visualizações
5. Implementar workspaces

