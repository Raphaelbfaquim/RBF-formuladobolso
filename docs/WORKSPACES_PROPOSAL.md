# Proposta: Sistema de Workspaces Completo

## Análise dos Concorrentes

### YNAB (You Need A Budget)
- **Orçamentos separados**: Cada orçamento é um workspace isolado
- **Compartilhamento familiar**: Múltiplos usuários podem editar
- **Categorias por workspace**: Cada workspace tem suas próprias categorias
- **Relatórios isolados**: Estatísticas separadas por workspace

### Mint
- **Contas agrupadas**: Tags e categorias para organizar
- **Orçamentos múltiplos**: Diferentes orçamentos para diferentes contextos
- **Filtros avançados**: Por conta, categoria, período

### PocketGuard
- **Pockets**: "Bolsos" separados para diferentes propósitos
- **Compartilhamento**: Família pode ver e editar
- **Visão consolidada**: Dashboard mostra todos os pockets

## Funcionalidades Propostas

### 1. Dashboard do Workspace
- Resumo financeiro específico do workspace
- KPIs: Saldo total, Receitas, Despesas, Saldo disponível
- Gráficos de evolução
- Últimas transações do workspace
- Contas vinculadas ao workspace

### 2. Gestão de Workspaces
- Criar/Editar/Excluir workspaces
- Tipos: Pessoal, Familiar, Compartilhado
- Cores e ícones para identificação visual
- Ativar/Desativar workspaces

### 3. Gestão de Membros
- Adicionar/Remover membros
- Permissões: Visualizar, Editar, Deletar
- Lista de membros com permissões
- Histórico de atividades dos membros

### 4. Filtros e Contexto
- Seletor de workspace no header (persistente)
- Filtro automático em todas as páginas
- Transações, Contas, Metas, Investimentos filtrados por workspace
- Relatórios por workspace

### 5. Estatísticas e Análises
- Resumo financeiro por workspace
- Comparação entre workspaces
- Gráficos de distribuição
- Evolução temporal por workspace

### 6. Templates de Workspace
- Templates pré-configurados:
  - Pessoal
  - Casal
  - Família
  - Negócio
  - Viagem
- Categorias pré-configuradas por template

### 7. Exportação e Backup
- Exportar dados do workspace (CSV, PDF)
- Backup completo do workspace
- Restaurar workspace

### 8. Integração com Outras Funcionalidades
- Metas vinculadas ao workspace
- Investimentos por workspace
- Planejamento por workspace
- Calendário filtrado por workspace

## Estrutura de Dados

### Workspace
- Nome, Descrição
- Tipo (Personal, Family, Shared)
- Cor, Ícone
- Dono
- Status (Ativo/Inativo)

### WorkspaceMember
- Usuário
- Permissões (can_edit, can_delete)
- Data de entrada

### Relacionamentos
- Accounts → workspace_id
- Transactions → workspace_id
- Transfers → workspace_id
- Goals → workspace_id (futuro)
- Investments → workspace_id (futuro)
- Planning → workspace_id (futuro)

## Interface do Usuário

### Header
- Seletor de workspace (dropdown)
- Indicador visual (cor/ícone)
- Botão "Criar Workspace"

### Página de Workspaces
- Lista de workspaces com cards
- Filtros por tipo
- Estatísticas rápidas
- Ações: Editar, Compartilhar, Excluir

### Dashboard do Workspace
- KPIs principais
- Gráficos de evolução
- Últimas transações
- Contas vinculadas
- Membros do workspace

### Gestão de Membros
- Lista de membros
- Adicionar por email
- Gerenciar permissões
- Remover membros

## Implementação

### Fase 1: MVP
- CRUD de workspaces
- Dashboard básico
- Seletor de workspace
- Filtros básicos

### Fase 2: Compartilhamento
- Gestão de membros
- Permissões
- Notificações

### Fase 3: Avançado
- Templates
- Comparação entre workspaces
- Exportação
- Estatísticas avançadas

