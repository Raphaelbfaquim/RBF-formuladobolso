'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useWorkspace } from '@/components/providers/workspace-provider'
import apiClient from '@/lib/api/client'
import toast from 'react-hot-toast'
import {
  BarChart, Bar, LineChart, Line, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts'

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#06b6d4', '#84cc16']

const WORKSPACE_TYPE_LABELS: Record<string, string> = {
  personal: 'Pessoal',
  family: 'Familiar',
  shared: 'Compartilhado'
}

const WORKSPACE_TYPE_COLORS: Record<string, string> = {
  personal: 'from-blue-500 to-blue-600',
  family: 'from-purple-500 to-purple-600',
  shared: 'from-green-500 to-green-600'
}

type TabType = 'list' | 'dashboard' | 'members'

export default function WorkspacesPage() {
  const router = useRouter()
  const { workspaces, loadWorkspaces, currentWorkspace } = useWorkspace()
  const [activeTab, setActiveTab] = useState<TabType>('list')
  const [selectedWorkspace, setSelectedWorkspace] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    setLoading(true)
    try {
      await loadWorkspaces()
      if (currentWorkspace) {
        setSelectedWorkspace(currentWorkspace)
        setActiveTab('dashboard')
      }
    } catch (error: any) {
      toast.error('Erro ao carregar workspaces')
    } finally {
      setLoading(false)
    }
  }

  const handleSelectWorkspace = async (workspace: any) => {
    setSelectedWorkspace(workspace)
    setActiveTab('dashboard')
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-background p-6">
        <div className="max-w-7xl mx-auto">
          <div className="glass rounded-xl p-12 text-center">Carregando...</div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-3xl font-bold mb-2">💼 Workspaces</h1>
          <p className="text-muted-foreground">Gerencie seus contextos financeiros</p>
        </div>

        {/* Tabs */}
        <div className="flex gap-2 mb-6 overflow-x-auto">
          <button
            onClick={() => setActiveTab('list')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors whitespace-nowrap ${
              activeTab === 'list'
                ? 'bg-indigo-600 text-white'
                : 'bg-background hover:bg-muted'
            }`}
          >
            📋 Lista
          </button>
          {selectedWorkspace && (
            <>
              <button
                onClick={() => setActiveTab('dashboard')}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors whitespace-nowrap ${
                  activeTab === 'dashboard'
                    ? 'bg-indigo-600 text-white'
                    : 'bg-background hover:bg-muted'
                }`}
              >
                📊 Dashboard
              </button>
              <button
                onClick={() => setActiveTab('members')}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors whitespace-nowrap ${
                  activeTab === 'members'
                    ? 'bg-indigo-600 text-white'
                    : 'bg-background hover:bg-muted'
                }`}
              >
                👥 Membros
              </button>
            </>
          )}
          <button
            onClick={() => router.push('/workspaces/new')}
            className="ml-auto px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 font-medium whitespace-nowrap"
          >
            + Novo Workspace
          </button>
        </div>

        {/* Content */}
        {activeTab === 'list' && (
          <WorkspacesList
            workspaces={workspaces}
            onSelect={handleSelectWorkspace}
            onDelete={loadData}
          />
        )}
        {activeTab === 'dashboard' && selectedWorkspace && (
          <WorkspaceDashboard workspace={selectedWorkspace} />
        )}
        {activeTab === 'members' && selectedWorkspace && (
          <WorkspaceMembers workspace={selectedWorkspace} />
        )}
      </div>
    </div>
  )
}

// ========== Workspaces List ==========
function WorkspacesList({ workspaces, onSelect, onDelete }: any) {
  const router = useRouter()
  const { currentWorkspace, setCurrentWorkspace } = useWorkspace()

  const handleDelete = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation()
    if (!confirm('Tem certeza que deseja excluir este workspace?')) return

    try {
      await apiClient.delete(`/workspaces/${id}`)
      toast.success('Workspace excluído!')
      if (currentWorkspace?.id === id) {
        setCurrentWorkspace(null)
      }
      onDelete()
    } catch (error: any) {
      toast.error('Erro ao excluir workspace')
    }
  }

  if (workspaces.length === 0) {
    return (
      <div className="glass rounded-xl p-12 text-center">
        <p className="text-muted-foreground mb-4">Nenhum workspace cadastrado</p>
        <button
          onClick={() => router.push('/workspaces/new')}
          className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
        >
          Criar Primeiro Workspace
        </button>
      </div>
    )
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {workspaces.map((workspace: any) => (
        <div
          key={workspace.id}
          onClick={() => onSelect(workspace)}
          className="glass rounded-xl p-6 cursor-pointer hover:bg-background/50 transition-colors"
        >
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <div
                className="w-12 h-12 rounded-lg flex items-center justify-center text-2xl"
                style={{
                  backgroundColor: workspace.color ? `${workspace.color}20` : '#3b82f620',
                  color: workspace.color || '#3b82f6'
                }}
              >
                {workspace.icon || '💼'}
              </div>
              <div>
                <h3 className="font-semibold">{workspace.name}</h3>
                <p className="text-xs text-muted-foreground">
                  {WORKSPACE_TYPE_LABELS[workspace.workspace_type] || workspace.workspace_type}
                </p>
              </div>
            </div>
            {!workspace.is_active && (
              <span className="text-xs px-2 py-1 bg-gray-500/20 text-gray-400 rounded">Inativo</span>
            )}
          </div>
          {workspace.description && (
            <p className="text-sm text-muted-foreground mb-4 line-clamp-2">
              {workspace.description}
            </p>
          )}
          <div className="flex gap-2">
            <button
              onClick={(e) => {
                e.stopPropagation()
                router.push(`/workspaces/${workspace.id}/edit`)
              }}
              className="flex-1 px-3 py-2 bg-background hover:bg-muted rounded-lg text-sm"
            >
              Editar
            </button>
            <button
              onClick={(e) => handleDelete(workspace.id, e)}
              className="flex-1 px-3 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg text-sm"
            >
              Excluir
            </button>
          </div>
        </div>
      ))}
    </div>
  )
}

// ========== Workspace Dashboard ==========
function WorkspaceDashboard({ workspace }: any) {
  const [loading, setLoading] = useState(true)
  const [stats, setStats] = useState<any>(null)

  useEffect(() => {
    loadStats()
  }, [workspace.id])

  const loadStats = async () => {
    setLoading(true)
    try {
      const response = await apiClient.get(`/workspaces/${workspace.id}/stats`)
      setStats(response.data)
    } catch (error: any) {
      toast.error('Erro ao carregar estatísticas')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="glass rounded-xl p-12 text-center">Carregando...</div>
  }

  if (!stats) {
    return <div className="glass rounded-xl p-12 text-center">Nenhum dado disponível</div>
  }

  return (
    <div className="space-y-6">
      {/* Header do Workspace */}
      <div className="glass rounded-xl p-6">
        <div className="flex items-center gap-4 mb-4">
          <div
            className="w-16 h-16 rounded-lg flex items-center justify-center text-3xl"
            style={{
              backgroundColor: workspace.color ? `${workspace.color}20` : '#3b82f620',
              color: workspace.color || '#3b82f6'
            }}
          >
            {workspace.icon || '💼'}
          </div>
          <div>
            <h2 className="text-2xl font-bold">{workspace.name}</h2>
            <p className="text-muted-foreground">{workspace.description || 'Sem descrição'}</p>
          </div>
        </div>
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="glass rounded-xl p-4">
          <p className="text-sm text-muted-foreground mb-1">Saldo Total</p>
          <p className="text-2xl font-bold">
            {new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(stats.total_balance)}
          </p>
        </div>
        <div className="glass rounded-xl p-4">
          <p className="text-sm text-muted-foreground mb-1">Receitas do Mês</p>
          <p className="text-2xl font-bold text-green-400">
            {new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(stats.monthly_income)}
          </p>
        </div>
        <div className="glass rounded-xl p-4">
          <p className="text-sm text-muted-foreground mb-1">Despesas do Mês</p>
          <p className="text-2xl font-bold text-red-400">
            {new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(stats.monthly_expenses)}
          </p>
        </div>
        <div className="glass rounded-xl p-4">
          <p className="text-sm text-muted-foreground mb-1">Economia do Mês</p>
          <p className={`text-2xl font-bold ${stats.monthly_savings >= 0 ? 'text-green-400' : 'text-red-400'}`}>
            {new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(stats.monthly_savings)}
          </p>
        </div>
      </div>

      {/* Últimas Transações */}
      {stats.recent_transactions && stats.recent_transactions.length > 0 && (
        <div className="glass rounded-xl p-6">
          <h3 className="text-lg font-bold mb-4">Últimas Transações</h3>
          <div className="space-y-2">
            {stats.recent_transactions.map((transaction: any) => (
              <div
                key={transaction.id}
                className="flex items-center justify-between p-3 bg-background/50 rounded-lg"
              >
                <div className="flex-1">
                  <p className="font-medium">{transaction.description}</p>
                  <p className="text-xs text-muted-foreground">
                    {transaction.category || 'Sem categoria'} • {transaction.account || 'Sem conta'} •{' '}
                    {new Date(transaction.transaction_date).toLocaleDateString('pt-BR')}
                  </p>
                </div>
                <p
                  className={`font-bold ${
                    transaction.transaction_type === 'income' ? 'text-green-400' : 'text-red-400'
                  }`}
                >
                  {transaction.transaction_type === 'income' ? '+' : '-'}
                  {new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(
                    transaction.amount
                  )}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

// ========== Workspace Members ==========
function WorkspaceMembers({ workspace }: any) {
  const [members, setMembers] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadMembers()
  }, [workspace.id])

  const loadMembers = async () => {
    setLoading(true)
    try {
      // TODO: Implementar endpoint de membros
      // const response = await apiClient.get(`/workspaces/${workspace.id}/members`)
      // setMembers(response.data)
      setMembers([])
    } catch (error: any) {
      toast.error('Erro ao carregar membros')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="glass rounded-xl p-12 text-center">Carregando...</div>
  }

  return (
    <div className="glass rounded-xl p-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-bold">Membros do Workspace</h3>
        <button className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 text-sm">
          + Adicionar Membro
        </button>
      </div>
      {members.length === 0 ? (
        <div className="text-center py-8 text-muted-foreground">
          <p>Nenhum membro adicionado ainda</p>
        </div>
      ) : (
        <div className="space-y-2">
          {members.map((member) => (
            <div key={member.id} className="flex items-center justify-between p-3 bg-background/50 rounded-lg">
              <div>
                <p className="font-medium">{member.user?.name || 'Usuário'}</p>
                <p className="text-xs text-muted-foreground">
                  {member.can_edit ? 'Pode editar' : 'Somente visualização'}
                </p>
              </div>
              <button className="px-3 py-1 bg-red-600 hover:bg-red-700 text-white rounded text-sm">
                Remover
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
