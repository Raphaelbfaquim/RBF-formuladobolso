'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import apiClient from '@/lib/api/client'
import toast from 'react-hot-toast'
import { 
  BarChart, Bar, LineChart, Line, PieChart, Pie, Cell, 
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  AreaChart, Area
} from 'recharts'

type ReportType = 'executive' | 'income' | 'expense' | 'categories' | 'planning' | 'comparative' | 'trends' | 'goals' | 'temporal' | 'accounts'

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#06b6d4', '#84cc16']

export default function ReportsPage() {
  const router = useRouter()
  const [loading, setLoading] = useState(false)
  const [activeReport, setActiveReport] = useState<ReportType>('executive')
  const [dateRange, setDateRange] = useState<'month' | 'quarter' | 'year' | 'custom'>('month')
  const [startDate, setStartDate] = useState<string>('')
  const [endDate, setEndDate] = useState<string>('')
  
  // Dados dos relatórios
  const [executiveData, setExecutiveData] = useState<any>(null)
  const [incomeData, setIncomeData] = useState<any>(null)
  const [expenseData, setExpenseData] = useState<any>(null)
  const [categoriesData, setCategoriesData] = useState<any>(null)
  const [planningData, setPlanningData] = useState<any>(null)
  const [comparativeData, setComparativeData] = useState<any>(null)
  const [trendsData, setTrendsData] = useState<any>(null)
  const [goalsData, setGoalsData] = useState<any>(null)
  const [temporalData, setTemporalData] = useState<any>(null)
  const [accountsData, setAccountsData] = useState<any>(null)

  useEffect(() => {
    // Inicializar com o mês atual
    const now = new Date()
    const year = now.getFullYear()
    const month = now.getMonth()
    
    const firstDay = new Date(year, month, 1)
    const lastDay = new Date(year, month + 1, 0)
    
    const formatDate = (date: Date) => {
      return date.toISOString().split('T')[0]
    }
    
    setStartDate(formatDate(firstDay))
    setEndDate(formatDate(lastDay))
  }, [])

  useEffect(() => {
    if (startDate && endDate) {
      loadReport()
    }
  }, [activeReport, startDate, endDate])

  const loadReport = async () => {
    if (!startDate || !endDate) return
    
    setLoading(true)
    try {
      const start = new Date(startDate).toISOString()
      const end = new Date(endDate + 'T23:59:59').toISOString()
      
      switch (activeReport) {
        case 'executive':
          const execResponse = await apiClient.get(`/reports/executive?start_date=${start}&end_date=${end}`)
          setExecutiveData(execResponse.data)
          break
        case 'income':
          const incomeResponse = await apiClient.get(`/reports/income?start_date=${start}&end_date=${end}`)
          setIncomeData(incomeResponse.data)
          break
        case 'expense':
          const expenseResponse = await apiClient.get(`/reports/expense?start_date=${start}&end_date=${end}`)
          setExpenseData(expenseResponse.data)
          break
        case 'categories':
          const categoriesResponse = await apiClient.get(`/reports/categories?start_date=${start}&end_date=${end}`)
          setCategoriesData(categoriesResponse.data)
          break
        case 'planning':
          const planningResponse = await apiClient.get(`/reports/planning-vs-real?start_date=${start}&end_date=${end}`)
          setPlanningData(planningResponse.data)
          break
        case 'comparative':
          const comparativeResponse = await apiClient.get(`/reports/comparative?start_date=${start}&end_date=${end}`)
          setComparativeData(comparativeResponse.data)
          break
        case 'trends':
          const trendsResponse = await apiClient.get(`/reports/trends?start_date=${start}&end_date=${end}`)
          setTrendsData(trendsResponse.data)
          break
        case 'goals':
          const goalsResponse = await apiClient.get(`/reports/goals`)
          setGoalsData(goalsResponse.data)
          break
        case 'temporal':
          const temporalResponse = await apiClient.get(`/reports/temporal?start_date=${start}&end_date=${end}`)
          setTemporalData(temporalResponse.data)
          break
        case 'accounts':
          const accountsResponse = await apiClient.get(`/reports/accounts?start_date=${start}&end_date=${end}`)
          setAccountsData(accountsResponse.data)
          break
      }
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Erro ao carregar relatório')
    } finally {
      setLoading(false)
    }
  }

  const handleDateRangeChange = (range: 'month' | 'quarter' | 'year' | 'custom') => {
    setDateRange(range)
    const now = new Date()
    
    if (range === 'month') {
      const year = now.getFullYear()
      const month = now.getMonth()
      const firstDay = new Date(year, month, 1)
      const lastDay = new Date(year, month + 1, 0)
      setStartDate(firstDay.toISOString().split('T')[0])
      setEndDate(lastDay.toISOString().split('T')[0])
    } else if (range === 'quarter') {
      const quarter = Math.floor(now.getMonth() / 3)
      const firstDay = new Date(now.getFullYear(), quarter * 3, 1)
      const lastDay = new Date(now.getFullYear(), (quarter + 1) * 3, 0)
      setStartDate(firstDay.toISOString().split('T')[0])
      setEndDate(lastDay.toISOString().split('T')[0])
    } else if (range === 'year') {
      const firstDay = new Date(now.getFullYear(), 0, 1)
      const lastDay = new Date(now.getFullYear(), 11, 31)
      setStartDate(firstDay.toISOString().split('T')[0])
      setEndDate(lastDay.toISOString().split('T')[0])
    }
  }

  const exportToPDF = async () => {
    try {
      const start = new Date(startDate).toISOString()
      const end = new Date(endDate + 'T23:59:59').toISOString()
      const year = new Date(startDate).getFullYear()
      const month = new Date(startDate).getMonth() + 1
      
      const response = await apiClient.get(`/reports/monthly/pdf?year=${year}&month=${month}`, {
        responseType: 'blob'
      })
      
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `relatorio_${month.toString().padStart(2, '0')}_${year}.pdf`)
      document.body.appendChild(link)
      link.click()
      link.remove()
      
      toast.success('PDF gerado com sucesso!')
    } catch (error: any) {
      toast.error('Erro ao gerar PDF')
    }
  }

  const exportToExcel = async () => {
    try {
      const start = new Date(startDate).toISOString()
      const end = new Date(endDate + 'T23:59:59').toISOString()
      
      const response = await apiClient.get(`/reports/transactions/excel?start_date=${start}&end_date=${end}`, {
        responseType: 'blob'
      })
      
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', 'transacoes.xlsx')
      document.body.appendChild(link)
      link.click()
      link.remove()
      
      toast.success('Excel gerado com sucesso!')
    } catch (error: any) {
      toast.error('Erro ao gerar Excel')
    }
  }

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-3xl font-bold mb-2">📊 Relatórios</h1>
            <p className="text-muted-foreground">Análise detalhada das suas finanças</p>
          </div>
          <div className="flex gap-3">
            <button
              onClick={exportToPDF}
              className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 font-medium"
            >
              📄 Exportar PDF
            </button>
            <button
              onClick={exportToExcel}
              className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 font-medium"
            >
              📊 Exportar Excel
            </button>
          </div>
        </div>

        {/* Filtros */}
        <div className="glass rounded-xl p-4 mb-6">
          <div className="flex flex-wrap items-center gap-4">
            <div className="flex gap-2">
              <button
                onClick={() => handleDateRangeChange('month')}
                className={`px-4 py-2 rounded-lg transition-colors ${
                  dateRange === 'month' ? 'bg-indigo-600 text-white' : 'bg-background hover:bg-muted'
                }`}
              >
                Mês Atual
              </button>
              <button
                onClick={() => handleDateRangeChange('quarter')}
                className={`px-4 py-2 rounded-lg transition-colors ${
                  dateRange === 'quarter' ? 'bg-indigo-600 text-white' : 'bg-background hover:bg-muted'
                }`}
              >
                Trimestre
              </button>
              <button
                onClick={() => handleDateRangeChange('year')}
                className={`px-4 py-2 rounded-lg transition-colors ${
                  dateRange === 'year' ? 'bg-indigo-600 text-white' : 'bg-background hover:bg-muted'
                }`}
              >
                Ano
              </button>
              <button
                onClick={() => setDateRange('custom')}
                className={`px-4 py-2 rounded-lg transition-colors ${
                  dateRange === 'custom' ? 'bg-indigo-600 text-white' : 'bg-background hover:bg-muted'
                }`}
              >
                Personalizado
              </button>
            </div>
            
            {dateRange === 'custom' && (
              <div className="flex gap-2 items-center">
                <input
                  type="date"
                  value={startDate}
                  onChange={(e) => setStartDate(e.target.value)}
                  className="px-3 py-2 bg-background border border-border rounded-lg"
                />
                <span className="text-muted-foreground">até</span>
                <input
                  type="date"
                  value={endDate}
                  onChange={(e) => setEndDate(e.target.value)}
                  className="px-3 py-2 bg-background border border-border rounded-lg"
                />
              </div>
            )}
          </div>
        </div>

        {/* Navegação de Relatórios */}
        <div className="flex flex-wrap gap-2 mb-6 overflow-x-auto">
          <button
            onClick={() => setActiveReport('executive')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors whitespace-nowrap ${
              activeReport === 'executive'
                ? 'bg-indigo-600 text-white'
                : 'bg-background hover:bg-muted'
            }`}
          >
            📈 Executivo
          </button>
          <button
            onClick={() => setActiveReport('income')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors whitespace-nowrap ${
              activeReport === 'income'
                ? 'bg-indigo-600 text-white'
                : 'bg-background hover:bg-muted'
            }`}
          >
            💰 Receitas
          </button>
          <button
            onClick={() => setActiveReport('expense')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors whitespace-nowrap ${
              activeReport === 'expense'
                ? 'bg-indigo-600 text-white'
                : 'bg-background hover:bg-muted'
            }`}
          >
            💸 Despesas
          </button>
          <button
            onClick={() => setActiveReport('categories')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors whitespace-nowrap ${
              activeReport === 'categories'
                ? 'bg-indigo-600 text-white'
                : 'bg-background hover:bg-muted'
            }`}
          >
            📂 Categorias
          </button>
          <button
            onClick={() => setActiveReport('planning')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors whitespace-nowrap ${
              activeReport === 'planning'
                ? 'bg-indigo-600 text-white'
                : 'bg-background hover:bg-muted'
            }`}
          >
            📊 Planejamento
          </button>
          <button
            onClick={() => setActiveReport('comparative')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors whitespace-nowrap ${
              activeReport === 'comparative'
                ? 'bg-indigo-600 text-white'
                : 'bg-background hover:bg-muted'
            }`}
          >
            📈 Comparativo
          </button>
          <button
            onClick={() => setActiveReport('trends')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors whitespace-nowrap ${
              activeReport === 'trends'
                ? 'bg-indigo-600 text-white'
                : 'bg-background hover:bg-muted'
            }`}
          >
            📉 Tendências
          </button>
          <button
            onClick={() => setActiveReport('goals')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors whitespace-nowrap ${
              activeReport === 'goals'
                ? 'bg-indigo-600 text-white'
                : 'bg-background hover:bg-muted'
            }`}
          >
            🎯 Metas
          </button>
          <button
            onClick={() => setActiveReport('temporal')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors whitespace-nowrap ${
              activeReport === 'temporal'
                ? 'bg-indigo-600 text-white'
                : 'bg-background hover:bg-muted'
            }`}
          >
            ⏰ Temporal
          </button>
          <button
            onClick={() => setActiveReport('accounts')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors whitespace-nowrap ${
              activeReport === 'accounts'
                ? 'bg-indigo-600 text-white'
                : 'bg-background hover:bg-muted'
            }`}
          >
            🏦 Contas
          </button>
        </div>

        {/* Conteúdo dos Relatórios */}
        {loading ? (
          <div className="glass rounded-xl p-12 text-center">
            <p className="text-muted-foreground">Carregando relatório...</p>
          </div>
        ) : (
          <>
            {activeReport === 'executive' && executiveData && (
              <ExecutiveReport data={executiveData} />
            )}
            {activeReport === 'income' && incomeData && (
              <IncomeReport data={incomeData} />
            )}
            {activeReport === 'expense' && expenseData && (
              <ExpenseReport data={expenseData} />
            )}
            {activeReport === 'categories' && categoriesData && (
              <CategoriesReport data={categoriesData} />
            )}
            {activeReport === 'planning' && planningData && (
              <PlanningReport data={planningData} />
            )}
            {activeReport === 'comparative' && comparativeData && (
              <ComparativeReport data={comparativeData} />
            )}
            {activeReport === 'trends' && trendsData && (
              <TrendsReport data={trendsData} />
            )}
            {activeReport === 'goals' && goalsData && (
              <GoalsReport data={goalsData} />
            )}
            {activeReport === 'temporal' && temporalData && (
              <TemporalReport data={temporalData} />
            )}
            {activeReport === 'accounts' && accountsData && (
              <AccountsReport data={accountsData} />
            )}
          </>
        )}
      </div>
    </div>
  )
}

// Componente: Relatório Executivo
function ExecutiveReport({ data }: { data: any }) {
  return (
    <div className="space-y-6">
      {/* KPIs */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="glass rounded-xl p-4">
          <p className="text-sm text-muted-foreground mb-1">Receita Total</p>
          <p className="text-2xl font-bold text-green-400">
            {new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(data.kpis.total_income)}
          </p>
        </div>
        <div className="glass rounded-xl p-4">
          <p className="text-sm text-muted-foreground mb-1">Despesa Total</p>
          <p className="text-2xl font-bold text-red-400">
            {new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(data.kpis.total_expense)}
          </p>
        </div>
        <div className="glass rounded-xl p-4">
          <p className="text-sm text-muted-foreground mb-1">Saldo</p>
          <p className={`text-2xl font-bold ${data.kpis.balance >= 0 ? 'text-green-400' : 'text-red-400'}`}>
            {new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(data.kpis.balance)}
          </p>
        </div>
        <div className="glass rounded-xl p-4">
          <p className="text-sm text-muted-foreground mb-1">Taxa de Economia</p>
          <p className="text-2xl font-bold text-indigo-400">
            {data.kpis.savings_rate.toFixed(1)}%
          </p>
        </div>
      </div>

      {/* Evolução de Saldo */}
      <div className="glass rounded-xl p-6">
        <h2 className="text-xl font-bold mb-4">Evolução de Saldo (Últimos 6 Meses)</h2>
        <ResponsiveContainer width="100%" height={300}>
          <AreaChart data={data.balance_evolution}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis dataKey="month" stroke="#9ca3af" />
            <YAxis stroke="#9ca3af" />
            <Tooltip 
              contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: '8px' }}
              formatter={(value: any) => new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value)}
            />
            <Legend />
            <Area type="monotone" dataKey="income" stackId="1" stroke="#10b981" fill="#10b981" fillOpacity={0.6} name="Receitas" />
            <Area type="monotone" dataKey="expense" stackId="1" stroke="#ef4444" fill="#ef4444" fillOpacity={0.6} name="Despesas" />
            <Line type="monotone" dataKey="balance" stroke="#3b82f6" strokeWidth={2} name="Saldo" />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}

// Componente: Relatório de Receitas
function IncomeReport({ data }: { data: any }) {
  return (
    <div className="space-y-6">
      {/* Resumo */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="glass rounded-xl p-4">
          <p className="text-sm text-muted-foreground mb-1">Receita Total</p>
          <p className="text-2xl font-bold text-green-400">
            {new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(data.total_income)}
          </p>
        </div>
        <div className="glass rounded-xl p-4">
          <p className="text-sm text-muted-foreground mb-1">Transações</p>
          <p className="text-2xl font-bold">{data.transactions_count}</p>
        </div>
      </div>

      {/* Por Categoria */}
      <div className="glass rounded-xl p-6">
        <h2 className="text-xl font-bold mb-4">Receitas por Categoria</h2>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={data.by_category}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percentage }) => `${name}: ${percentage.toFixed(1)}%`}
                outerRadius={100}
                fill="#8884d8"
                dataKey="amount"
              >
                {data.by_category.map((entry: any, index: number) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip 
                contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: '8px' }}
                formatter={(value: any) => new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value)}
              />
            </PieChart>
          </ResponsiveContainer>
          <div className="space-y-2">
            {data.by_category.map((item: any, index: number) => (
              <div key={index} className="flex items-center justify-between p-3 bg-background/50 rounded-lg">
                <div className="flex items-center gap-3">
                  <div className="w-4 h-4 rounded-full" style={{ backgroundColor: COLORS[index % COLORS.length] }} />
                  <span className="font-medium">{item.category}</span>
                </div>
                <div className="text-right">
                  <p className="font-bold">{new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(item.amount)}</p>
                  <p className="text-xs text-muted-foreground">{item.percentage.toFixed(1)}%</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Evolução Mensal */}
      <div className="glass rounded-xl p-6">
        <h2 className="text-xl font-bold mb-4">Evolução Mensal</h2>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={data.monthly_evolution}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis dataKey="month" stroke="#9ca3af" />
            <YAxis stroke="#9ca3af" />
            <Tooltip 
              contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: '8px' }}
              formatter={(value: any) => new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value)}
            />
            <Line type="monotone" dataKey="amount" stroke="#10b981" strokeWidth={2} name="Receitas" />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}

// Componente: Relatório de Despesas
function ExpenseReport({ data }: { data: any }) {
  return (
    <div className="space-y-6">
      {/* Resumo */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="glass rounded-xl p-4">
          <p className="text-sm text-muted-foreground mb-1">Despesa Total</p>
          <p className="text-2xl font-bold text-red-400">
            {new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(data.total_expense)}
          </p>
        </div>
        <div className="glass rounded-xl p-4">
          <p className="text-sm text-muted-foreground mb-1">Transações</p>
          <p className="text-2xl font-bold">{data.transactions_count}</p>
        </div>
      </div>

      {/* Insights */}
      {data.insights && data.insights.length > 0 && (
        <div className="glass rounded-xl p-4 bg-yellow-500/10 border border-yellow-500/30">
          <h3 className="font-semibold mb-2 text-yellow-400">💡 Insights</h3>
          <ul className="space-y-1">
            {data.insights.map((insight: any, index: number) => (
              <li key={index} className="text-sm">{insight.message}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Top Categorias */}
      <div className="glass rounded-xl p-6">
        <h2 className="text-xl font-bold mb-4">Top 10 Categorias de Gastos</h2>
        <ResponsiveContainer width="100%" height={400}>
          <BarChart data={data.top_categories} layout="vertical">
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis type="number" stroke="#9ca3af" />
            <YAxis dataKey="category" type="category" stroke="#9ca3af" width={120} />
            <Tooltip 
              contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: '8px' }}
              formatter={(value: any) => new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value)}
            />
            <Bar dataKey="amount" fill="#ef4444" name="Despesas" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Evolução Mensal */}
      <div className="glass rounded-xl p-6">
        <h2 className="text-xl font-bold mb-4">Evolução Mensal</h2>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={data.monthly_evolution}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis dataKey="month" stroke="#9ca3af" />
            <YAxis stroke="#9ca3af" />
            <Tooltip 
              contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: '8px' }}
              formatter={(value: any) => new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value)}
            />
            <Line type="monotone" dataKey="amount" stroke="#ef4444" strokeWidth={2} name="Despesas" />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}

// Componente: Relatório de Categorias
function CategoriesReport({ data }: { data: any }) {
  return (
    <div className="space-y-6">
      {/* Resumo */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="glass rounded-xl p-4">
          <p className="text-sm text-muted-foreground mb-1">Total de Categorias</p>
          <p className="text-2xl font-bold">{data.total_categories}</p>
        </div>
        <div className="glass rounded-xl p-4">
          <p className="text-sm text-muted-foreground mb-1">Receita Total</p>
          <p className="text-2xl font-bold text-green-400">
            {new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(data.total_income)}
          </p>
        </div>
        <div className="glass rounded-xl p-4">
          <p className="text-sm text-muted-foreground mb-1">Despesa Total</p>
          <p className="text-2xl font-bold text-red-400">
            {new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(data.total_expense)}
          </p>
        </div>
      </div>

      {/* Tabela de Categorias */}
      <div className="glass rounded-xl p-6">
        <h2 className="text-xl font-bold mb-4">Análise por Categoria</h2>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-border">
                <th className="text-left p-3 font-semibold">Categoria</th>
                <th className="text-right p-3 font-semibold">Receitas</th>
                <th className="text-right p-3 font-semibold">Despesas</th>
                <th className="text-right p-3 font-semibold">Saldo</th>
                <th className="text-right p-3 font-semibold">Transações</th>
              </tr>
            </thead>
            <tbody>
              {data.categories.map((cat: any, index: number) => (
                <tr key={index} className="border-b border-border/50 hover:bg-background/50">
                  <td className="p-3 font-medium">{cat.category}</td>
                  <td className="p-3 text-right text-green-400">
                    {new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(cat.income)}
                  </td>
                  <td className="p-3 text-right text-red-400">
                    {new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(cat.expense)}
                  </td>
                  <td className={`p-3 text-right font-bold ${cat.net >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                    {new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(cat.net)}
                  </td>
                  <td className="p-3 text-right text-muted-foreground">{cat.transactions_count}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

// Componente: Relatório de Planejamento vs Real
function PlanningReport({ data }: { data: any }) {
  return (
    <div className="space-y-6">
      <div className="glass rounded-xl p-6">
        <h2 className="text-xl font-bold mb-4">Planejamento vs Real</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h3 className="font-semibold mb-3">Receitas</h3>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Planejado:</span>
                <span className="font-medium">{new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(data.planned.income)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Real:</span>
                <span className="font-medium text-green-400">{new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(data.real.income)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Variação:</span>
                <span className={`font-bold ${data.variance.income >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                  {new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(data.variance.income)}
                </span>
              </div>
            </div>
          </div>
          <div>
            <h3 className="font-semibold mb-3">Despesas</h3>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Planejado:</span>
                <span className="font-medium">{new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(data.planned.expense)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Real:</span>
                <span className="font-medium text-red-400">{new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(data.real.expense)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Variação:</span>
                <span className={`font-bold ${data.variance.expense <= 0 ? 'text-green-400' : 'text-red-400'}`}>
                  {new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(data.variance.expense)}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

// Componente: Relatório Comparativo
function ComparativeReport({ data }: { data: any }) {
  const comparisonData = [
    {
      name: 'Receitas',
      atual: data.current_period.income,
      anterior: data.previous_period.income,
      variacao: data.variance.income,
      variacaoPercent: data.variance.income_percentage,
    },
    {
      name: 'Despesas',
      atual: data.current_period.expense,
      anterior: data.previous_period.expense,
      variacao: data.variance.expense,
      variacaoPercent: data.variance.expense_percentage,
    },
    {
      name: 'Saldo',
      atual: data.current_period.balance,
      anterior: data.previous_period.balance,
      variacao: data.variance.balance,
      variacaoPercent: 0,
    },
  ]

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="glass rounded-xl p-4">
          <p className="text-sm text-muted-foreground mb-1">Período Atual</p>
          <p className="text-lg font-bold">
            {new Date(data.current_period.start_date).toLocaleDateString('pt-BR')} - {new Date(data.current_period.end_date).toLocaleDateString('pt-BR')}
          </p>
        </div>
        <div className="glass rounded-xl p-4">
          <p className="text-sm text-muted-foreground mb-1">Período Anterior</p>
          <p className="text-lg font-bold">
            {new Date(data.previous_period.start_date).toLocaleDateString('pt-BR')} - {new Date(data.previous_period.end_date).toLocaleDateString('pt-BR')}
          </p>
        </div>
      </div>

      <div className="glass rounded-xl p-6">
        <h2 className="text-xl font-bold mb-4">Comparação</h2>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={comparisonData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis dataKey="name" stroke="#9ca3af" />
            <YAxis stroke="#9ca3af" />
            <Tooltip 
              contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: '8px' }}
              formatter={(value: any) => new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value)}
            />
            <Legend />
            <Bar dataKey="atual" fill="#3b82f6" name="Período Atual" />
            <Bar dataKey="anterior" fill="#6b7280" name="Período Anterior" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="glass rounded-xl p-6">
        <h2 className="text-xl font-bold mb-4">Variações</h2>
        <div className="space-y-3">
          {comparisonData.map((item, index) => (
            <div key={index} className="flex items-center justify-between p-3 bg-background/50 rounded-lg">
              <span className="font-medium">{item.name}</span>
              <div className="text-right">
                <p className={`font-bold ${item.variacao >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                  {item.variacao >= 0 ? '+' : ''}{new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(item.variacao)}
                </p>
                {item.variacaoPercent !== 0 && (
                  <p className="text-xs text-muted-foreground">
                    {item.variacaoPercent >= 0 ? '+' : ''}{item.variacaoPercent.toFixed(1)}%
                  </p>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

// Componente: Relatório de Tendências
function TrendsReport({ data }: { data: any }) {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="glass rounded-xl p-4">
          <p className="text-sm text-muted-foreground mb-1">Tendência de Receitas</p>
          <p className={`text-2xl font-bold ${data.income_trend >= 0 ? 'text-green-400' : 'text-red-400'}`}>
            {data.income_trend >= 0 ? '+' : ''}{data.income_trend.toFixed(1)}%
          </p>
        </div>
        <div className="glass rounded-xl p-4">
          <p className="text-sm text-muted-foreground mb-1">Tendência de Despesas</p>
          <p className={`text-2xl font-bold ${data.expense_trend <= 0 ? 'text-green-400' : 'text-red-400'}`}>
            {data.expense_trend >= 0 ? '+' : ''}{data.expense_trend.toFixed(1)}%
          </p>
        </div>
      </div>

      <div className="glass rounded-xl p-6">
        <h2 className="text-xl font-bold mb-4">Evolução Mensal</h2>
        <ResponsiveContainer width="100%" height={400}>
          <AreaChart data={data.trends}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis dataKey="month" stroke="#9ca3af" />
            <YAxis stroke="#9ca3af" />
            <Tooltip 
              contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: '8px' }}
              formatter={(value: any) => new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value)}
            />
            <Legend />
            <Area type="monotone" dataKey="income" stackId="1" stroke="#10b981" fill="#10b981" fillOpacity={0.6} name="Receitas" />
            <Area type="monotone" dataKey="expense" stackId="1" stroke="#ef4444" fill="#ef4444" fillOpacity={0.6} name="Despesas" />
            <Line type="monotone" dataKey="balance" stroke="#3b82f6" strokeWidth={2} name="Saldo" />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}

// Componente: Relatório de Metas
function GoalsReport({ data }: { data: any }) {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="glass rounded-xl p-4">
          <p className="text-sm text-muted-foreground mb-1">Total de Metas</p>
          <p className="text-2xl font-bold">{data.summary.total_goals}</p>
        </div>
        <div className="glass rounded-xl p-4">
          <p className="text-sm text-muted-foreground mb-1">Valor Total</p>
          <p className="text-2xl font-bold">
            {new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(data.summary.total_target)}
          </p>
        </div>
        <div className="glass rounded-xl p-4">
          <p className="text-sm text-muted-foreground mb-1">Economizado</p>
          <p className="text-2xl font-bold text-green-400">
            {new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(data.summary.total_current)}
          </p>
        </div>
        <div className="glass rounded-xl p-4">
          <p className="text-sm text-muted-foreground mb-1">Progresso Geral</p>
          <p className="text-2xl font-bold text-indigo-400">
            {data.summary.total_progress.toFixed(1)}%
          </p>
        </div>
      </div>

      <div className="glass rounded-xl p-6">
        <h2 className="text-xl font-bold mb-4">Metas</h2>
        <div className="space-y-4">
          {data.goals.map((goal: any, index: number) => (
            <div key={index} className="p-4 bg-background/50 rounded-lg">
              <div className="flex items-center justify-between mb-2">
                <h3 className="font-semibold">{goal.name}</h3>
                <span className="text-sm text-muted-foreground">{goal.progress.toFixed(1)}%</span>
              </div>
              <div className="w-full bg-background rounded-full h-3 mb-2">
                <div
                  className="bg-indigo-600 h-3 rounded-full transition-all"
                  style={{ width: `${Math.min(goal.progress, 100)}%` }}
                />
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">
                  {new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(goal.current_amount)} / {new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(goal.target_amount)}
                </span>
                {goal.days_remaining !== null && (
                  <span className="text-muted-foreground">
                    {goal.days_remaining > 0 ? `${goal.days_remaining} dias restantes` : 'Vencida'}
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

// Componente: Relatório Temporal
function TemporalReport({ data }: { data: any }) {
  return (
    <div className="space-y-6">
      <div className="glass rounded-xl p-6">
        <h2 className="text-xl font-bold mb-4">Gastos por Dia da Semana</h2>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={data.by_weekday}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis dataKey="day" stroke="#9ca3af" />
            <YAxis stroke="#9ca3af" />
            <Tooltip 
              contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: '8px' }}
              formatter={(value: any) => new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value)}
            />
            <Bar dataKey="amount" fill="#ef4444" name="Gastos" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="glass rounded-xl p-6">
        <h2 className="text-xl font-bold mb-4">Gastos por Dia do Mês</h2>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={data.by_day}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis dataKey="day" stroke="#9ca3af" />
            <YAxis stroke="#9ca3af" />
            <Tooltip 
              contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: '8px' }}
              formatter={(value: any) => new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value)}
            />
            <Bar dataKey="amount" fill="#f59e0b" name="Gastos" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}

// Componente: Relatório de Contas
function AccountsReport({ data }: { data: any }) {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="glass rounded-xl p-4">
          <p className="text-sm text-muted-foreground mb-1">Total de Contas</p>
          <p className="text-2xl font-bold">{data.total_accounts}</p>
        </div>
        <div className="glass rounded-xl p-4">
          <p className="text-sm text-muted-foreground mb-1">Saldo Total</p>
          <p className="text-2xl font-bold text-green-400">
            {new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(data.total_balance)}
          </p>
        </div>
      </div>

      <div className="glass rounded-xl p-6">
        <h2 className="text-xl font-bold mb-4">Análise por Conta</h2>
        <div className="space-y-4">
          {data.accounts.map((account: any, index: number) => (
            <div key={index} className="p-4 bg-background/50 rounded-lg">
              <div className="flex items-center justify-between mb-3">
                <div>
                  <h3 className="font-semibold">{account.name}</h3>
                  <p className="text-sm text-muted-foreground">{account.type}</p>
                </div>
                <div className="text-right">
                  <p className="text-lg font-bold text-green-400">
                    {new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(account.balance)}
                  </p>
                  <p className="text-xs text-muted-foreground">Saldo atual</p>
                </div>
              </div>
              <div className="grid grid-cols-3 gap-4 mt-3">
                <div>
                  <p className="text-xs text-muted-foreground">Receitas</p>
                  <p className="text-sm font-medium text-green-400">
                    {new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(account.income)}
                  </p>
                </div>
                <div>
                  <p className="text-xs text-muted-foreground">Despesas</p>
                  <p className="text-sm font-medium text-red-400">
                    {new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(account.expense)}
                  </p>
                </div>
                <div>
                  <p className="text-xs text-muted-foreground">Transações</p>
                  <p className="text-sm font-medium">{account.transactions_count}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
