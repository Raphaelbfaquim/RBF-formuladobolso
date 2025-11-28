'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import apiClient from '@/lib/api/client'
import toast from 'react-hot-toast'

type TabType = 'dashboard' | 'users' | 'families' | 'security' | 'reports'

interface DashboardStats {
  total_users: number
  active_users: number
  inactive_users: number
  new_users_last_7_days: number
  new_users_last_30_days: number
  total_families: number
  total_transactions: number
  total_volume: number
  users_with_2fa: number
  unverified_users: number
}

interface User {
  id: string
  email: string
  username: string
  full_name?: string
  is_active: boolean
  is_verified: boolean
  role: string
  created_at: string
  families_count: number
  accounts_count: number
  transactions_count: number
  has_2fa: boolean
}

export default function AdminPage() {
  const router = useRouter()
  const [activeTab, setActiveTab] = useState<TabType>('dashboard')
  const [loading, setLoading] = useState(false)
  const [dashboardData, setDashboardData] = useState<any>(null)
  const [users, setUsers] = useState<User[]>([])
  const [selectedUser, setSelectedUser] = useState<User | null>(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [filters, setFilters] = useState({
    is_active: null as boolean | null,
    is_verified: null as boolean | null,
    role: null as string | null,
  })
  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  
  // Estados para Famílias
  const [families, setFamilies] = useState<any[]>([])
  const [familiesPage, setFamiliesPage] = useState(1)
  const [familiesTotalPages, setFamiliesTotalPages] = useState(1)
  const [familiesSearch, setFamiliesSearch] = useState('')
  
  // Estados para Segurança
  const [auditLogs, setAuditLogs] = useState<any[]>([])
  const [securityAlerts, setSecurityAlerts] = useState<any[]>([])
  const [logsPage, setLogsPage] = useState(1)
  const [alertsPage, setAlertsPage] = useState(1)
  
  // Estados para Relatórios
  const [reportsData, setReportsData] = useState<any>(null)
  const [reportsStartDate, setReportsStartDate] = useState(() => {
    const date = new Date()
    date.setDate(date.getDate() - 30)
    return date.toISOString().split('T')[0]
  })
  const [reportsEndDate, setReportsEndDate] = useState(() => {
    return new Date().toISOString().split('T')[0]
  })

  useEffect(() => {
    checkAdminAccess()
    if (activeTab === 'dashboard') {
      loadDashboard()
    } else if (activeTab === 'users') {
      loadUsers()
    } else if (activeTab === 'families') {
      loadFamilies()
    } else if (activeTab === 'security') {
      loadSecurityData()
    } else if (activeTab === 'reports') {
      loadReports()
    }
  }, [activeTab, page, searchTerm, filters, familiesPage, familiesSearch, logsPage, alertsPage])

  const checkAdminAccess = async () => {
    try {
      const response = await apiClient.get('/users/me')
      if (response.data.role !== 'admin' && response.data.role !== 'ADMIN') {
        toast.error('Acesso negado. Apenas administradores podem acessar esta área.')
        router.push('/dashboard')
      }
    } catch (error: any) {
      if (error.response?.status === 403) {
        toast.error('Acesso negado. Apenas administradores podem acessar esta área.')
        router.push('/dashboard')
      }
    }
  }

  const loadDashboard = async () => {
    setLoading(true)
    try {
      const response = await apiClient.get('/admin/dashboard')
      setDashboardData(response.data)
    } catch (error: any) {
      if (error.response?.status === 403) {
        toast.error('Acesso negado')
        router.push('/dashboard')
      } else {
        toast.error('Erro ao carregar dashboard')
      }
    } finally {
      setLoading(false)
    }
  }

  const loadUsers = async () => {
    setLoading(true)
    try {
      const params: any = {
        page,
        page_size: 20,
      }
      if (searchTerm) params.search = searchTerm
      if (filters.is_active !== null) params.is_active = filters.is_active
      if (filters.is_verified !== null) params.is_verified = filters.is_verified
      if (filters.role) params.role = filters.role

      const response = await apiClient.get('/admin/users', { params })
      setUsers(response.data.users)
      setTotalPages(response.data.total_pages)
    } catch (error: any) {
      if (error.response?.status === 403) {
        toast.error('Acesso negado')
        router.push('/dashboard')
      } else {
        toast.error('Erro ao carregar usuários')
      }
    } finally {
      setLoading(false)
    }
  }

  const handleActivateUser = async (userId: string) => {
    try {
      await apiClient.post(`/admin/users/${userId}/activate`)
      toast.success('Usuário ativado com sucesso!')
      loadUsers()
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Erro ao ativar usuário')
    }
  }

  const handleDeactivateUser = async (userId: string) => {
    if (!confirm('Tem certeza que deseja desativar este usuário?')) return

    try {
      await apiClient.post(`/admin/users/${userId}/deactivate`)
      toast.success('Usuário desativado com sucesso!')
      loadUsers()
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Erro ao desativar usuário')
    }
  }

  const handleMakeAdmin = async (userId: string) => {
    if (!confirm('Tem certeza que deseja tornar este usuário administrador?')) return

    try {
      await apiClient.post(`/admin/users/${userId}/make-admin`)
      toast.success('Usuário promovido a administrador!')
      loadUsers()
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Erro ao promover usuário')
    }
  }

  const handleRemoveAdmin = async (userId: string) => {
    if (!confirm('Tem certeza que deseja remover os privilégios de administrador?')) return

    try {
      await apiClient.post(`/admin/users/${userId}/remove-admin`)
      toast.success('Privilégios de admin removidos!')
      loadUsers()
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Erro ao remover privilégios')
    }
  }

  const loadFamilies = async () => {
    setLoading(true)
    try {
      const params: any = {
        page: familiesPage,
        page_size: 20,
      }
      if (familiesSearch) params.search = familiesSearch

      const response = await apiClient.get('/admin/families', { params })
      setFamilies(response.data.families)
      setFamiliesTotalPages(response.data.total_pages)
    } catch (error: any) {
      toast.error('Erro ao carregar famílias')
    } finally {
      setLoading(false)
    }
  }

  const loadSecurityData = async () => {
    setLoading(true)
    try {
      const [logsResponse, alertsResponse] = await Promise.all([
        apiClient.get('/admin/audit-logs', { params: { page: logsPage, page_size: 20 } }),
        apiClient.get('/admin/security-alerts', { params: { page: alertsPage, page_size: 20, is_read: false } }),
      ])
      setAuditLogs(logsResponse.data.logs)
      setSecurityAlerts(alertsResponse.data.alerts)
    } catch (error: any) {
      toast.error('Erro ao carregar dados de segurança')
    } finally {
      setLoading(false)
    }
  }

  const loadReports = async () => {
    setLoading(true)
    try {
      const params: any = {}
      if (reportsStartDate) params.start_date = reportsStartDate
      if (reportsEndDate) params.end_date = reportsEndDate

      const response = await apiClient.get('/admin/reports/summary', { params })
      setReportsData(response.data)
    } catch (error: any) {
      toast.error('Erro ao carregar relatórios')
    } finally {
      setLoading(false)
    }
  }

  const handleMarkAlertRead = async (alertId: string) => {
    try {
      // Endpoint para marcar alerta como lido (precisa ser criado)
      await apiClient.put(`/admin/security-alerts/${alertId}/read`)
      toast.success('Alerta marcado como lido')
      loadSecurityData()
    } catch (error: any) {
      toast.error('Erro ao marcar alerta como lido')
    }
  }

  const tabs = [
    { id: 'dashboard' as TabType, name: 'Dashboard', icon: '📊' },
    { id: 'users' as TabType, name: 'Usuários', icon: '👥' },
    { id: 'families' as TabType, name: 'Famílias', icon: '👨‍👩‍👧‍👦' },
    { id: 'security' as TabType, name: 'Segurança', icon: '🔒' },
    { id: 'reports' as TabType, name: 'Relatórios', icon: '📈' },
  ]

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">🛡️ Área do Administrador</h1>
          <p className="text-muted-foreground">Gerencie o sistema completo</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Sidebar de Tabs */}
          <div className="lg:col-span-1">
            <div className="bg-card rounded-lg border border-border p-4 space-y-2">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                    activeTab === tab.id
                      ? 'bg-indigo-500/20 text-indigo-400 border border-indigo-500/30'
                      : 'text-muted-foreground hover:bg-background hover:text-foreground'
                  }`}
                >
                  <span className="text-lg">{tab.icon}</span>
                  <span className="font-medium">{tab.name}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Conteúdo */}
          <div className="lg:col-span-3">
            <div className="bg-card rounded-lg border border-border p-6">
              {/* Tab: Dashboard */}
              {activeTab === 'dashboard' && (
                <div>
                  <h2 className="text-2xl font-bold mb-6">Dashboard Administrativo</h2>
                  {loading ? (
                    <div className="text-center py-12">
                      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-500 mx-auto"></div>
                    </div>
                  ) : dashboardData ? (
                    <div className="space-y-6">
                      {/* Estatísticas */}
                      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                        <div className="bg-background p-4 rounded-lg border border-border">
                          <div className="text-sm text-muted-foreground mb-1">Total de Usuários</div>
                          <div className="text-2xl font-bold">{dashboardData.stats.total_users}</div>
                          <div className="text-xs text-muted-foreground mt-1">
                            {dashboardData.stats.active_users} ativos
                          </div>
                        </div>

                        <div className="bg-background p-4 rounded-lg border border-border">
                          <div className="text-sm text-muted-foreground mb-1">Novos (7 dias)</div>
                          <div className="text-2xl font-bold">{dashboardData.stats.new_users_last_7_days}</div>
                          <div className="text-xs text-muted-foreground mt-1">
                            {dashboardData.stats.new_users_last_30_days} nos últimos 30 dias
                          </div>
                        </div>

                        <div className="bg-background p-4 rounded-lg border border-border">
                          <div className="text-sm text-muted-foreground mb-1">Famílias</div>
                          <div className="text-2xl font-bold">{dashboardData.stats.total_families}</div>
                        </div>

                        <div className="bg-background p-4 rounded-lg border border-border">
                          <div className="text-sm text-muted-foreground mb-1">Transações</div>
                          <div className="text-2xl font-bold">{dashboardData.stats.total_transactions.toLocaleString()}</div>
                          <div className="text-xs text-muted-foreground mt-1">
                            Volume: R$ {dashboardData.stats.total_volume.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                          </div>
                        </div>

                        <div className="bg-background p-4 rounded-lg border border-border">
                          <div className="text-sm text-muted-foreground mb-1">2FA Habilitado</div>
                          <div className="text-2xl font-bold">{dashboardData.stats.users_with_2fa}</div>
                        </div>

                        <div className="bg-background p-4 rounded-lg border border-border">
                          <div className="text-sm text-muted-foreground mb-1">Não Verificados</div>
                          <div className="text-2xl font-bold text-yellow-400">{dashboardData.stats.unverified_users}</div>
                        </div>

                        <div className="bg-background p-4 rounded-lg border border-border">
                          <div className="text-sm text-muted-foreground mb-1">Alertas de Segurança</div>
                          <div className="text-2xl font-bold text-red-400">{dashboardData.security_alerts_count}</div>
                        </div>
                      </div>

                      {/* Usuários Recentes */}
                      <div>
                        <h3 className="text-lg font-semibold mb-4">Usuários Recentes</h3>
                        <div className="space-y-2">
                          {dashboardData.recent_users.map((user: any) => (
                            <div
                              key={user.id}
                              className="flex items-center justify-between p-3 bg-background rounded-lg border border-border"
                            >
                              <div>
                                <div className="font-medium">{user.username}</div>
                                <div className="text-sm text-muted-foreground">{user.email}</div>
                              </div>
                              <div className="text-sm text-muted-foreground">
                                {new Date(user.created_at).toLocaleDateString('pt-BR')}
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  ) : null}
                </div>
              )}

              {/* Tab: Usuários */}
              {activeTab === 'users' && (
                <div>
                  <h2 className="text-2xl font-bold mb-6">Gerenciamento de Usuários</h2>

                  {/* Filtros e Busca */}
                  <div className="mb-6 space-y-4">
                    <div>
                      <input
                        type="text"
                        placeholder="Buscar por email, username ou nome..."
                        value={searchTerm}
                        onChange={(e) => {
                          setSearchTerm(e.target.value)
                          setPage(1)
                        }}
                        className="w-full px-4 py-3 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                      />
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <select
                        value={filters.is_active === null ? '' : filters.is_active.toString()}
                        onChange={(e) => {
                          setFilters({
                            ...filters,
                            is_active: e.target.value === '' ? null : e.target.value === 'true',
                          })
                          setPage(1)
                        }}
                        className="px-4 py-3 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                      >
                        <option value="">Todos os status</option>
                        <option value="true">Ativos</option>
                        <option value="false">Inativos</option>
                      </select>

                      <select
                        value={filters.role || ''}
                        onChange={(e) => {
                          setFilters({ ...filters, role: e.target.value || null })
                          setPage(1)
                        }}
                        className="px-4 py-3 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                      >
                        <option value="">Todos os roles</option>
                        <option value="admin">Admin</option>
                        <option value="user">Usuário</option>
                      </select>
                    </div>
                  </div>

                  {/* Tabela de Usuários */}
                  {loading ? (
                    <div className="text-center py-12">
                      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-500 mx-auto"></div>
                    </div>
                  ) : (
                    <div>
                      <div className="overflow-x-auto">
                        <table className="w-full">
                          <thead>
                            <tr className="border-b border-border">
                              <th className="text-left p-3">Email</th>
                              <th className="text-left p-3">Username</th>
                              <th className="text-left p-3">Status</th>
                              <th className="text-left p-3">Role</th>
                              <th className="text-left p-3">2FA</th>
                              <th className="text-left p-3">Ações</th>
                            </tr>
                          </thead>
                          <tbody>
                            {users.map((user) => (
                              <tr key={user.id} className="border-b border-border hover:bg-background">
                                <td className="p-3">{user.email}</td>
                                <td className="p-3">{user.username}</td>
                                <td className="p-3">
                                  <span
                                    className={`px-2 py-1 rounded text-xs ${
                                      user.is_active
                                        ? 'bg-green-500/20 text-green-400'
                                        : 'bg-red-500/20 text-red-400'
                                    }`}
                                  >
                                    {user.is_active ? 'Ativo' : 'Inativo'}
                                  </span>
                                </td>
                                <td className="p-3">
                                  <span
                                    className={`px-2 py-1 rounded text-xs ${
                                      (user.role === 'admin' || user.role === 'ADMIN')
                                        ? 'bg-purple-500/20 text-purple-400'
                                        : 'bg-gray-500/20 text-gray-400'
                                    }`}
                                  >
                                    {(user.role === 'admin' || user.role === 'ADMIN') ? 'Admin' : 'Usuário'}
                                  </span>
                                </td>
                                <td className="p-3">
                                  {user.has_2fa ? (
                                    <span className="text-green-400">✅</span>
                                  ) : (
                                    <span className="text-muted-foreground">❌</span>
                                  )}
                                </td>
                                <td className="p-3">
                                  <div className="flex gap-2">
                                    {!user.is_active ? (
                                      <button
                                        onClick={() => handleActivateUser(user.id)}
                                        className="px-3 py-1 bg-green-600 text-white rounded text-sm hover:bg-green-700"
                                      >
                                        Ativar
                                      </button>
                                    ) : (
                                      <button
                                        onClick={() => handleDeactivateUser(user.id)}
                                        className="px-3 py-1 bg-red-600 text-white rounded text-sm hover:bg-red-700"
                                      >
                                        Desativar
                                      </button>
                                    )}
                                    {(user.role !== 'admin' && user.role !== 'ADMIN') ? (
                                      <button
                                        onClick={() => handleMakeAdmin(user.id)}
                                        className="px-3 py-1 bg-purple-600 text-white rounded text-sm hover:bg-purple-700"
                                      >
                                        Tornar Admin
                                      </button>
                                    ) : (
                                      <button
                                        onClick={() => handleRemoveAdmin(user.id)}
                                        className="px-3 py-1 bg-orange-600 text-white rounded text-sm hover:bg-orange-700"
                                      >
                                        Remover Admin
                                      </button>
                                    )}
                                    <button
                                      onClick={() => setSelectedUser(user)}
                                      className="px-3 py-1 bg-indigo-600 text-white rounded text-sm hover:bg-indigo-700"
                                    >
                                      Ver
                                    </button>
                                  </div>
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>

                      {/* Paginação */}
                      {totalPages > 1 && (
                        <div className="mt-6 flex justify-center gap-2">
                          <button
                            onClick={() => setPage(p => Math.max(1, p - 1))}
                            disabled={page === 1}
                            className="px-4 py-2 bg-background border border-border rounded disabled:opacity-50"
                          >
                            Anterior
                          </button>
                          <span className="px-4 py-2">
                            Página {page} de {totalPages}
                          </span>
                          <button
                            onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                            disabled={page === totalPages}
                            className="px-4 py-2 bg-background border border-border rounded disabled:opacity-50"
                          >
                            Próxima
                          </button>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              )}

              {/* Tab: Famílias */}
              {activeTab === 'families' && (
                <div>
                  <h2 className="text-2xl font-bold mb-6">Gerenciamento de Famílias</h2>
                  
                  {/* Busca */}
                  <div className="mb-6">
                    <input
                      type="text"
                      placeholder="Buscar por nome ou descrição..."
                      value={familiesSearch}
                      onChange={(e) => {
                        setFamiliesSearch(e.target.value)
                        setFamiliesPage(1)
                      }}
                      className="w-full px-4 py-3 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    />
                  </div>

                  {loading ? (
                    <div className="text-center py-12">
                      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-500 mx-auto"></div>
                    </div>
                  ) : (
                    <div>
                      <div className="overflow-x-auto">
                        <table className="w-full">
                          <thead>
                            <tr className="border-b border-border">
                              <th className="text-left p-3">Nome</th>
                              <th className="text-left p-3">Criador</th>
                              <th className="text-left p-3">Membros</th>
                              <th className="text-left p-3">Contas</th>
                              <th className="text-left p-3">Criada em</th>
                            </tr>
                          </thead>
                          <tbody>
                            {families.map((family) => (
                              <tr key={family.id} className="border-b border-border hover:bg-background">
                                <td className="p-3">
                                  <div className="font-medium">{family.name}</div>
                                  {family.description && (
                                    <div className="text-sm text-muted-foreground">{family.description}</div>
                                  )}
                                </td>
                                <td className="p-3">
                                  <div>{family.creator_username || family.creator_email}</div>
                                </td>
                                <td className="p-3">{family.members_count}</td>
                                <td className="p-3">{family.accounts_count}</td>
                                <td className="p-3 text-sm text-muted-foreground">
                                  {new Date(family.created_at).toLocaleDateString('pt-BR')}
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>

                      {familiesTotalPages > 1 && (
                        <div className="mt-6 flex justify-center gap-2">
                          <button
                            onClick={() => setFamiliesPage(p => Math.max(1, p - 1))}
                            disabled={familiesPage === 1}
                            className="px-4 py-2 bg-background border border-border rounded disabled:opacity-50"
                          >
                            Anterior
                          </button>
                          <span className="px-4 py-2">
                            Página {familiesPage} de {familiesTotalPages}
                          </span>
                          <button
                            onClick={() => setFamiliesPage(p => Math.min(familiesTotalPages, p + 1))}
                            disabled={familiesPage === familiesTotalPages}
                            className="px-4 py-2 bg-background border border-border rounded disabled:opacity-50"
                          >
                            Próxima
                          </button>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              )}

              {/* Tab: Segurança */}
              {activeTab === 'security' && (
                <div className="space-y-8">
                  <h2 className="text-2xl font-bold mb-6">Segurança e Auditoria</h2>
                  
                  {/* Alertas de Segurança */}
                  <div>
                    <h3 className="text-xl font-semibold mb-4">🔔 Alertas de Segurança</h3>
                    {loading ? (
                      <div className="text-center py-8">
                        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-500 mx-auto"></div>
                      </div>
                    ) : (
                      <div className="space-y-3">
                        {securityAlerts.length === 0 ? (
                          <p className="text-muted-foreground text-center py-8">Nenhum alerta pendente</p>
                        ) : (
                          securityAlerts.map((alert) => (
                            <div
                              key={alert.id}
                              className={`p-4 rounded-lg border ${
                                alert.severity === 'high'
                                  ? 'bg-red-500/10 border-red-500/20'
                                  : alert.severity === 'medium'
                                  ? 'bg-yellow-500/10 border-yellow-500/20'
                                  : 'bg-blue-500/10 border-blue-500/20'
                              }`}
                            >
                              <div className="flex items-start justify-between">
                                <div className="flex-1">
                                  <div className="flex items-center gap-2 mb-2">
                                    <span className="font-medium">{alert.alert_type}</span>
                                    <span className={`px-2 py-1 rounded text-xs ${
                                      alert.severity === 'high'
                                        ? 'bg-red-500/20 text-red-400'
                                        : alert.severity === 'medium'
                                        ? 'bg-yellow-500/20 text-yellow-400'
                                        : 'bg-blue-500/20 text-blue-400'
                                    }`}>
                                      {alert.severity}
                                    </span>
                                  </div>
                                  <p className="text-sm text-muted-foreground mb-1">{alert.message}</p>
                                  <p className="text-xs text-muted-foreground">
                                    {new Date(alert.created_at).toLocaleString('pt-BR')}
                                  </p>
                                </div>
                                {!alert.is_read && (
                                  <button
                                    onClick={() => handleMarkAlertRead(alert.id)}
                                    className="px-3 py-1 bg-indigo-600 text-white rounded text-sm hover:bg-indigo-700"
                                  >
                                    Marcar como lido
                                  </button>
                                )}
                              </div>
                            </div>
                          ))
                        )}
                      </div>
                    )}
                  </div>

                  {/* Logs de Auditoria */}
                  <div>
                    <h3 className="text-xl font-semibold mb-4">📋 Logs de Auditoria</h3>
                    {loading ? (
                      <div className="text-center py-8">
                        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-500 mx-auto"></div>
                      </div>
                    ) : (
                      <div className="overflow-x-auto">
                        <table className="w-full">
                          <thead>
                            <tr className="border-b border-border">
                              <th className="text-left p-3">Ação</th>
                              <th className="text-left p-3">Tipo</th>
                              <th className="text-left p-3">IP</th>
                              <th className="text-left p-3">Data</th>
                            </tr>
                          </thead>
                          <tbody>
                            {auditLogs.map((log) => (
                              <tr key={log.id} className="border-b border-border hover:bg-background">
                                <td className="p-3">{log.action}</td>
                                <td className="p-3">
                                  <span className="px-2 py-1 rounded text-xs bg-gray-500/20 text-gray-400">
                                    {log.resource_type}
                                  </span>
                                </td>
                                <td className="p-3 text-sm text-muted-foreground">{log.ip_address}</td>
                                <td className="p-3 text-sm text-muted-foreground">
                                  {new Date(log.created_at).toLocaleString('pt-BR')}
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Tab: Relatórios */}
              {activeTab === 'reports' && (
                <div>
                  <h2 className="text-2xl font-bold mb-6">Relatórios do Sistema</h2>
                  
                  {/* Filtros de Data */}
                  <div className="mb-6 grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                      <label className="block text-sm font-medium mb-2">Data Inicial</label>
                      <input
                        type="date"
                        value={reportsStartDate}
                        onChange={(e) => setReportsStartDate(e.target.value)}
                        className="w-full px-4 py-3 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium mb-2">Data Final</label>
                      <input
                        type="date"
                        value={reportsEndDate}
                        onChange={(e) => setReportsEndDate(e.target.value)}
                        className="w-full px-4 py-3 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                      />
                    </div>
                    <div className="flex items-end">
                      <button
                        onClick={loadReports}
                        className="w-full px-4 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
                      >
                        Gerar Relatório
                      </button>
                    </div>
                  </div>

                  {loading ? (
                    <div className="text-center py-12">
                      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-500 mx-auto"></div>
                    </div>
                  ) : reportsData ? (
                    <div className="space-y-6">
                      {/* Estatísticas Gerais */}
                      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                        <div className="bg-background p-4 rounded-lg border border-border">
                          <div className="text-sm text-muted-foreground mb-1">Total de Transações</div>
                          <div className="text-2xl font-bold">{reportsData.transactions.total.toLocaleString()}</div>
                        </div>

                        <div className="bg-background p-4 rounded-lg border border-border">
                          <div className="text-sm text-muted-foreground mb-1">Volume Total</div>
                          <div className="text-2xl font-bold">
                            R$ {reportsData.transactions.volume.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                          </div>
                        </div>

                        <div className="bg-background p-4 rounded-lg border border-border">
                          <div className="text-sm text-muted-foreground mb-1">Total de Receitas</div>
                          <div className="text-2xl font-bold text-green-400">
                            R$ {reportsData.transactions.income.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                          </div>
                        </div>

                        <div className="bg-background p-4 rounded-lg border border-border">
                          <div className="text-sm text-muted-foreground mb-1">Total de Despesas</div>
                          <div className="text-2xl font-bold text-red-400">
                            R$ {reportsData.transactions.expenses.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                          </div>
                        </div>

                        <div className="bg-background p-4 rounded-lg border border-border">
                          <div className="text-sm text-muted-foreground mb-1">Contas Ativas</div>
                          <div className="text-2xl font-bold">{reportsData.accounts.active}</div>
                        </div>

                        <div className="bg-background p-4 rounded-lg border border-border">
                          <div className="text-sm text-muted-foreground mb-1">Total de Famílias</div>
                          <div className="text-2xl font-bold">{reportsData.families.total}</div>
                        </div>
                      </div>

                      {/* Período */}
                      <div className="bg-background p-4 rounded-lg border border-border">
                        <div className="text-sm text-muted-foreground mb-2">Período do Relatório</div>
                        <div className="text-sm">
                          {new Date(reportsData.period.start_date).toLocaleDateString('pt-BR')} até{' '}
                          {new Date(reportsData.period.end_date).toLocaleDateString('pt-BR')}
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div className="text-center py-12">
                      <p className="text-muted-foreground">Selecione um período e clique em "Gerar Relatório"</p>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

