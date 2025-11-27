# 📅 Proposta: Calendário Social e Compartilhado

## 🎯 Conceito

Um calendário unificado que integra:
- **Eventos Financeiros** (transações, contas a pagar, metas)
- **Eventos Pessoais** (viagens, aniversários, eventos importantes)
- **Comunicação** (comentários, lembretes compartilhados)
- **Visualização Compartilhada** (via Workspace/Família)

## 🚀 Funcionalidades Principais

### 1. **Tipos de Eventos**

#### 📊 Eventos Financeiros (Automáticos)
- **Transações** - Receitas e despesas do dia
- **Contas a Pagar/Receber** - Vencimentos destacados
- **Metas** - Datas importantes de metas financeiras
- **Contribuições para Metas** - Quando alguém contribui

#### 🎉 Eventos Pessoais (Cadastrados)
- **Viagens** - Data de partida/retorno, destino
- **Aniversários** - Aniversários de membros da família
- **Eventos Importantes** - Casamentos, formaturas, etc.
- **Lembretes** - Notas e lembretes pessoais

### 2. **Visualização**

#### 📅 Calendário Mensal
- Grid mensal com todos os eventos
- Cores diferentes por tipo:
  - 💰 Verde: Receitas
  - 🔴 Vermelho: Despesas
  - 📋 Laranja: Contas a pagar
  - 🎯 Azul: Metas
  - ✈️ Roxo: Viagens
  - 🎂 Rosa: Aniversários
  - 📝 Cinza: Eventos/lembretes

#### 📊 Visualização por Dia
- Ao clicar em um dia:
  - Lista completa de eventos
  - Saldo do dia (financeiro)
  - Comentários e comunicações
  - Ações rápidas

#### 👥 Visualização Compartilhada
- Ver eventos de todos os membros do workspace/família
- Filtro por pessoa
- Indicador de quem criou o evento

### 3. **Comunicação e Colaboração**

#### 💬 Comentários em Eventos
- Comentar em qualquer evento
- Notificações quando alguém comenta
- Thread de conversas

#### 🔔 Lembretes Compartilhados
- Criar lembretes que todos veem
- Notificações antes do evento
- Marcar como "visto" ou "confirmado"

#### 👤 Indicadores de Participação
- Ver quem confirmou presença
- Ver quem visualizou o evento
- Status: "Vou", "Talvez", "Não vou"

### 4. **Integração com Dados Existentes**

#### 🔗 Eventos Automáticos
- Transações aparecem automaticamente
- Contas a pagar aparecem no vencimento
- Metas aparecem nas datas importantes
- Aniversários de membros da família aparecem automaticamente

#### 📈 Projeção Financeira
- Saldo projetado por dia
- Alertas de saldo negativo futuro
- Gráfico de fluxo de caixa no calendário

## 🗄️ Estrutura de Dados

### Modelo: CalendarEvent

```python
class CalendarEventType(str, enum.Enum):
    # Financeiros
    TRANSACTION = "transaction"
    BILL = "bill"
    GOAL = "goal"
    GOAL_CONTRIBUTION = "goal_contribution"
    
    # Pessoais
    TRAVEL = "travel"
    BIRTHDAY = "birthday"
    IMPORTANT_EVENT = "important_event"
    REMINDER = "reminder"
    CUSTOM = "custom"

class CalendarEvent(Base):
    id: UUID
    event_type: CalendarEventType
    title: str
    description: Optional[str]
    start_date: datetime
    end_date: Optional[datetime]  # Para eventos com duração
    all_day: bool  # Evento de dia inteiro
    
    # Relacionamentos
    user_id: UUID  # Criador do evento
    workspace_id: Optional[UUID]  # Workspace compartilhado
    family_id: Optional[UUID]  # Família compartilhada
    
    # Dados específicos por tipo
    related_transaction_id: Optional[UUID]
    related_bill_id: Optional[UUID]
    related_goal_id: Optional[UUID]
    
    # Personalização
    color: Optional[str]  # Cor personalizada
    icon: Optional[str]  # Ícone personalizado
    location: Optional[str]  # Local (para viagens, eventos)
    
    # Compartilhamento
    is_shared: bool  # Se é compartilhado no workspace/família
    is_public: bool  # Se todos podem ver
    
    # Metadados
    created_at: datetime
    updated_at: datetime
    created_by: UUID
```

### Modelo: CalendarEventComment

```python
class CalendarEventComment(Base):
    id: UUID
    event_id: UUID
    user_id: UUID
    comment: str
    created_at: datetime
    updated_at: datetime
```

### Modelo: CalendarEventParticipant

```python
class EventParticipationStatus(str, enum.Enum):
    GOING = "going"
    MAYBE = "maybe"
    NOT_GOING = "not_going"
    NOT_RESPONDED = "not_responded"

class CalendarEventParticipant(Base):
    id: UUID
    event_id: UUID
    user_id: UUID
    status: EventParticipationStatus
    responded_at: datetime
```

## 🎨 Interface do Usuário

### 1. **Calendário Principal**
```
┌─────────────────────────────────────────┐
│  📅 Calendário  [Nov 2025]  [<] [>]    │
├─────────────────────────────────────────┤
│  Dom Seg Ter Qua Qui Sex Sáb            │
│  [1] [2] [3] [4] [5] [6] [7]            │
│  💰💰  🔴   📋   🎯   ✈️   🎂   📝      │
│  [8] [9] [10][11][12][13][14]           │
│  ...                                     │
└─────────────────────────────────────────┘
```

### 2. **Modal de Evento**
```
┌─────────────────────────────────────────┐
│  ✈️ Viagem para Paris                   │
│  📅 15/12/2025 - 20/12/2025             │
│  📍 Paris, França                       │
│                                         │
│  Viagem de férias com a família        │
│                                         │
│  👥 Participantes:                      │
│  ✅ João (você)                          │
│  ⏳ Maria (não respondeu)               │
│                                         │
│  💬 Comentários (3):                    │
│  João: "Não esqueçam o passaporte!"    │
│  Maria: "Já reservei o hotel"          │
│                                         │
│  [Adicionar Comentário]                 │
│  [Confirmar Presença]                   │
└─────────────────────────────────────────┘
```

### 3. **Filtros e Visualizações**
- Toggle de tipos de eventos
- Filtro por pessoa (workspace/família)
- Visualização: Mês / Semana / Dia
- Busca de eventos

## 🔧 Implementação Técnica

### Backend
1. **Modelos** (`calendar_event.py`)
2. **Schemas** (`calendar.py`)
3. **Repositórios** (`calendar_repository.py`)
4. **Use Cases** (`calendar_use_cases.py`)
5. **Rotas** (`calendar.py`)

### Frontend
1. **Página Principal** (`calendar/page.tsx`)
2. **Componente de Calendário** (`CalendarGrid.tsx`)
3. **Modal de Evento** (`EventModal.tsx`)
4. **Formulário de Evento** (`EventForm.tsx`)
5. **Comentários** (`EventComments.tsx`)

## 📋 MVP - Fase 1

### Funcionalidades Essenciais
1. ✅ Visualização mensal do calendário
2. ✅ Criar eventos pessoais (viagens, aniversários, eventos)
3. ✅ Eventos financeiros automáticos (transações, contas, metas)
4. ✅ Visualização compartilhada (workspace/família)
5. ✅ Comentários em eventos
6. ✅ Filtros básicos

### Próximas Fases
- Fase 2: Confirmação de presença, notificações
- Fase 3: Integração com Google Calendar
- Fase 4: Análise e insights do calendário

## 🎯 Diferenciais

1. **Integração Financeira + Pessoal** - Único lugar para ver tudo
2. **Colaboração Familiar** - Todos veem e comentam
3. **Automático** - Eventos financeiros aparecem sozinhos
4. **Contextual** - Comentários e lembretes no contexto certo
5. **Visual** - Interface intuitiva e colorida


