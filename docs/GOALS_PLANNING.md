# 📋 Planejamento: Página de Metas Financeiras

## 🔍 Análise dos Concorrentes

### Funcionalidades Comuns (YNAB, Mint, PocketGuard, GuiaBolso):

1. **Metas Básicas**
   - Criar metas com valor e data
   - Acompanhar progresso com barras
   - Contribuições manuais
   - Tipos pré-definidos (casa, carro, viagem, etc.)

2. **Visualização**
   - Cards com progresso visual
   - Gráficos de evolução
   - Lista de contribuições

3. **Notificações**
   - Lembretes de prazos
   - Alertas de progresso

4. **Gamificação Básica**
   - Badges ao completar metas
   - Níveis de conquista

---

## 💡 Nossas Inovações Propostas

### 1. **Metas Inteligentes com IA** 🤖
- **Sugestão automática de metas** baseada em:
  - Histórico de gastos
  - Receita atual
  - Metas similares de outros usuários
  - Análise de padrões de consumo

- **Previsão de conclusão**:
  - "Com base no seu histórico, você pode alcançar esta meta em X meses"
  - Ajuste automático de data baseado em contribuições

### 2. **Metas com Contribuições Automáticas** 💰
- **Integração com Planejamento Mensal**:
  - Vincular meta ao planejamento 50-30-20
  - Contribuição automática mensal (ex: 20% da poupança vai para a meta)
  - "Arredondamento" de transações (ex: R$ 10,50 → R$ 11,00, R$ 0,50 vai para a meta)

- **Regras de Contribuição**:
  - "Sempre que economizar mais de X% do orçamento, adicionar Y% à meta"
  - Contribuição baseada em categorias (ex: 10% de cada gasto em "Lazer" vai para "Viagem")

### 3. **Metas Compartilhadas (Família/Casais)** 👨‍👩‍👧‍👦
- **Metas em grupo**:
  - Múltiplos usuários contribuindo para a mesma meta
  - Dashboard compartilhado
  - Chat/comentários na meta
  - Divisão proporcional ou igualitária

### 4. **Metas com Sub-objetivos** 🎯
- **Breakdown de metas grandes**:
  - Meta: "Casa própria" (R$ 300.000)
    - Sub-meta 1: "Entrada" (R$ 60.000)
    - Sub-meta 2: "Documentação" (R$ 5.000)
    - Sub-meta 3: "Móveis" (R$ 20.000)
  - Progresso visual por sub-meta

### 5. **Metas com Investimentos** 📈
- **Integração com investimentos**:
  - Vincular meta a investimento específico
  - Cálculo de rentabilidade projetada
  - "Com investimento de X% ao ano, você alcançará em Y meses"
  - Sugestão de produtos financeiros adequados

### 6. **Desafios e Missões** 🏆
- **Desafios temporários**:
  - "Economize R$ 500 em 30 dias"
  - "Não gaste em restaurantes por 1 mês"
  - Recompensas e badges exclusivos
  - Ranking entre usuários (opcional)

### 7. **Metas com Milestones** 🎉
- **Marcos intermediários**:
  - "25% completo" → Badge + Notificação
  - "50% completo" → Badge + Sugestão de ajuste
  - "75% completo" → Badge + Preparação para conclusão
  - Celebração visual ao completar

### 8. **Análise Preditiva** 📊
- **Insights inteligentes**:
  - "Se continuar neste ritmo, alcançará em X meses"
  - "Para alcançar na data, precisa economizar R$ Y/mês"
  - "Você está X% acima/abaixo da média"
  - Sugestões de ajuste de data ou valor

### 9. **Metas Recorrentes** 🔄
- **Metas que se repetem**:
  - "Férias anuais" (todo ano)
  - "Presentes de Natal" (todo dezembro)
  - "IPVA" (todo janeiro)
  - Reinício automático após conclusão

### 10. **Visualização Avançada** 📈
- **Timeline interativa**:
  - Linha do tempo com contribuições
  - Gráfico de evolução mensal
  - Comparação com outras metas
  - Heatmap de contribuições

### 11. **Metas com Categorias de Economia** 💡
- **Sugestão de onde economizar**:
  - "Para alcançar esta meta, você pode economizar R$ X em 'Restaurantes'"
  - Análise de gastos desnecessários
  - "Se reduzir Y% em Z categoria, alcançará 1 mês antes"

### 12. **Metas com Foto/Imagem** 📸
- **Personalização visual**:
  - Upload de foto do objetivo (casa, carro, viagem)
  - Visualização antes/depois
  - Motivação visual

---

## 🎨 Interface Proposta

### Layout Principal:
```
┌─────────────────────────────────────────────────────────┐
│  🎯 Metas e Sonhos                    [+ Nova Meta]      │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  📊 Resumo Geral                                         │
│  ├─ Total em Metas: R$ X                                │
│  ├─ Meta Mais Próxima: "Nome" (X% completo)            │
│  └─ Economia Mensal Necessária: R$ Y                    │
│                                                          │
│  🎯 Minhas Metas                                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │ 🏠 Casa     │  │ 🚗 Carro     │  │ ✈️ Viagem   │    │
│  │ R$ 60k/300k│  │ R$ 15k/50k   │  │ R$ 2k/5k    │    │
│  │ ████░░░░░░ │  │ ████████░░░░ │  │ ████░░░░░░  │    │
│  │ 20% | 18m  │  │ 30% | 8m     │  │ 40% | 3m    │    │
│  └─────────────┘  └─────────────┘  └─────────────┘    │
│                                                          │
│  🏆 Desafios Ativos                                      │
│  ┌──────────────────────────────────────────────────┐  │
│  │ 💪 Economize R$ 500 em 30 dias                   │  │
│  │ ████████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ │  │
│  │ Progresso: 60% | 12 dias restantes               │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
│  📈 Estatísticas                                         │
│  ├─ Metas Concluídas: 5                                │
│  ├─ Total Economizado: R$ 150.000                       │
│  └─ Tempo Médio para Conclusão: 8 meses                │
└─────────────────────────────────────────────────────────┘
```

### Detalhes da Meta:
```
┌─────────────────────────────────────────────────────────┐
│  🏠 Comprar Casa Própria                    [Editar]    │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  📊 Progresso                                            │
│  R$ 60.000 / R$ 300.000                                   │
│  ████████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ │
│  20% completo | R$ 240.000 restantes                    │
│                                                          │
│  📅 Prazo                                                 │
│  Data Objetivo: 25/12/2027                               │
│  Tempo Restante: 18 meses                                │
│  Economia Mensal Necessária: R$ 13.333                   │
│                                                          │
│  💰 Contribuições                                        │
│  ┌──────────────────────────────────────────────────┐  │
│  │ 25/11/2025 | R$ 2.000 | Automática (Poupança)    │  │
│  │ 10/11/2025 | R$ 1.500 | Manual                   │  │
│  │ 01/11/2025 | R$ 3.000 | Automática (Poupança)    │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
│  📈 Projeção                                             │
│  "Com base no seu histórico, você alcançará em 16 meses"│
│                                                          │
│  💡 Sugestões                                             │
│  • Reduza R$ 200/mês em "Restaurantes" para alcançar    │
│    1 mês antes                                           │
│  • Considere investir em CDB para acelerar o prazo      │
│                                                          │
│  🎯 Sub-metas                                            │
│  ├─ ✅ Entrada (R$ 60.000) - 100%                       │
│  ├─ ⏳ Documentação (R$ 5.000) - 0%                      │
│  └─ ⏳ Móveis (R$ 20.000) - 0%                           │
└─────────────────────────────────────────────────────────┘
```

---

## 🚀 Fase 1 - MVP (Implementação Inicial)

### Funcionalidades Essenciais:
1. ✅ Listar metas (já existe)
2. ✅ Criar meta (já existe)
3. ✅ Editar meta (já existe)
4. ✅ Deletar meta (já existe)
5. ✅ Adicionar contribuição (já existe)
6. ⚠️ **Melhorar visualização** (cards mais bonitos)
7. ⚠️ **Filtros** (por status, tipo, data)
8. ⚠️ **Busca** (por nome)
9. ⚠️ **Ordenação** (por data, progresso, valor)

### Melhorias Visuais:
- Cards com gradiente baseado no tipo
- Animações de progresso
- Ícones personalizados por tipo
- Cores dinâmicas baseadas no progresso

---

## 🚀 Fase 2 - Funcionalidades Avançadas

1. **Contribuições Automáticas**
   - Integração com planejamento mensal
   - Regras de contribuição

2. **Análise Preditiva**
   - Cálculo de data estimada
   - Sugestões de ajuste

3. **Milestones**
   - Badges em 25%, 50%, 75%, 100%
   - Notificações de progresso

4. **Sub-metas**
   - Breakdown de metas grandes

---

## 🚀 Fase 3 - Inovações

1. **Metas Compartilhadas**
2. **Desafios e Missões**
3. **Integração com Investimentos**
4. **IA para Sugestões**

---

## 📝 Próximos Passos

1. **Discutir prioridades** - Qual funcionalidade implementar primeiro?
2. **Definir MVP** - O que é essencial para lançar?
3. **Criar mockups** - Visualizar antes de implementar
4. **Implementar** - Começar pela Fase 1

---

## ❓ Perguntas para Discussão

1. Qual funcionalidade você considera mais importante?
2. Devemos começar com MVP simples ou já incluir algumas inovações?
3. Metas compartilhadas são prioritárias?
4. Integração com investimentos é essencial agora?
5. Queremos gamificação desde o início?

