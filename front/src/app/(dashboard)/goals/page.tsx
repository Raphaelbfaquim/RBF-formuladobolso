'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import apiClient from '@/lib/api/client'
import toast from 'react-hot-toast'

interface Goal {
  id: string
  name: string
  description: string | null
  goal_type: string
  target_amount: number
  current_amount: number
  status: string
  target_date: string | null
  icon: string | null
  color: string | null
  percentage: number
  remaining_amount: number
  days_remaining: number | null
  estimated_completion_date: string | null
  created_at: string
  updated_at: string
}

const GOAL_TYPE_LABELS: Record<string, string> = {
  house: '🏠 Casa',
  car: '🚗 Carro',
  trip: '✈️ Viagem',
  wedding: '💍 Casamento',
  education: '📚 Educação',
  emergency: '🚨 Emergência',
  retirement: '👴 Aposentadoria',
  other: '🎯 Outros'
}

const GOAL_TYPE_COLORS: Record<string, string> = {
  house: 'from-blue-500 to-blue-600',
  car: 'from-purple-500 to-purple-600',
  trip: 'from-cyan-500 to-cyan-600',
  wedding: 'from-pink-500 to-pink-600',
  education: 'from-green-500 to-green-600',
  emergency: 'from-red-500 to-red-600',
  retirement: 'from-orange-500 to-orange-600',
  other: 'from-indigo-500 to-indigo-600'
}

const STATUS_LABELS: Record<string, string> = {
  active: 'Ativa',
  paused: 'Pausada',
  completed: 'Concluída',
  cancelled: 'Cancelada'
}

export default function GoalsPage() {
  const router = useRouter()
  const [loading, setLoading] = useState(true)
  const [goals, setGoals] = useState<Goal[]>([])
  const [filteredGoals, setFilteredGoals] = useState<Goal[]>([])
  const [searchText, setSearchText] = useState('')
  const [filterStatus, setFilterStatus] = useState<string>('all')
  const [filterType, setFilterType] = useState<string>('all')
  const [sortBy, setSortBy] = useState<string>('progress') // progress, date, value, name

  useEffect(() => {
    loadGoals()
  }, [])

  useEffect(() => {
    applyFilters()
  }, [goals, searchText, filterStatus, filterType, sortBy])

  const loadGoals = async () => {
    setLoading(true)
    try {
      const response = await apiClient.get('/goals/')
      setGoals(response.data)
    } catch (error: any) {
      if (error.response?.status === 401) {
        router.push('/login')
      } else {
        toast.error('Erro ao carregar metas')
      }
    } finally {
      setLoading(false)
    }
  }

  const applyFilters = () => {
    let filtered = [...goals]

    // Busca por texto
    if (searchText.trim()) {
      const searchLower = searchText.toLowerCase()
      filtered = filtered.filter(goal =>
        goal.name.toLowerCase().includes(searchLower) ||
        goal.description?.toLowerCase().includes(searchLower)
      )
    }

    // Filtro por status
    if (filterStatus !== 'all') {
      filtered = filtered.filter(goal => goal.status === filterStatus)
    }

    // Filtro por tipo
    if (filterType !== 'all') {
      filtered = filtered.filter(goal => goal.goal_type === filterType)
    }

    // Ordenação
    filtered.sort((a, b) => {
      switch (sortBy) {
        case 'progress':
          return b.percentage - a.percentage
        case 'date':
          if (!a.target_date && !b.target_date) return 0
          if (!a.target_date) return 1
          if (!b.target_date) return -1
          return new Date(a.target_date).getTime() - new Date(b.target_date).getTime()
        case 'value':
          return b.target_amount - a.target_amount
        case 'name':
          return a.name.localeCompare(b.name)
        default:
          return 0
      }
    })

    setFilteredGoals(filtered)
  }

  const handleDelete = async (goalId: string, goalName: string) => {
    if (!confirm(`Tem certeza que deseja excluir a meta "${goalName}"?`)) {
      return
    }

    try {
      await apiClient.delete(`/goals/${goalId}`)
      toast.success('Meta excluída com sucesso!')
      loadGoals()
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Erro ao excluir meta')
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-green-500/20 text-green-400 border-green-500/30'
      case 'paused':
        return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30'
      case 'completed':
        return 'bg-blue-500/20 text-blue-400 border-blue-500/30'
      case 'cancelled':
        return 'bg-red-500/20 text-red-400 border-red-500/30'
      default:
        return 'bg-gray-500/20 text-gray-400 border-gray-500/30'
    }
  }

  const getProgressColor = (percentage: number) => {
    if (percentage >= 100) return 'bg-green-500'
    if (percentage >= 75) return 'bg-blue-500'
    if (percentage >= 50) return 'bg-indigo-500'
    if (percentage >= 25) return 'bg-yellow-500'
    return 'bg-orange-500'
  }

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold mb-2">Metas e Sonhos</h1>
            <p className="text-muted-foreground">Acompanhe seus objetivos financeiros</p>
          </div>
          <button
            onClick={() => router.push('/goals/new')}
            className="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 font-medium transition-colors flex items-center gap-2"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            Nova Meta
          </button>
        </div>

        {/* Filtros e Busca */}
        <div className="mb-6 glass rounded-xl p-4">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {/* Busca */}
            <div className="md:col-span-2">
              <input
                type="text"
                placeholder="Buscar por nome ou descrição..."
                value={searchText}
                onChange={(e) => setSearchText(e.target.value)}
                className="w-full px-4 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>

            {/* Filtro Status */}
            <div>
              <select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
                className="w-full px-4 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                <option value="all">Todos os Status</option>
                <option value="active">Ativa</option>
                <option value="paused">Pausada</option>
                <option value="completed">Concluída</option>
                <option value="cancelled">Cancelada</option>
              </select>
            </div>

            {/* Filtro Tipo */}
            <div>
              <select
                value={filterType}
                onChange={(e) => setFilterType(e.target.value)}
                className="w-full px-4 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                <option value="all">Todos os Tipos</option>
                <option value="house">🏠 Casa</option>
                <option value="car">🚗 Carro</option>
                <option value="trip">✈️ Viagem</option>
                <option value="wedding">💍 Casamento</option>
                <option value="education">📚 Educação</option>
                <option value="emergency">🚨 Emergência</option>
                <option value="retirement">👴 Aposentadoria</option>
                <option value="other">🎯 Outros</option>
              </select>
            </div>
          </div>

          {/* Ordenação */}
          <div className="mt-4 flex items-center gap-2">
            <span className="text-sm text-muted-foreground">Ordenar por:</span>
            <div className="flex gap-2">
              <button
                onClick={() => setSortBy('progress')}
                className={`px-3 py-1 text-sm rounded-lg transition-colors ${
                  sortBy === 'progress'
                    ? 'bg-indigo-600 text-white'
                    : 'bg-background border border-border hover:bg-muted'
                }`}
              >
                Progresso
              </button>
              <button
                onClick={() => setSortBy('date')}
                className={`px-3 py-1 text-sm rounded-lg transition-colors ${
                  sortBy === 'date'
                    ? 'bg-indigo-600 text-white'
                    : 'bg-background border border-border hover:bg-muted'
                }`}
              >
                Data
              </button>
              <button
                onClick={() => setSortBy('value')}
                className={`px-3 py-1 text-sm rounded-lg transition-colors ${
                  sortBy === 'value'
                    ? 'bg-indigo-600 text-white'
                    : 'bg-background border border-border hover:bg-muted'
                }`}
              >
                Valor
              </button>
              <button
                onClick={() => setSortBy('name')}
                className={`px-3 py-1 text-sm rounded-lg transition-colors ${
                  sortBy === 'name'
                    ? 'bg-indigo-600 text-white'
                    : 'bg-background border border-border hover:bg-muted'
                }`}
              >
                Nome
              </button>
            </div>
          </div>
        </div>

        {/* Resumo */}
        {!loading && goals.length > 0 && (
          <div className="mb-6 grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="glass rounded-xl p-4">
              <p className="text-sm text-muted-foreground mb-1">Total de Metas</p>
              <p className="text-2xl font-bold">{goals.length}</p>
            </div>
            <div className="glass rounded-xl p-4">
              <p className="text-sm text-muted-foreground mb-1">Total Economizado</p>
              <p className="text-2xl font-bold text-green-400">
                {new Intl.NumberFormat('pt-BR', {
                  style: 'currency',
                  currency: 'BRL'
                }).format(goals.reduce((sum, goal) => sum + goal.current_amount, 0))}
              </p>
            </div>
            <div className="glass rounded-xl p-4">
              <p className="text-sm text-muted-foreground mb-1">Total em Metas</p>
              <p className="text-2xl font-bold">
                {new Intl.NumberFormat('pt-BR', {
                  style: 'currency',
                  currency: 'BRL'
                }).format(goals.reduce((sum, goal) => sum + goal.target_amount, 0))}
              </p>
            </div>
            <div className="glass rounded-xl p-4">
              <p className="text-sm text-muted-foreground mb-1">Metas Concluídas</p>
              <p className="text-2xl font-bold text-blue-400">
                {goals.filter(g => g.status === 'completed').length}
              </p>
            </div>
          </div>
        )}

        {/* Lista de Metas */}
        {loading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-500 mx-auto"></div>
            <p className="mt-4 text-muted-foreground">Carregando metas...</p>
          </div>
        ) : filteredGoals.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredGoals.map((goal) => (
              <div
                key={goal.id}
                className="glass rounded-xl overflow-hidden hover:shadow-lg transition-all cursor-pointer group"
                onClick={() => router.push(`/goals/${goal.id}`)}
              >
                {/* Header com gradiente */}
                <div className={`bg-gradient-to-r ${GOAL_TYPE_COLORS[goal.goal_type] || GOAL_TYPE_COLORS.other} p-6 text-white`}>
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <span className="text-3xl">{goal.icon || '🎯'}</span>
                      <div>
                        <h3 className="text-xl font-bold">{goal.name}</h3>
                        <p className="text-sm text-white/80">{GOAL_TYPE_LABELS[goal.goal_type] || 'Outros'}</p>
                      </div>
                    </div>
                    <span className={`px-2 py-1 text-xs rounded-full border font-medium ${getStatusColor(goal.status)}`}>
                      {STATUS_LABELS[goal.status] || goal.status}
                    </span>
                  </div>
                </div>

                {/* Conteúdo */}
                <div className="p-6">
                  {goal.description && (
                    <p className="text-sm text-muted-foreground mb-4 line-clamp-2">{goal.description}</p>
                  )}

                  {/* Progresso */}
                  <div className="mb-4">
                    <div className="flex items-center justify-between text-sm mb-2">
                      <span className="text-muted-foreground">Progresso</span>
                      <span className="font-bold text-lg">{goal.percentage.toFixed(1)}%</span>
                    </div>
                    <div className="w-full bg-background rounded-full h-3 overflow-hidden">
                      <div
                        className={`h-3 rounded-full transition-all ${getProgressColor(goal.percentage)}`}
                        style={{ width: `${Math.min(goal.percentage, 100)}%` }}
                      ></div>
                    </div>
                  </div>

                  {/* Valores */}
                  <div className="mb-4 space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-muted-foreground">Atual</span>
                      <span className="font-semibold text-green-400">
                        {new Intl.NumberFormat('pt-BR', {
                          style: 'currency',
                          currency: 'BRL'
                        }).format(goal.current_amount)}
                      </span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-muted-foreground">Meta</span>
                      <span className="font-semibold">
                        {new Intl.NumberFormat('pt-BR', {
                          style: 'currency',
                          currency: 'BRL'
                        }).format(goal.target_amount)}
                      </span>
                    </div>
                    <div className="flex items-center justify-between pt-2 border-t border-border">
                      <span className="text-sm text-muted-foreground">Falta</span>
                      <span className="font-bold text-yellow-400">
                        {new Intl.NumberFormat('pt-BR', {
                          style: 'currency',
                          currency: 'BRL'
                        }).format(goal.remaining_amount)}
                      </span>
                    </div>
                  </div>

                  {/* Informações adicionais */}
                  {goal.target_date && (
                    <div className="mb-4 p-3 bg-background/50 rounded-lg">
                      <div className="flex items-center gap-2 text-sm">
                        <svg className="w-4 h-4 text-muted-foreground" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                        </svg>
                        <span className="text-muted-foreground">Prazo:</span>
                        <span className="font-medium">
                          {new Date(goal.target_date).toLocaleDateString('pt-BR')}
                        </span>
                        {goal.days_remaining !== null && (
                          <span className="text-xs text-muted-foreground ml-auto">
                            {goal.days_remaining > 0 ? `${goal.days_remaining} dias` : 'Atrasada'}
                          </span>
                        )}
                      </div>
                    </div>
                  )}

                  {/* Ações */}
                  <div className="flex items-center gap-2 pt-4 border-t border-border">
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        router.push(`/goals/${goal.id}/edit`)
                      }}
                      className="flex-1 px-3 py-2 text-indigo-400 hover:text-indigo-300 hover:bg-indigo-500/10 rounded-lg transition-colors text-sm font-medium"
                    >
                      Editar
                    </button>
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        router.push(`/goals/${goal.id}`)
                      }}
                      className="flex-1 px-3 py-2 text-blue-400 hover:text-blue-300 hover:bg-blue-500/10 rounded-lg transition-colors text-sm font-medium"
                    >
                      Ver Detalhes
                    </button>
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        handleDelete(goal.id, goal.name)
                      }}
                      className="px-3 py-2 text-red-400 hover:text-red-300 hover:bg-red-500/10 rounded-lg transition-colors"
                      title="Excluir meta"
                    >
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="col-span-full text-center py-12 glass rounded-xl">
            <div className="text-6xl mb-4">🎯</div>
            <p className="text-xl font-semibold mb-2">
              {searchText || filterStatus !== 'all' || filterType !== 'all'
                ? 'Nenhuma meta encontrada'
                : 'Nenhuma meta criada ainda'}
            </p>
            <p className="text-muted-foreground mb-6">
              {searchText || filterStatus !== 'all' || filterType !== 'all'
                ? 'Tente ajustar os filtros de busca'
                : 'Comece criando sua primeira meta financeira'}
            </p>
            {(!searchText && filterStatus === 'all' && filterType === 'all') && (
              <button
                onClick={() => router.push('/goals/new')}
                className="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 font-medium transition-colors"
              >
                Criar Primeira Meta
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
