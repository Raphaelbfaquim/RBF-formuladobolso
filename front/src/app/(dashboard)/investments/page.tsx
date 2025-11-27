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

type TabType = 'dashboard' | 'accounts' | 'transactions' | 'performance' | 'diversification' | 'simulator' | 'taxes'

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#06b6d4', '#84cc16']

const ACCOUNT_TYPE_LABELS: Record<string, string> = {
  stock_broker: 'Corretora',
  bank: 'Banco',
  crypto_exchange: 'Exchange',
  investment_platform: 'Plataforma',
  other: 'Outros'
}

const INVESTMENT_TYPE_LABELS: Record<string, string> = {
  stock: 'Ações',
  bond: 'Títulos',
  fund: 'Fundos',
  crypto: 'Criptomoedas',
  fixed_income: 'Renda Fixa',
  real_estate: 'Imóveis',
  other: 'Outros'
}

const TRANSACTION_TYPE_LABELS: Record<string, string> = {
  buy: 'Compra',
  sell: 'Venda',
  dividend: 'Dividendo',
  interest: 'Juros',
  fee: 'Taxa',
  transfer: 'Transferência'
}

export default function InvestmentsPage() {
  const router = useRouter()
  const [activeTab, setActiveTab] = useState<TabType>('dashboard')
  const [loading, setLoading] = useState(false)

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-3xl font-bold mb-2">💰 Investimentos</h1>
          <p className="text-muted-foreground">Gerencie e acompanhe seus investimentos</p>
        </div>

        {/* Tabs */}
        <div className="flex gap-2 mb-6 overflow-x-auto">
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
            onClick={() => setActiveTab('accounts')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors whitespace-nowrap ${
              activeTab === 'accounts'
                ? 'bg-indigo-600 text-white'
                : 'bg-background hover:bg-muted'
            }`}
          >
            🏦 Contas
          </button>
          <button
            onClick={() => setActiveTab('transactions')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors whitespace-nowrap ${
              activeTab === 'transactions'
                ? 'bg-indigo-600 text-white'
                : 'bg-background hover:bg-muted'
            }`}
          >
            📝 Transações
          </button>
          <button
            onClick={() => setActiveTab('performance')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors whitespace-nowrap ${
              activeTab === 'performance'
                ? 'bg-indigo-600 text-white'
                : 'bg-background hover:bg-muted'
            }`}
          >
            📈 Performance
          </button>
          <button
            onClick={() => setActiveTab('diversification')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors whitespace-nowrap ${
              activeTab === 'diversification'
                ? 'bg-indigo-600 text-white'
                : 'bg-background hover:bg-muted'
            }`}
          >
            🎯 Diversificação
          </button>
          <button
            onClick={() => setActiveTab('simulator')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors whitespace-nowrap ${
              activeTab === 'simulator'
                ? 'bg-indigo-600 text-white'
                : 'bg-background hover:bg-muted'
            }`}
          >
            🔮 Simulador
          </button>
          <button
            onClick={() => setActiveTab('taxes')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors whitespace-nowrap ${
              activeTab === 'taxes'
                ? 'bg-indigo-600 text-white'
                : 'bg-background hover:bg-muted'
            }`}
          >
            📋 IRPF
          </button>
        </div>

        {/* Content */}
        {activeTab === 'dashboard' && <DashboardTab />}
        {activeTab === 'accounts' && <AccountsTab />}
        {activeTab === 'transactions' && <TransactionsTab />}
        {activeTab === 'performance' && <PerformanceTab />}
        {activeTab === 'diversification' && <DiversificationTab />}
        {activeTab === 'simulator' && <SimulatorTab />}
        {activeTab === 'taxes' && <TaxesTab />}
      </div>
    </div>
  )
}

// ========== Dashboard Tab ==========
function DashboardTab() {
  const [loading, setLoading] = useState(true)
  const [summary, setSummary] = useState<any>(null)

  useEffect(() => {
    loadSummary()
  }, [])

  const loadSummary = async () => {
    setLoading(true)
    try {
      const response = await apiClient.get('/investments/summary')
      setSummary(response.data)
    } catch (error: any) {
      toast.error('Erro ao carregar resumo')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="glass rounded-xl p-12 text-center">Carregando...</div>
  }

  if (!summary) {
    return <div className="glass rounded-xl p-12 text-center">Nenhum dado disponível</div>
  }

  return (
    <div className="space-y-6">
      {/* KPIs */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="glass rounded-xl p-4">
          <p className="text-sm text-muted-foreground mb-1">Total Investido</p>
          <p className="text-2xl font-bold">
            {new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(summary.total_invested)}
          </p>
        </div>
        <div className="glass rounded-xl p-4">
          <p className="text-sm text-muted-foreground mb-1">Valor Atual</p>
          <p className="text-2xl font-bold text-green-400">
            {new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(summary.current_value)}
          </p>
        </div>
        <div className="glass rounded-xl p-4">
          <p className="text-sm text-muted-foreground mb-1">Ganho/Perda Total</p>
          <p className={`text-2xl font-bold ${summary.total_return >= 0 ? 'text-green-400' : 'text-red-400'}`}>
            {summary.total_return >= 0 ? '+' : ''}{new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(summary.total_return)}
          </p>
        </div>
        <div className="glass rounded-xl p-4">
          <p className="text-sm text-muted-foreground mb-1">Rentabilidade</p>
          <p className={`text-2xl font-bold ${summary.return_percentage >= 0 ? 'text-green-400' : 'text-red-400'}`}>
            {summary.return_percentage >= 0 ? '+' : ''}{summary.return_percentage.toFixed(2)}%
          </p>
        </div>
      </div>

      {/* Variações */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="glass rounded-xl p-4">
          <p className="text-sm text-muted-foreground mb-1">Variação do Dia</p>
          <p className={`text-xl font-bold ${summary.day_variation >= 0 ? 'text-green-400' : 'text-red-400'}`}>
            {summary.day_variation >= 0 ? '+' : ''}{new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(summary.day_variation)}
          </p>
          <p className="text-xs text-muted-foreground">{summary.day_variation_percentage.toFixed(2)}%</p>
        </div>
        <div className="glass rounded-xl p-4">
          <p className="text-sm text-muted-foreground mb-1">Variação do Mês</p>
          <p className={`text-xl font-bold ${summary.month_variation >= 0 ? 'text-green-400' : 'text-red-400'}`}>
            {summary.month_variation >= 0 ? '+' : ''}{new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(summary.month_variation)}
          </p>
          <p className="text-xs text-muted-foreground">{summary.month_variation_percentage.toFixed(2)}%</p>
        </div>
        <div className="glass rounded-xl p-4">
          <p className="text-sm text-muted-foreground mb-1">Variação do Ano</p>
          <p className={`text-xl font-bold ${summary.year_variation >= 0 ? 'text-green-400' : 'text-red-400'}`}>
            {summary.year_variation >= 0 ? '+' : ''}{new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(summary.year_variation)}
          </p>
          <p className="text-xs text-muted-foreground">{summary.year_variation_percentage.toFixed(2)}%</p>
        </div>
      </div>

      {/* Distribuição por Tipo */}
      {summary.distribution_by_type && Object.keys(summary.distribution_by_type).length > 0 && (
        <div className="glass rounded-xl p-6">
          <h2 className="text-xl font-bold mb-4">Distribuição por Tipo</h2>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={Object.entries(summary.distribution_by_type).map(([name, value]) => ({
                  name: INVESTMENT_TYPE_LABELS[name] || name,
                  value
                }))}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(1)}%`}
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
              >
                {Object.keys(summary.distribution_by_type).map((_, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: '8px' }}
                formatter={(value: any) => new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value)}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  )
}

// ========== Accounts Tab ==========
function AccountsTab() {
  const router = useRouter()
  const [loading, setLoading] = useState(true)
  const [accounts, setAccounts] = useState<any[]>([])

  useEffect(() => {
    loadAccounts()
  }, [])

  const loadAccounts = async () => {
    setLoading(true)
    try {
      const response = await apiClient.get('/investments/accounts')
      setAccounts(response.data)
    } catch (error: any) {
      toast.error('Erro ao carregar contas')
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (id: string) => {
    if (!confirm('Tem certeza que deseja excluir esta conta?')) return

    try {
      await apiClient.delete(`/investments/accounts/${id}`)
      toast.success('Conta excluída com sucesso!')
      loadAccounts()
    } catch (error: any) {
      toast.error('Erro ao excluir conta')
    }
  }

  if (loading) {
    return <div className="glass rounded-xl p-12 text-center">Carregando...</div>
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">Contas de Investimento</h2>
        <button
          onClick={() => router.push('/investments/accounts/new')}
          className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 font-medium"
        >
          + Nova Conta
        </button>
      </div>

      {accounts.length === 0 ? (
        <div className="glass rounded-xl p-12 text-center">
          <p className="text-muted-foreground mb-4">Nenhuma conta cadastrada</p>
          <button
            onClick={() => router.push('/investments/accounts/new')}
            className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
          >
            Criar Primeira Conta
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {accounts.map((account) => (
            <div key={account.id} className="glass rounded-xl p-4">
              <div className="flex items-center justify-between mb-3">
                <h3 className="font-semibold">{account.name}</h3>
                {!account.is_active && (
                  <span className="text-xs px-2 py-1 bg-gray-500/20 text-gray-400 rounded">Inativa</span>
                )}
              </div>
              <p className="text-sm text-muted-foreground mb-2">
                {ACCOUNT_TYPE_LABELS[account.account_type] || account.account_type}
              </p>
              {account.institution_name && (
                <p className="text-xs text-muted-foreground mb-2">{account.institution_name}</p>
              )}
              <p className="text-2xl font-bold text-green-400 mb-4">
                {new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(account.current_balance)}
              </p>
              <div className="flex gap-2">
                <button
                  onClick={() => router.push(`/investments/accounts/${account.id}/edit`)}
                  className="flex-1 px-3 py-2 bg-background hover:bg-muted rounded-lg text-sm"
                >
                  Editar
                </button>
                <button
                  onClick={() => handleDelete(account.id)}
                  className="flex-1 px-3 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg text-sm"
                >
                  Excluir
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

// ========== Transactions Tab ==========
function TransactionsTab() {
  const router = useRouter()
  const [loading, setLoading] = useState(true)
  const [transactions, setTransactions] = useState<any[]>([])
  const [accounts, setAccounts] = useState<any[]>([])

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    setLoading(true)
    try {
      const [transactionsRes, accountsRes] = await Promise.all([
        apiClient.get('/investments/transactions'),
        apiClient.get('/investments/accounts')
      ])
      setTransactions(transactionsRes.data)
      setAccounts(accountsRes.data)
    } catch (error: any) {
      toast.error('Erro ao carregar transações')
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (id: string) => {
    if (!confirm('Tem certeza que deseja excluir esta transação?')) return

    try {
      await apiClient.delete(`/investments/transactions/${id}`)
      toast.success('Transação excluída!')
      loadData()
    } catch (error: any) {
      toast.error('Erro ao excluir transação')
    }
  }

  if (loading) {
    return <div className="glass rounded-xl p-12 text-center">Carregando...</div>
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">Transações</h2>
        <button
          onClick={() => router.push('/investments/transactions/new')}
          className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 font-medium"
        >
          + Nova Transação
        </button>
      </div>

      {transactions.length === 0 ? (
        <div className="glass rounded-xl p-12 text-center">
          <p className="text-muted-foreground mb-4">Nenhuma transação cadastrada</p>
          <button
            onClick={() => router.push('/investments/transactions/new')}
            className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
          >
            Criar Primeira Transação
          </button>
        </div>
      ) : (
        <div className="glass rounded-xl overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-border">
                  <th className="text-left p-3 font-semibold">Data</th>
                  <th className="text-left p-3 font-semibold">Tipo</th>
                  <th className="text-left p-3 font-semibold">Investimento</th>
                  <th className="text-left p-3 font-semibold">Símbolo</th>
                  <th className="text-right p-3 font-semibold">Quantidade</th>
                  <th className="text-right p-3 font-semibold">Valor</th>
                  <th className="text-right p-3 font-semibold">Ações</th>
                </tr>
              </thead>
              <tbody>
                {transactions.map((transaction) => (
                  <tr key={transaction.id} className="border-b border-border/50 hover:bg-background/50">
                    <td className="p-3 text-sm">
                      {new Date(transaction.transaction_date).toLocaleDateString('pt-BR')}
                    </td>
                    <td className="p-3">
                      <span className={`px-2 py-1 rounded text-xs font-semibold ${
                        transaction.transaction_type === 'buy' ? 'bg-green-500/20 text-green-400' :
                        transaction.transaction_type === 'sell' ? 'bg-red-500/20 text-red-400' :
                        'bg-blue-500/20 text-blue-400'
                      }`}>
                        {TRANSACTION_TYPE_LABELS[transaction.transaction_type] || transaction.transaction_type}
                      </span>
                    </td>
                    <td className="p-3 text-sm">
                      {INVESTMENT_TYPE_LABELS[transaction.investment_type] || transaction.investment_type}
                    </td>
                    <td className="p-3 text-sm font-mono">{transaction.symbol || '-'}</td>
                    <td className="p-3 text-right text-sm">{parseFloat(transaction.quantity).toLocaleString('pt-BR')}</td>
                    <td className="p-3 text-right font-medium">
                      {new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(transaction.total_amount)}
                    </td>
                    <td className="p-3">
                      <div className="flex gap-2 justify-end">
                        <button
                          onClick={() => router.push(`/investments/transactions/${transaction.id}/edit`)}
                          className="px-2 py-1 bg-background hover:bg-muted rounded text-xs"
                        >
                          Editar
                        </button>
                        <button
                          onClick={() => handleDelete(transaction.id)}
                          className="px-2 py-1 bg-red-600 hover:bg-red-700 text-white rounded text-xs"
                        >
                          Excluir
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}

// ========== Performance Tab ==========
function PerformanceTab() {
  const [loading, setLoading] = useState(true)
  const [performance, setPerformance] = useState<any>(null)
  const [periodDays, setPeriodDays] = useState(365)

  useEffect(() => {
    loadPerformance()
  }, [periodDays])

  const loadPerformance = async () => {
    setLoading(true)
    try {
      const response = await apiClient.get(`/investments/performance?period_days=${periodDays}`)
      setPerformance(response.data)
    } catch (error: any) {
      toast.error('Erro ao carregar performance')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="glass rounded-xl p-12 text-center">Carregando...</div>
  }

  if (!performance) {
    return <div className="glass rounded-xl p-12 text-center">Nenhum dado disponível</div>
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <h2 className="text-2xl font-bold">Performance</h2>
        <select
          value={periodDays}
          onChange={(e) => setPeriodDays(parseInt(e.target.value))}
          className="px-3 py-2 bg-background border border-border rounded-lg"
        >
          <option value={30}>30 dias</option>
          <option value={90}>90 dias</option>
          <option value={180}>180 dias</option>
          <option value={365}>1 ano</option>
          <option value={730}>2 anos</option>
        </select>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="glass rounded-xl p-4">
          <p className="text-sm text-muted-foreground mb-1">Total Investido</p>
          <p className="text-2xl font-bold">
            {new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(performance.total_invested)}
          </p>
        </div>
        <div className="glass rounded-xl p-4">
          <p className="text-sm text-muted-foreground mb-1">Valor Atual</p>
          <p className="text-2xl font-bold text-green-400">
            {new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(performance.current_value)}
          </p>
        </div>
        <div className="glass rounded-xl p-4">
          <p className="text-sm text-muted-foreground mb-1">Retorno</p>
          <p className={`text-2xl font-bold ${performance.return_amount >= 0 ? 'text-green-400' : 'text-red-400'}`}>
            {performance.return_amount >= 0 ? '+' : ''}{new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(performance.return_amount)}
          </p>
        </div>
        <div className="glass rounded-xl p-4">
          <p className="text-sm text-muted-foreground mb-1">Rentabilidade</p>
          <p className={`text-2xl font-bold ${performance.return_percentage >= 0 ? 'text-green-400' : 'text-red-400'}`}>
            {performance.return_percentage >= 0 ? '+' : ''}{performance.return_percentage.toFixed(2)}%
          </p>
        </div>
      </div>
    </div>
  )
}

// ========== Diversification Tab ==========
function DiversificationTab() {
  const [loading, setLoading] = useState(true)
  const [diversification, setDiversification] = useState<any>(null)

  useEffect(() => {
    loadDiversification()
  }, [])

  const loadDiversification = async () => {
    setLoading(true)
    try {
      const response = await apiClient.get('/investments/diversification')
      setDiversification(response.data)
    } catch (error: any) {
      toast.error('Erro ao carregar diversificação')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="glass rounded-xl p-12 text-center">Carregando...</div>
  }

  if (!diversification) {
    return <div className="glass rounded-xl p-12 text-center">Nenhum dado disponível</div>
  }

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Diversificação</h2>

      {diversification.recommendations && diversification.recommendations.length > 0 && (
        <div className="glass rounded-xl p-4 bg-yellow-500/10 border border-yellow-500/30">
          <h3 className="font-semibold mb-2 text-yellow-400">💡 Recomendações</h3>
          <ul className="space-y-1">
            {diversification.recommendations.map((rec: string, index: number) => (
              <li key={index} className="text-sm">{rec}</li>
            ))}
          </ul>
        </div>
      )}

      {diversification.by_type && Object.keys(diversification.by_type).length > 0 && (
        <div className="glass rounded-xl p-6">
          <h3 className="text-lg font-bold mb-4">Por Tipo de Investimento</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={Object.entries(diversification.by_type).map(([name, value]) => ({
              name: INVESTMENT_TYPE_LABELS[name] || name,
              value
            }))}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="name" stroke="#9ca3af" />
              <YAxis stroke="#9ca3af" />
              <Tooltip
                contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: '8px' }}
                formatter={(value: any) => new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value)}
              />
              <Bar dataKey="value" fill="#3b82f6" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  )
}

// ========== Simulator Tab ==========
function SimulatorTab() {
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<any>(null)
  const [formData, setFormData] = useState({
    initial_amount: '',
    monthly_contribution: '',
    annual_rate: '',
    period_months: '12',
    inflation_rate: '0'
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    try {
      const response = await apiClient.post('/investments/simulator', {
        initial_amount: parseFloat(formData.initial_amount),
        monthly_contribution: parseFloat(formData.monthly_contribution) || 0,
        annual_rate: parseFloat(formData.annual_rate),
        period_months: parseInt(formData.period_months),
        inflation_rate: parseFloat(formData.inflation_rate) || 0
      })
      setResult(response.data)
    } catch (error: any) {
      toast.error('Erro ao simular investimento')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Simulador de Investimentos</h2>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="glass rounded-xl p-6">
          <h3 className="text-lg font-bold mb-4">Parâmetros</h3>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-1">Valor Inicial (R$)</label>
              <input
                type="number"
                step="0.01"
                min="0"
                value={formData.initial_amount}
                onChange={(e) => setFormData({ ...formData, initial_amount: e.target.value })}
                className="w-full px-3 py-2 bg-background border border-border rounded-lg"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Aporte Mensal (R$)</label>
              <input
                type="number"
                step="0.01"
                min="0"
                value={formData.monthly_contribution}
                onChange={(e) => setFormData({ ...formData, monthly_contribution: e.target.value })}
                className="w-full px-3 py-2 bg-background border border-border rounded-lg"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Taxa Anual (%)</label>
              <input
                type="number"
                step="0.01"
                min="0"
                max="100"
                value={formData.annual_rate}
                onChange={(e) => setFormData({ ...formData, annual_rate: e.target.value })}
                className="w-full px-3 py-2 bg-background border border-border rounded-lg"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Período (meses)</label>
              <input
                type="number"
                min="1"
                max="600"
                value={formData.period_months}
                onChange={(e) => setFormData({ ...formData, period_months: e.target.value })}
                className="w-full px-3 py-2 bg-background border border-border rounded-lg"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Inflação Anual (%)</label>
              <input
                type="number"
                step="0.01"
                min="0"
                max="100"
                value={formData.inflation_rate}
                onChange={(e) => setFormData({ ...formData, inflation_rate: e.target.value })}
                className="w-full px-3 py-2 bg-background border border-border rounded-lg"
              />
            </div>
            <button
              type="submit"
              disabled={loading}
              className="w-full px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 font-medium disabled:opacity-50"
            >
              {loading ? 'Simulando...' : 'Simular'}
            </button>
          </form>
        </div>

        {result && (
          <div className="glass rounded-xl p-6">
            <h3 className="text-lg font-bold mb-4">Resultado</h3>
            <div className="space-y-4">
              <div>
                <p className="text-sm text-muted-foreground">Total Contribuído</p>
                <p className="text-xl font-bold">
                  {new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(result.total_contributed)}
                </p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Valor Final</p>
                <p className="text-2xl font-bold text-green-400">
                  {new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(result.final_amount)}
                </p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Retorno Total</p>
                <p className={`text-xl font-bold ${result.total_return >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                  {result.total_return >= 0 ? '+' : ''}{new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(result.total_return)}
                </p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Rentabilidade</p>
                <p className={`text-xl font-bold ${result.return_percentage >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                  {result.return_percentage >= 0 ? '+' : ''}{result.return_percentage.toFixed(2)}%
                </p>
              </div>

              {result.monthly_breakdown && result.monthly_breakdown.length > 0 && (
                <div className="mt-6">
                  <h4 className="font-semibold mb-3">Evolução Mensal</h4>
                  <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={result.monthly_breakdown}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                      <XAxis dataKey="month" stroke="#9ca3af" />
                      <YAxis stroke="#9ca3af" />
                      <Tooltip
                        contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: '8px' }}
                        formatter={(value: any) => new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value)}
                      />
                      <Line type="monotone" dataKey="amount" stroke="#3b82f6" strokeWidth={2} name="Valor" />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

// ========== Taxes Tab ==========
function TaxesTab() {
  const [loading, setLoading] = useState(false)
  const [taxes, setTaxes] = useState<any>(null)
  const [startDate, setStartDate] = useState('')
  const [endDate, setEndDate] = useState('')

  useEffect(() => {
    const now = new Date()
    const yearStart = new Date(now.getFullYear(), 0, 1)
    const yearEnd = new Date(now.getFullYear(), 11, 31)
    setStartDate(yearStart.toISOString().split('T')[0])
    setEndDate(yearEnd.toISOString().split('T')[0])
  }, [])

  const loadTaxes = async () => {
    if (!startDate || !endDate) return

    setLoading(true)
    try {
      const start = new Date(startDate).toISOString()
      const end = new Date(endDate + 'T23:59:59').toISOString()
      const response = await apiClient.get(`/investments/taxes?start_date=${start}&end_date=${end}`)
      setTaxes(response.data)
    } catch (error: any) {
      toast.error('Erro ao calcular impostos')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Cálculo de IRPF</h2>

      <div className="glass rounded-xl p-6">
        <div className="flex gap-4 mb-4">
          <div className="flex-1">
            <label className="block text-sm font-medium mb-1">Data Inicial</label>
            <input
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              className="w-full px-3 py-2 bg-background border border-border rounded-lg"
            />
          </div>
          <div className="flex-1">
            <label className="block text-sm font-medium mb-1">Data Final</label>
            <input
              type="date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              className="w-full px-3 py-2 bg-background border border-border rounded-lg"
            />
          </div>
          <div className="flex items-end">
            <button
              onClick={loadTaxes}
              disabled={loading}
              className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 font-medium disabled:opacity-50"
            >
              {loading ? 'Calculando...' : 'Calcular'}
            </button>
          </div>
        </div>

        {taxes && (
          <div className="space-y-4 mt-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="p-4 bg-background/50 rounded-lg">
                <p className="text-sm text-muted-foreground mb-1">Ganho Total</p>
                <p className="text-xl font-bold">
                  {new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(taxes.total_gain)}
                </p>
              </div>
              <div className="p-4 bg-background/50 rounded-lg">
                <p className="text-sm text-muted-foreground mb-1">Valor Tributável</p>
                <p className="text-xl font-bold">
                  {new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(taxes.taxable_amount)}
                </p>
              </div>
              <div className="p-4 bg-background/50 rounded-lg">
                <p className="text-sm text-muted-foreground mb-1">Imposto Devido</p>
                <p className="text-xl font-bold text-red-400">
                  {new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(taxes.tax_amount)}
                </p>
              </div>
              <div className="p-4 bg-background/50 rounded-lg">
                <p className="text-sm text-muted-foreground mb-1">Alíquota</p>
                <p className="text-xl font-bold">{taxes.tax_rate.toFixed(2)}%</p>
              </div>
            </div>

            {taxes.transactions && taxes.transactions.length > 0 && (
              <div className="mt-6">
                <h4 className="font-semibold mb-3">Transações Tributáveis</h4>
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b border-border">
                        <th className="text-left p-3 font-semibold">Data</th>
                        <th className="text-left p-3 font-semibold">Símbolo</th>
                        <th className="text-right p-3 font-semibold">Valor</th>
                      </tr>
                    </thead>
                    <tbody>
                      {taxes.transactions.map((tx: any, index: number) => (
                        <tr key={index} className="border-b border-border/50">
                          <td className="p-3 text-sm">
                            {new Date(tx.date).toLocaleDateString('pt-BR')}
                          </td>
                          <td className="p-3 text-sm font-mono">{tx.symbol || '-'}</td>
                          <td className="p-3 text-right">
                            {new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(tx.amount)}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
