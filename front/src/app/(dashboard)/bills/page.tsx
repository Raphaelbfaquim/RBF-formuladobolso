'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import apiClient from '@/lib/api/client'
import toast from 'react-hot-toast'

interface Bill {
  id: string
  name: string
  description?: string
  bill_type: 'expense' | 'income'
  amount: number
  due_date: string
  status: string
  is_recurring: boolean
  recurrence_type: string
  days_until_due?: number
  is_overdue: boolean
  account_id?: string
  category_id?: string
  category?: {
    id: string
    name: string
  }
}

export default function BillsPage() {
  const router = useRouter()
  const [loading, setLoading] = useState(true)
  const [bills, setBills] = useState<Bill[]>([])
  const [filteredBills, setFilteredBills] = useState<Bill[]>([])
  const [deletingId, setDeletingId] = useState<string | null>(null)
  const [payingId, setPayingId] = useState<string | null>(null)
  
  // Filtros de busca
  const [searchText, setSearchText] = useState('')
  const [filterStatus, setFilterStatus] = useState<string>('pending')
  const [filterType, setFilterType] = useState<string>('all')
  const [filterCategory, setFilterCategory] = useState<string>('all')
  const [categories, setCategories] = useState<any[]>([])
  
  // Filtros de data
  const [dateRange, setDateRange] = useState<'month' | 'custom'>('month')
  const [startDate, setStartDate] = useState<string>('')
  const [endDate, setEndDate] = useState<string>('')

  useEffect(() => {
    // Inicializar com o mês atual (usando timezone local)
    const now = new Date()
    const year = now.getFullYear()
    const month = now.getMonth()
    
    // Primeiro dia do mês (1)
    const firstDay = new Date(year, month, 1)
    // Último dia do mês (0 do próximo mês)
    const lastDay = new Date(year, month + 1, 0)
    
    // Formatar como YYYY-MM-DD usando timezone local
    const formatDate = (date: Date) => {
      const y = date.getFullYear()
      const m = String(date.getMonth() + 1).padStart(2, '0')
      const d = String(date.getDate()).padStart(2, '0')
      return `${y}-${m}-${d}`
    }
    
    const start = formatDate(firstDay)
    const end = formatDate(lastDay)
    
    setStartDate(start)
    setEndDate(end)
    
    loadCategories()
  }, [])

  useEffect(() => {
    loadBills()
  }, [startDate, endDate])

  useEffect(() => {
    applyFilters()
  }, [bills, searchText, filterStatus, filterType, filterCategory])

  const loadCategories = async () => {
    try {
      const response = await apiClient.get('/categories/')
      setCategories(Array.isArray(response.data) ? response.data : [])
    } catch (error: any) {
      // Categorias são opcionais
      setCategories([])
    }
  }

  const loadBills = async () => {
    setLoading(true)
    try {
      let url = '/bills/'
      const params = new URLSearchParams()
      
      if (startDate) {
        const [year, month, day] = startDate.split('-').map(Number)
        const startISO = `${year}-${String(month).padStart(2, '0')}-${String(day).padStart(2, '0')}T00:00:00Z`
        params.append('start_date', startISO)
      }
      if (endDate) {
        const [year, month, day] = endDate.split('-').map(Number)
        const endISO = `${year}-${String(month).padStart(2, '0')}-${String(day).padStart(2, '0')}T23:59:59Z`
        params.append('end_date', endISO)
      }
      
      if (params.toString()) {
        url += `?${params.toString()}`
      }
      
      const response = await apiClient.get(url)
      setBills(response.data)
    } catch (error: any) {
      if (error.response?.status === 401) {
        router.push('/login')
      } else {
        toast.error('Erro ao carregar contas')
      }
    } finally {
      setLoading(false)
    }
  }

  const formatDateLocal = (date: Date) => {
    const y = date.getFullYear()
    const m = String(date.getMonth() + 1).padStart(2, '0')
    const d = String(date.getDate()).padStart(2, '0')
    return `${y}-${m}-${d}`
  }

  const handleDateRangeChange = (range: 'month' | 'custom') => {
    setDateRange(range)
    
    if (range === 'month') {
      const now = new Date()
      const year = now.getFullYear()
      const month = now.getMonth()
      
      const firstDay = new Date(year, month, 1)
      const lastDay = new Date(year, month + 1, 0)
      
      setStartDate(formatDateLocal(firstDay))
      setEndDate(formatDateLocal(lastDay))
    }
  }

  const handleMonthChange = (monthsOffset: number) => {
    const [year, month, day] = startDate.split('-').map(Number)
    const currentDate = new Date(year, month - 1, day)
    const newDate = new Date(currentDate.getFullYear(), currentDate.getMonth() + monthsOffset, 1)
    
    const firstDay = new Date(newDate.getFullYear(), newDate.getMonth(), 1)
    const lastDay = new Date(newDate.getFullYear(), newDate.getMonth() + 1, 0)
    
    setStartDate(formatDateLocal(firstDay))
    setEndDate(formatDateLocal(lastDay))
  }

  const applyFilters = () => {
    let filtered = [...bills]

    // Excluir contas canceladas por padrão (só mostrar se filtro for explicitamente "cancelled")
    if (filterStatus !== 'cancelled') {
      filtered = filtered.filter(bill => bill.status !== 'cancelled')
    }

    // Busca por texto (nome, descrição)
    if (searchText.trim()) {
      const searchLower = searchText.toLowerCase()
      filtered = filtered.filter(bill =>
        bill.name?.toLowerCase().includes(searchLower) ||
        bill.description?.toLowerCase().includes(searchLower) ||
        bill.category?.name?.toLowerCase().includes(searchLower)
      )
    }

    // Filtro por status
    if (filterStatus !== 'all') {
      filtered = filtered.filter(bill => bill.status === filterStatus)
    }

    // Filtro por tipo
    if (filterType !== 'all') {
      filtered = filtered.filter(bill => bill.bill_type === filterType)
    }

    // Filtro por categoria
    if (filterCategory !== 'all') {
      filtered = filtered.filter(bill => 
        bill.category?.id === filterCategory
      )
    }

    setFilteredBills(filtered)
  }

  const handlePayBill = async (billId: string) => {
    if (!confirm('Deseja marcar esta conta como paga? Uma transação será criada automaticamente.')) {
      return
    }

    setPayingId(billId)
    try {
      await apiClient.post(`/bills/${billId}/pay`)
      toast.success('Conta marcada como paga!')
      loadBills()
    } catch (error: any) {
      console.error('Erro ao pagar conta:', error)
      const errorMessage = error.response?.data?.detail || 'Erro ao pagar conta'
      toast.error(errorMessage)
    } finally {
      setPayingId(null)
    }
  }

  const handleDelete = async (billId: string) => {
    if (!confirm('Tem certeza que deseja excluir esta conta? Esta ação não pode ser desfeita.')) {
      return
    }

    setDeletingId(billId)
    try {
      await apiClient.delete(`/bills/${billId}`)
      toast.success('Conta excluída com sucesso!')
      loadBills()
    } catch (error: any) {
      console.error('Erro ao excluir conta:', error)
      const errorMessage = error.response?.data?.detail || 'Erro ao excluir conta'
      toast.error(errorMessage)
    } finally {
      setDeletingId(null)
    }
  }

  const handleEdit = (billId: string) => {
    router.push(`/bills/${billId}/edit`)
  }

  const getStatusColor = (status: string, isOverdue: boolean) => {
    if (isOverdue) return 'text-red-400 bg-red-500/20'
    if (status === 'paid' || status === 'received') return 'text-green-400 bg-green-500/20'
    return 'text-yellow-400 bg-yellow-500/20'
  }

  const getStatusText = (status: string) => {
    const statusMap: Record<string, string> = {
      pending: 'Pendente',
      paid: 'Pago',
      received: 'Recebido',
      overdue: 'Vencido',
      cancelled: 'Cancelado',
    }
    return statusMap[status] || status
  }

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold mb-2">Contas a Pagar/Receber</h1>
            <p className="text-muted-foreground">Gerencie suas contas recorrentes</p>
          </div>
          <button
            onClick={() => router.push('/bills/new')}
            className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors font-medium"
          >
            + Nova Conta
          </button>
        </div>

        {/* Filtros de Busca */}
        <div className="mb-6 glass rounded-xl p-4">
          {/* Filtro de Data */}
          <div className="mb-4 pb-4 border-b border-border">
            <label className="block text-sm font-medium mb-3">Período</label>
            <div className="flex flex-wrap items-center gap-3">
              <div className="flex gap-2">
                <button
                  onClick={() => handleDateRangeChange('month')}
                  className={`px-4 py-2 rounded-lg transition-colors font-medium ${
                    dateRange === 'month'
                      ? 'bg-indigo-600 text-white'
                      : 'bg-background border border-border text-foreground hover:bg-muted'
                  }`}
                >
                  Mês Atual
                </button>
                <button
                  onClick={() => handleDateRangeChange('custom')}
                  className={`px-4 py-2 rounded-lg transition-colors font-medium ${
                    dateRange === 'custom'
                      ? 'bg-indigo-600 text-white'
                      : 'bg-background border border-border text-foreground hover:bg-muted'
                  }`}
                >
                  Período Personalizado
                </button>
              </div>

              {dateRange === 'month' && (
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => handleMonthChange(-1)}
                    className="p-2 text-muted-foreground hover:text-foreground hover:bg-muted rounded-lg transition-colors"
                    title="Mês anterior"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                    </svg>
                  </button>
                  <span className="px-3 py-1 text-sm font-medium capitalize">
                    {(() => {
                      const [year, month, day] = startDate.split('-').map(Number)
                      const date = new Date(year, month - 1, day)
                      return date.toLocaleDateString('pt-BR', { month: 'long', year: 'numeric' })
                    })()}
                  </span>
                  <button
                    onClick={() => handleMonthChange(1)}
                    className="p-2 text-muted-foreground hover:text-foreground hover:bg-muted rounded-lg transition-colors"
                    title="Próximo mês"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                    </svg>
                  </button>
                </div>
              )}

              {dateRange === 'custom' && (
                <div className="flex items-center gap-3 flex-wrap">
                  <div>
                    <label className="text-xs text-muted-foreground mb-1 block">Data Inicial</label>
                    <input
                      type="date"
                      value={startDate}
                      onChange={(e) => setStartDate(e.target.value)}
                      className="px-3 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    />
                  </div>
                  <div>
                    <label className="text-xs text-muted-foreground mb-1 block">Data Final</label>
                    <input
                      type="date"
                      value={endDate}
                      onChange={(e) => setEndDate(e.target.value)}
                      min={startDate}
                      className="px-3 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    />
                  </div>
                </div>
              )}
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Busca por texto */}
            <div className="lg:col-span-2">
              <label className="block text-sm font-medium mb-2">Buscar</label>
              <div className="relative">
                <input
                  type="text"
                  value={searchText}
                  onChange={(e) => setSearchText(e.target.value)}
                  placeholder="Buscar por nome, descrição ou categoria..."
                  className="w-full px-4 py-2 pl-10 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
                <svg className="w-5 h-5 absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
            </div>

            {/* Filtro por Status */}
            <div>
              <label className="block text-sm font-medium mb-2">Status</label>
              <select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
                className="w-full px-4 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                <option value="all">Todos</option>
                <option value="pending">Pendente</option>
                <option value="paid">Pago</option>
                <option value="received">Recebido</option>
                <option value="overdue">Vencido</option>
                <option value="cancelled">Cancelada</option>
              </select>
            </div>

            {/* Filtro por Tipo */}
            <div>
              <label className="block text-sm font-medium mb-2">Tipo</label>
              <select
                value={filterType}
                onChange={(e) => setFilterType(e.target.value)}
                className="w-full px-4 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                <option value="all">Todos</option>
                <option value="expense">Contas a Pagar</option>
                <option value="income">Contas a Receber</option>
              </select>
            </div>
          </div>

          {/* Filtro por Categoria */}
          {categories.length > 0 && (
            <div className="mt-4">
              <label className="block text-sm font-medium mb-2">Categoria</label>
              <select
                value={filterCategory}
                onChange={(e) => setFilterCategory(e.target.value)}
                className="w-full px-4 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                <option value="all">Todas</option>
                {categories.map((category) => (
                  <option key={category.id} value={category.id}>
                    {category.name}
                  </option>
                ))}
              </select>
            </div>
          )}

          {/* Contador de resultados */}
          <div className="mt-4 text-sm text-muted-foreground">
            {filteredBills.length} de {bills.length} contas
            {dateRange === 'custom' && (
              <span className="ml-2">
                ({new Date(startDate).toLocaleDateString('pt-BR')} até {new Date(endDate).toLocaleDateString('pt-BR')})
              </span>
            )}
            {(searchText || filterStatus !== 'all' || filterType !== 'all' || filterCategory !== 'all') && (
              <button
                onClick={() => {
                  setSearchText('')
                  setFilterStatus('pending')
                  setFilterType('all')
                  setFilterCategory('all')
                }}
                className="ml-2 text-indigo-400 hover:text-indigo-300 underline"
              >
                Limpar filtros
              </button>
            )}
          </div>
        </div>

        {/* Lista de Contas */}
        {loading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-500 mx-auto"></div>
            <p className="mt-4 text-muted-foreground">Carregando contas...</p>
          </div>
        ) : filteredBills.length > 0 ? (
          <div className="space-y-3">
            {filteredBills.map((bill) => (
              <div
                key={bill.id}
                className={`glass rounded-xl p-6 hover:bg-background/70 transition-colors ${
                  bill.is_overdue ? 'border-l-4 border-red-500' : ''
                }`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2 flex-wrap">
                      <h3 className="text-xl font-semibold">{bill.name}</h3>
                      <span className={`px-2 py-1 rounded text-xs font-medium ${getStatusColor(bill.status, bill.is_overdue)}`}>
                        {getStatusText(bill.status)}
                      </span>
                      {bill.is_overdue && (
                        <span className="px-2 py-1 rounded text-xs bg-red-500/20 text-red-400 font-medium">
                          ⚠️ Vencida
                        </span>
                      )}
                      {bill.is_recurring && (
                        <span className="px-2 py-1 rounded text-xs bg-blue-500/20 text-blue-400">
                          🔄 Recorrente
                        </span>
                      )}
                    </div>
                    {bill.description && (
                      <p className="text-sm text-muted-foreground mb-2">{bill.description}</p>
                    )}
                    <div className="flex items-center gap-4 text-sm flex-wrap">
                      <span className={`font-semibold text-lg ${bill.bill_type === 'income' ? 'text-green-400' : 'text-red-400'}`}>
                        {bill.bill_type === 'income' ? '+' : '-'}
                        {new Intl.NumberFormat('pt-BR', {
                          style: 'currency',
                          currency: 'BRL'
                        }).format(bill.amount)}
                      </span>
                      <span className="text-muted-foreground">
                        📅 Vencimento: {new Date(bill.due_date).toLocaleDateString('pt-BR', {
                          day: '2-digit',
                          month: '2-digit',
                          year: 'numeric'
                        })}
                      </span>
                      {bill.days_until_due !== undefined && bill.days_until_due !== null && bill.days_until_due > 0 && (
                        <span className="text-muted-foreground">
                          ⏱️ {bill.days_until_due} {bill.days_until_due === 1 ? 'dia restante' : 'dias restantes'}
                        </span>
                      )}
                      {bill.category && (
                        <span className="px-2 py-0.5 text-xs bg-indigo-500/20 text-indigo-300 rounded font-medium">
                          {bill.category.name}
                        </span>
                      )}
                    </div>
                  </div>
                  <div className="flex gap-2 ml-4">
                    <button
                      onClick={() => handleEdit(bill.id)}
                      className="p-2 text-indigo-400 hover:text-indigo-300 hover:bg-indigo-500/10 rounded-lg transition-colors"
                      title="Editar conta"
                    >
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                      </svg>
                    </button>
                    {bill.status === 'pending' && (
                      <button
                        onClick={() => handlePayBill(bill.id)}
                        disabled={payingId === bill.id}
                        className="p-2 text-green-400 hover:text-green-300 hover:bg-green-500/10 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                        title="Marcar como pago"
                      >
                        {payingId === bill.id ? (
                          <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-green-400"></div>
                        ) : (
                          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                        )}
                      </button>
                    )}
                    <button
                      onClick={() => handleDelete(bill.id)}
                      disabled={deletingId === bill.id}
                      className="p-2 text-red-400 hover:text-red-300 hover:bg-red-500/10 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                      title="Excluir conta"
                    >
                      {deletingId === bill.id ? (
                        <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-red-400"></div>
                      ) : (
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                      )}
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : bills.length === 0 ? (
          <div className="text-center py-12 glass rounded-xl">
            <p className="text-muted-foreground mb-4">Nenhuma conta encontrada</p>
            <button
              onClick={() => router.push('/bills/new')}
              className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
            >
              Criar Primeira Conta
            </button>
          </div>
        ) : (
          <div className="text-center py-12 glass rounded-xl">
            <p className="text-muted-foreground mb-4">Nenhuma conta encontrada com os filtros aplicados</p>
            <button
              onClick={() => {
                setSearchText('')
                setFilterStatus('pending')
                setFilterType('all')
                setFilterCategory('all')
              }}
              className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
            >
              Limpar Filtros
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
