# 📋 Plano do Site de Marketing - FormuladoBolso

## 🎯 Objetivo
Criar um site empresarial moderno e profissional para divulgar e vender o sistema FormuladoBolso, destacando todas as funcionalidades e diferenciais competitivos.

---

## 📄 Estrutura de Páginas

### 1. **Home / Landing Page** (`/`)
**Objetivo:** Primeira impressão impactante, conversão imediata

**Conteúdo:**
- Hero section com headline forte
- Value proposition clara
- Diferenciais principais (3-4 cards)
- Call-to-action destacado
- Depoimentos/testimonials
- Números/estatísticas (se houver)
- CTA final para começar

**Diferenciais a destacar:**
- 🤖 IA Financeira Pessoal (Chatbot Inteligente)
- 👨‍👩‍👧‍👦 Colaboração Familiar Completa
- 🎮 Gamificação e Educação Financeira
- 📊 Insights Automáticos e Previsões
- 🔒 Segurança Avançada (2FA, Open Banking)

---

### 2. **Funcionalidades** (`/features`)
**Objetivo:** Detalhar todas as capacidades do sistema

**Seções:**
1. **Gestão Financeira Básica**
   - Contas múltiplas
   - Transações detalhadas
   - Categorização inteligente
   - Saldos em tempo real

2. **Planejamento e Orçamento**
   - Planejamento mensal/semanal/diário
   - Metas e sonhos
   - Contas a pagar/receber
   - Alertas de vencimento

3. **Análise e Insights**
   - Dashboard interativo
   - Relatórios PDF/Excel
   - Insights automáticos
   - Previsões com IA
   - Análise de hábitos

4. **Colaboração Familiar**
   - Workspaces compartilhados
   - Permissões granulares
   - Chat familiar
   - Aprovações de gastos

5. **IA e Automação**
   - Chatbot financeiro 24/7
   - Categorização automática
   - OCR de notas fiscais
   - Open Banking (sincronização automática)

6. **Gamificação e Educação**
   - Sistema de níveis e badges
   - Desafios financeiros
   - Conteúdo educativo
   - Quizzes interativos

7. **Segurança**
   - Autenticação 2FA
   - Logs de auditoria
   - Criptografia de dados
   - Backup automático

---

### 3. **Diferenciais** (`/diferenciais`)
**Objetivo:** Mostrar o que nos torna únicos

**Destaques:**
1. **IA Financeira Pessoal**
   - Assistente virtual que entende contexto
   - Recomendações personalizadas
   - Análise preditiva

2. **Colaboração Familiar Avançada**
   - Permissões granulares por módulo
   - Workspaces isolados
   - Chat integrado

3. **Gamificação Completa**
   - Transforma finanças em jogo
   - Motivação através de conquistas
   - Educação financeira divertida

4. **Open Banking Nativo**
   - Integração com bancos brasileiros
   - Sincronização automática
   - Reconciliação inteligente

5. **Design Moderno e Intuitivo**
   - Glassmorphism
   - Dark mode nativo
   - Interface responsiva

---

### 4. **Preços** (`/pricing`)
**Objetivo:** Apresentar planos e valores

**Planos sugeridos:**
- **Básico** (Gratuito ou R$ 9,90/mês)
- **Premium** (R$ 29,90/mês)
- **Família** (R$ 49,90/mês)
- **Empresarial** (Sob consulta)

---

### 5. **Sobre** (`/sobre`)
**Objetivo:** Contar a história e missão

**Conteúdo:**
- História da empresa
- Missão e visão
- Valores
- Equipe (se aplicável)

---

### 6. **Contato** (`/contato`)
**Objetivo:** Canal de comunicação

**Formulário de contato:**
- Nome
- Email
- Telefone
- Mensagem
- Tipo de interesse (venda, suporte, parceria)

---

## 🎨 Design e UX

### Estilo Visual
- **Moderno e profissional**
- **Cores:** Gradientes indigo/purple (mesma paleta do sistema)
- **Tipografia:** Limpa e legível
- **Imagens:** Ilustrações modernas ou screenshots do sistema
- **Animações:** Suaves e profissionais

### Componentes Principais
1. **Hero Section** - Grande, impactante, com CTA
2. **Feature Cards** - Cards com ícones e descrições
3. **Comparison Table** - Comparação com concorrentes
4. **Testimonials** - Depoimentos de clientes
5. **CTA Sections** - Múltiplos pontos de conversão
6. **Footer** - Links, contato, redes sociais

---

## 🚀 Tecnologias

- **Next.js 14** (App Router)
- **TypeScript**
- **Tailwind CSS**
- **Framer Motion** (animações)
- **React Icons**

---

## 📍 Estrutura de Arquivos

```
sites/formula-bolso/
├── package.json
├── next.config.js
├── tailwind.config.ts
├── tsconfig.json
├── public/
│   ├── images/
│   └── icons/
└── src/
    ├── app/
    │   ├── layout.tsx
    │   ├── page.tsx (Home)
    │   ├── features/
    │   │   └── page.tsx
    │   ├── diferenciais/
    │   │   └── page.tsx
    │   ├── pricing/
    │   │   └── page.tsx
    │   ├── sobre/
    │   │   └── page.tsx
    │   └── contato/
    │       └── page.tsx
    ├── components/
    │   ├── Hero.tsx
    │   ├── FeatureCard.tsx
    │   ├── PricingCard.tsx
    │   ├── Testimonial.tsx
    │   ├── CTA.tsx
    │   ├── Header.tsx
    │   └── Footer.tsx
    └── styles/
        └── globals.css
```

---

## ✅ Checklist de Implementação

- [ ] Estrutura do projeto Next.js
- [ ] Página Home com Hero
- [ ] Página de Funcionalidades
- [ ] Página de Diferenciais
- [ ] Página de Preços
- [ ] Página Sobre
- [ ] Página de Contato
- [ ] Componentes reutilizáveis
- [ ] Responsividade mobile
- [ ] Animações e transições
- [ ] SEO básico
- [ ] Links para sistema principal
- [ ] Formulário de contato funcional

---

## 🎯 Call-to-Actions (CTAs)

**Principais CTAs:**
1. "Comece Grátis" - Link para registro
2. "Experimente Agora" - Link para demo
3. "Fale Conosco" - Link para contato
4. "Ver Preços" - Link para pricing
5. "Acessar Sistema" - Link para login

**Links principais:**
- Sistema: `http://3.238.162.190` ou domínio próprio
- Registro: `/register`
- Login: `/login`

---

## 📊 Métricas de Sucesso

- Taxa de conversão (visitas → registros)
- Tempo na página
- Taxa de rejeição
- Páginas mais visitadas
- Origem do tráfego

---

## 🚀 Próximos Passos

1. Criar estrutura do projeto
2. Implementar Home page
3. Implementar páginas secundárias
4. Adicionar componentes
5. Testar responsividade
6. Deploy

