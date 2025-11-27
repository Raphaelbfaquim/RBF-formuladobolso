'use client'

import { useEffect, useState } from 'react'
import { useRouter, useParams } from 'next/navigation'
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

interface Contribution {
  id: string
  amount: number
  contribution_date: string
  notes: string | null
  created_at: string
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

export default function GoalDetailPage() {
  const router = useRouter()
  const params = useParams()
  const goalId = params.id as string

  const [loading, setLoading] = useState(true)
  const [goal, setGoal] = useState<Goal | null>(null)
  const [contributions, setContributions] = useState<Contribution[]>([])
  const [showAddContribution, setShowAddContribution] = useState(false)
  const [contributionAmount, setContributionAmount] = useState('')
  const [contributionNotes, setContributionNotes] = useState('')

  useEffect(() => {
    if (goalId) {
      loadGoal()
      loadContributions()
    }
  }, [goalId])

  const loadGoal = async () => {
    try {
      const response = await apiClient.get(`/goals/${goalId}`)
      setGoal(response.data)
    } catch (error: any) {
      if (error.response?.status === 401) {
        router.push('/login')
      } else if (error.response?.status === 404) {
        toast.error('Meta não encontrada')
        router.push('/goals')
      } else {
        toast.error('Erro ao carregar meta')
      }
    } finally {
      setLoading(false)
    }
  }

  const loadContributions = async () => {
    try {
      const response = await apiClient.get(`/goals/${goalId}/contributions`)
      setContributions(response.data.sort((a: Contribution, b: Contribution) => 
        new Date(b.contribution_date).getTime() - new Date(a.contribution_date).getTime()
      ))
    } catch (error: any) {
      console.error('Erro ao carregar contribuições:', error)
    }
  }

  const handleAddContribution = async () => {
    if (!contributionAmount || parseFloat(contributionAmount) <= 0) {
      toast.error('Digite um valor válido')
      return
    }

    try {
      await apiClient.post(`/goals/${goalId}/contributions`, {
        amount: parseFloat(contributionAmount),
        contribution_date: new Date().toISOString(),
        notes: contributionNotes || null
      })
      toast.success('Contribuição adicionada!')
      setContributionAmount('')
      setContributionNotes('')
      setShowAddContribution(false)
      loadGoal()
      loadContributions()
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Erro ao adicionar contribuição')
    }
  }

  const handleDelete = async () => {
    if (!confirm(`Tem certeza que deseja excluir a meta "${goal?.name}"?`)) {
      return
    }

    try {
      await apiClient.delete(`/goals/${goalId}`)
      toast.success('Meta excluída com sucesso!')
      router.push('/goals')
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Erro ao excluir meta')
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-500 mx-auto"></div>
          <p className="mt-4 text-muted-foreground">Carregando meta...</p>
        </div>
      </div>
    )
  }

  if (!goal) {
    return (
      <div className="min-h-screen bg-background p-6">
        <div className="max-w-4xl mx-auto">
          <p className="text-muted-foreground">Meta não encontrada</p>
        </div>
      </div>
    )
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
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <button
            onClick={() => router.back()}
            className="mb-4 text-muted-foreground hover:text-foreground flex items-center gap-2"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            Voltar
          </button>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <span className="text-5xl">{goal.icon || '🎯'}</span>
              <div>
                <h1 className="text-3xl font-bold mb-2">{goal.name}</h1>
                <p className="text-muted-foreground">{GOAL_TYPE_LABELS[goal.goal_type] || 'Outros'}</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={() => router.push(`/goals/${goalId}/edit`)}
                className="px-4 py-2 text-indigo-400 hover:text-indigo-300 hover:bg-indigo-500/10 rounded-lg transition-colors"
              >
                Editar
              </button>
              <button
                onClick={handleDelete}
                className="px-4 py-2 text-red-400 hover:text-red-300 hover:bg-red-500/10 rounded-lg transition-colors"
              >
                Excluir
              </button>
            </div>
          </div>
        </div>

        {/* Progresso Principal */}
        <div className="mb-6 glass rounded-xl p-6">
          <div className="mb-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-muted-foreground">Progresso</span>
              <span className="text-3xl font-bold">{goal.percentage.toFixed(1)}%</span>
            </div>
            <div className="w-full bg-background rounded-full h-4 overflow-hidden">
              <div
                className={`h-4 rounded-full transition-all ${getProgressColor(goal.percentage)}`}
                style={{ width: `${Math.min(goal.percentage, 100)}%` }}
              ></div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <p className="text-sm text-muted-foreground mb-1">Atual</p>
              <p className="text-2xl font-bold text-green-400">
                {new Intl.NumberFormat('pt-BR', {
                  style: 'currency',
                  currency: 'BRL'
                }).format(goal.current_amount)}
              </p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground mb-1">Meta</p>
              <p className="text-2xl font-bold">
                {new Intl.NumberFormat('pt-BR', {
                  style: 'currency',
                  currency: 'BRL'
                }).format(goal.target_amount)}
              </p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground mb-1">Falta</p>
              <p className="text-2xl font-bold text-yellow-400">
                {new Intl.NumberFormat('pt-BR', {
                  style: 'currency',
                  currency: 'BRL'
                }).format(goal.remaining_amount)}
              </p>
            </div>
          </div>
        </div>

        {/* Informações */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          <div className="glass rounded-xl p-6">
            <h2 className="text-lg font-semibold mb-4">Informações</h2>
            <div className="space-y-3">
              {goal.description && (
                <div>
                  <p className="text-sm text-muted-foreground mb-1">Descrição</p>
                  <p>{goal.description}</p>
                </div>
              )}
              {goal.target_date && (
                <div>
                  <p className="text-sm text-muted-foreground mb-1">Data Objetivo</p>
                  <p className="font-medium">
                    {new Date(goal.target_date).toLocaleDateString('pt-BR', {
                      day: '2-digit',
                      month: '2-digit',
                      year: 'numeric'
                    })}
                  </p>
                  {goal.days_remaining !== null && (
                    <p className="text-xs text-muted-foreground mt-1">
                      {goal.days_remaining > 0 ? `${goal.days_remaining} dias restantes` : 'Prazo vencido'}
                    </p>
                  )}
                </div>
              )}
              <div>
                <p className="text-sm text-muted-foreground mb-1">Status</p>
                <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                  goal.status === 'active' ? 'bg-green-500/20 text-green-400' :
                  goal.status === 'completed' ? 'bg-blue-500/20 text-blue-400' :
                  goal.status === 'paused' ? 'bg-yellow-500/20 text-yellow-400' :
                  'bg-red-500/20 text-red-400'
                }`}>
                  {goal.status === 'active' ? 'Ativa' :
                   goal.status === 'completed' ? 'Concluída' :
                   goal.status === 'paused' ? 'Pausada' :
                   'Cancelada'}
                </span>
              </div>
            </div>
          </div>

          <div className="glass rounded-xl p-6">
            <h2 className="text-lg font-semibold mb-4">Estatísticas</h2>
            <div className="space-y-3">
              {goal.estimated_completion_date && (
                <div>
                  <p className="text-sm text-muted-foreground mb-1">Data Estimada de Conclusão</p>
                  <p className="font-medium">
                    {new Date(goal.estimated_completion_date).toLocaleDateString('pt-BR', {
                      day: '2-digit',
                      month: '2-digit',
                      year: 'numeric'
                    })}
                  </p>
                </div>
              )}
              <div>
                <p className="text-sm text-muted-foreground mb-1">Criada em</p>
                <p className="font-medium">
                  {new Date(goal.created_at).toLocaleDateString('pt-BR', {
                    day: '2-digit',
                    month: '2-digit',
                    year: 'numeric'
                  })}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Contribuições */}
        <div className="glass rounded-xl p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold">Contribuições</h2>
            <button
              onClick={() => setShowAddContribution(!showAddContribution)}
              className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 text-sm font-medium"
            >
              {showAddContribution ? 'Cancelar' : '+ Adicionar Contribuição'}
            </button>
          </div>

          {showAddContribution && (
            <div className="mb-6 p-4 bg-background/50 rounded-lg border border-border">
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Valor</label>
                  <input
                    type="number"
                    value={contributionAmount}
                    onChange={(e) => setContributionAmount(e.target.value)}
                    placeholder="0.00"
                    step="0.01"
                    min="0.01"
                    className="w-full px-4 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">Observações (opcional)</label>
                  <textarea
                    value={contributionNotes}
                    onChange={(e) => setContributionNotes(e.target.value)}
                    placeholder="Adicione uma observação..."
                    rows={2}
                    className="w-full px-4 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  />
                </div>
                <button
                  onClick={handleAddContribution}
                  className="w-full px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 font-medium"
                >
                  Adicionar
                </button>
              </div>
            </div>
          )}

          {contributions.length > 0 ? (
            <div className="space-y-3">
              {contributions.map((contribution) => (
                <div key={contribution.id} className="p-4 bg-background/50 rounded-lg border border-border">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-semibold text-green-400">
                        {new Intl.NumberFormat('pt-BR', {
                          style: 'currency',
                          currency: 'BRL'
                        }).format(contribution.amount)}
                      </p>
                      <p className="text-sm text-muted-foreground">
                        {new Date(contribution.contribution_date).toLocaleDateString('pt-BR')}
                      </p>
                      {contribution.notes && (
                        <p className="text-sm mt-1">{contribution.notes}</p>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-muted-foreground">
              <p>Nenhuma contribuição registrada ainda</p>
              <p className="text-sm mt-2">Adicione sua primeira contribuição para começar!</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

