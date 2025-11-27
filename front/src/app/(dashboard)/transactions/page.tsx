'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import apiClient from '@/lib/api/client'
import toast from 'react-hot-toast'

export default function TransactionsPage() {
  const router = useRouter()
  const [loading, setLoading] = useState(true)
  const [transactions, setTransactions] = useState<any[]>([])
  const [filteredTransactions, setFilteredTransactions] = useState<any[]>([])
  const [deletingId, setDeletingId] = useState<string | null>(null)
  
  // Filtros de busca
  const [searchText, setSearchText] = useState('')
  const [filterStatus, setFilterStatus] = useState<string>('all')
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
    const month = now.getMonth() // 0-11 (novembro = 10)
    
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
    loadTransactions()
  }, [startDate, endDate])

  useEffect(() => {
    applyFilters()
  }, [transactions, searchText, filterStatus, filterType, filterCategory])

  const loadCategories = async () => {
    try {
      const response = await apiClient.get('/categories/')
      setCategories(Array.isArray(response.data) ? response.data : [])
    } catch (error: any) {
      // Categorias são opcionais
      setCategories([])
    }
  }

  const loadTransactions = async () => {
    setLoading(true)
    try {
      let url = '/transactions/'
      const params = new URLSearchParams()
      
      if (startDate) {
        // Enviar data no formato YYYY-MM-DDTHH:mm:ss com timezone UTC
        // Usar meia-noite UTC para garantir que não mude de dia
        const [year, month, day] = startDate.split('-').map(Number)
        const startISO = `${year}-${String(month).padStart(2, '0')}-${String(day).padStart(2, '0')}T00:00:00Z`
        params.append('start_date', startISO)
      }
      if (endDate) {
        // Enviar data no formato YYYY-MM-DDTHH:mm:ss com timezone UTC
        // Usar 23:59:59 UTC para garantir que inclua todo o dia
        const [year, month, day] = endDate.split('-').map(Number)
        const endISO = `${year}-${String(month).padStart(2, '0')}-${String(day).padStart(2, '0')}T23:59:59Z`
        params.append('end_date', endISO)
      }
      
      if (params.toString()) {
        url += `?${params.toString()}`
      }
      
      const response = await apiClient.get(url)
      // Lidar com resposta paginada ou array direto (compatibilidade)
      if (response.data && typeof response.data === 'object' && 'transactions' in response.data) {
        setTransactions(response.data.transactions)
      } else if (Array.isArray(response.data)) {
        setTransactions(response.data)
      } else {
        setTransactions([])
      }
    } catch (error: any) {
      if (error.response?.status === 401) {
        router.push('/login')
      } else {
        toast.error('Erro ao carregar transações')
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
      // Voltar para o mês atual
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
    // Parse da data atual considerando timezone local
    const [year, month, day] = startDate.split('-').map(Number)
    const currentDate = new Date(year, month - 1, day)
    const newDate = new Date(currentDate.getFullYear(), currentDate.getMonth() + monthsOffset, 1)
    
    const firstDay = new Date(newDate.getFullYear(), newDate.getMonth(), 1)
    const lastDay = new Date(newDate.getFullYear(), newDate.getMonth() + 1, 0)
    
    setStartDate(formatDateLocal(firstDay))
    setEndDate(formatDateLocal(lastDay))
  }

  const applyFilters = () => {
    let filtered = [...transactions]

    // Excluir transações canceladas por padrão (só mostrar se filtro for explicitamente "cancelled")
    if (filterStatus !== 'cancelled') {
      filtered = filtered.filter(transaction => transaction.status !== 'cancelled')
    }

    // Busca por texto (descrição)
    if (searchText.trim()) {
      const searchLower = searchText.toLowerCase()
      filtered = filtered.filter(transaction =>
        transaction.description?.toLowerCase().includes(searchLower) ||
        transaction.category?.name?.toLowerCase().includes(searchLower) ||
        transaction.notes?.toLowerCase().includes(searchLower)
      )
    }

    // Filtro por status
    if (filterStatus !== 'all') {
      filtered = filtered.filter(transaction => transaction.status === filterStatus)
    }

    // Filtro por tipo
    if (filterType !== 'all') {
      filtered = filtered.filter(transaction => transaction.transaction_type === filterType)
    }

    // Filtro por categoria
    if (filterCategory !== 'all') {
      filtered = filtered.filter(transaction => 
        transaction.category?.id === filterCategory
      )
    }

    setFilteredTransactions(filtered)
  }

  const handleDelete = async (transactionId: string) => {
    if (!confirm('Tem certeza que deseja excluir esta transação? Esta ação não pode ser desfeita.')) {
      return
    }

    setDeletingId(transactionId)
    try {
      await apiClient.delete(`/transactions/${transactionId}`)
      toast.success('Transação excluída com sucesso!')
      loadTransactions() // Recarregar lista
    } catch (error: any) {
      console.error('Erro ao excluir transação:', error)
      const errorMessage = error.response?.data?.detail || error.message || 'Erro ao excluir transação'
      toast.error(errorMessage)
    } finally {
      setDeletingId(null)
    }
  }

  const handleEdit = (transactionId: string) => {
    router.push(`/transactions/${transactionId}/edit`)
  }

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold mb-2">Transações</h1>
            <p className="text-muted-foreground">Gerencie suas receitas e despesas</p>
          </div>
          <button
            onClick={() => router.push('/transactions/new')}
            className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors font-medium"
          >
            + Nova Transação
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
                      // Parse da data considerando timezone local
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
                  placeholder="Buscar por descrição, categoria ou notas..."
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
                <option value="completed">Concluída</option>
                <option value="pending">Pendente</option>
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
                <option value="income">Receita</option>
                <option value="expense">Despesa</option>
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
            {filteredTransactions.length} de {transactions.length} transações
            {dateRange === 'custom' && (
              <span className="ml-2">
                ({new Date(startDate).toLocaleDateString('pt-BR')} até {new Date(endDate).toLocaleDateString('pt-BR')})
              </span>
            )}
            {(searchText || filterStatus !== 'all' || filterType !== 'all' || filterCategory !== 'all') && (
              <button
                onClick={() => {
                  setSearchText('')
                  setFilterStatus('all')
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

        {loading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-500 mx-auto"></div>
          </div>
        ) : (
          <div className="glass rounded-xl p-6">
            {filteredTransactions.length > 0 ? (
              <div className="space-y-3">
                {filteredTransactions.map((transaction) => (
                  <div
                    key={transaction.id}
                    className="flex items-center justify-between p-4 bg-background/50 rounded-lg hover:bg-background/70 transition-colors"
                  >
                    <div className="flex items-center gap-4 flex-1">
                      <div className={`w-12 h-12 rounded-lg flex items-center justify-center flex-shrink-0 ${
                        transaction.transaction_type === 'income' 
                          ? 'bg-green-500/20' 
                          : 'bg-red-500/20'
                      }`}>
                        <span className="text-xl">
                          {transaction.transaction_type === 'income' ? '📈' : '📉'}
                        </span>
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 flex-wrap mb-1">
                          <p className="font-medium truncate">{transaction.description}</p>
                          {/* Status destacado */}
                          <span className={`px-3 py-1 text-xs rounded-full font-semibold border ${
                            transaction.status === 'completed' 
                              ? 'bg-green-500/20 text-green-400 border-green-500/30' 
                              : transaction.status === 'pending'
                              ? 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30'
                              : 'bg-red-500/20 text-red-400 border-red-500/30'
                          }`}>
                            {transaction.status === 'completed' ? '✓ Concluída' : 
                             transaction.status === 'pending' ? '⏳ Pendente' : 
                             '✗ Cancelada'}
                          </span>
                        </div>
                        <div className="flex items-center gap-2 flex-wrap">
                          <div className="flex items-center gap-1 text-sm text-muted-foreground">
                            <span className="font-medium">Data da Transação:</span>
                            <span>
                              {new Date(transaction.transaction_date).toLocaleDateString('pt-BR', {
                                day: '2-digit',
                                month: '2-digit',
                                year: 'numeric',
                                hour: '2-digit',
                                minute: '2-digit'
                              })}
                            </span>
                          </div>
                          {transaction.created_at && (
                            <div className="flex items-center gap-1 text-xs text-muted-foreground/80">
                              <span className="font-medium">Cadastrada:</span>
                              <span>
                                {new Date(transaction.created_at).toLocaleDateString('pt-BR', {
                                  day: '2-digit',
                                  month: '2-digit',
                                  year: 'numeric',
                                  hour: '2-digit',
                                  minute: '2-digit'
                                })}
                              </span>
                            </div>
                          )}
                          <span className={`px-2 py-0.5 text-xs rounded font-medium ${
                            transaction.transaction_type === 'income'
                              ? 'bg-green-500/20 text-green-400'
                              : 'bg-red-500/20 text-red-400'
                          }`}>
                            {transaction.transaction_type === 'income' ? 'Receita' : 'Despesa'}
                          </span>
                          {transaction.category && (
                            <span className="px-2 py-0.5 text-xs bg-indigo-500/20 text-indigo-300 rounded font-medium">
                              {transaction.category.name}
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-4">
                      <div className={`text-lg font-semibold ${
                        transaction.transaction_type === 'income' 
                          ? 'text-green-400' 
                          : 'text-red-400'
                      }`}>
                        {transaction.transaction_type === 'income' ? '+' : '-'}
                        {new Intl.NumberFormat('pt-BR', {
                          style: 'currency',
                          currency: 'BRL'
                        }).format(transaction.amount)}
                      </div>
                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => handleEdit(transaction.id)}
                          className="p-2 text-indigo-400 hover:text-indigo-300 hover:bg-indigo-500/10 rounded-lg transition-colors"
                          title="Editar transação"
                        >
                          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                          </svg>
                        </button>
                        <button
                          onClick={() => handleDelete(transaction.id)}
                          disabled={deletingId === transaction.id}
                          className="p-2 text-red-400 hover:text-red-300 hover:bg-red-500/10 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                          title="Excluir transação"
                        >
                          {deletingId === transaction.id ? (
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
            ) : transactions.length === 0 ? (
              <div className="text-center py-12">
                <p className="text-muted-foreground">Nenhuma transação encontrada</p>
                <button
                  onClick={() => router.push('/transactions/new')}
                  className="mt-4 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
                >
                  Criar Transação
                </button>
              </div>
            ) : (
              <div className="text-center py-12">
                <p className="text-muted-foreground">Nenhuma transação encontrada com os filtros aplicados</p>
                <button
                  onClick={() => {
                    setSearchText('')
                    setFilterStatus('all')
                    setFilterType('all')
                    setFilterCategory('all')
                  }}
                  className="mt-4 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
                >
                  Limpar Filtros
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

