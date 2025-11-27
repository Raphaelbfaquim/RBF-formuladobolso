'use client'

import { useEffect, useState } from 'react'
import apiClient from '@/lib/api/client'
import toast from 'react-hot-toast'
import {
  BarChart, Bar, LineChart, Line, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  AreaChart, Area
} from 'recharts'

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#06b6d4', '#84cc16', '#f97316', '#6366f1']

const SEVERITY_COLORS: Record<string, string> = {
  info: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
  warning: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
  error: 'bg-red-500/20 text-red-400 border-red-500/30',
  success: 'bg-green-500/20 text-green-400 border-green-500/30',
}

type TabType = 'overview' | 'insights' | 'categories' | 'patterns' | 'trends' | 'recommendations'

export default function InsightsPage() {
  const [activeTab, setActiveTab] = useState<TabType>('overview')
  const [days, setDays] = useState(30)
  const [loading, setLoading] = useState(false)

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-3xl font-bold mb-2">💡 Insights</h1>
          <p className="text-muted-foreground">Análises inteligentes das suas finanças</p>
        </div>

        {/* Tabs */}
        <div className="flex gap-2 mb-6 overflow-x-auto">
          <button
            onClick={() => setActiveTab('overview')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors whitespace-nowrap ${
              activeTab === 'overview'
                ? 'bg-indigo-600 text-white'
                : 'bg-background hover:bg-muted'
            }`}
          >
            📊 Visão Geral
          </button>
          <button
            onClick={() => setActiveTab('insights')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors whitespace-nowrap ${
              activeTab === 'insights'
                ? 'bg-indigo-600 text-white'
                : 'bg-background hover:bg-muted'
            }`}
          >
            🔍 Insights Automáticos
          </button>
          <button
            onClick={() => setActiveTab('categories')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors whitespace-nowrap ${
              activeTab === 'categories'
                ? 'bg-indigo-600 text-white'
                : 'bg-background hover:bg-muted'
            }`}
          >
            📁 Categorias
          </button>
          <button
            onClick={() => setActiveTab('patterns')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors whitespace-nowrap ${
              activeTab === 'patterns'
                ? 'bg-indigo-600 text-white'
                : 'bg-background hover:bg-muted'
            }`}
          >
            📈 Padrões
          </button>
          <button
            onClick={() => setActiveTab('trends')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors whitespace-nowrap ${
              activeTab === 'trends'
                ? 'bg-indigo-600 text-white'
                : 'bg-background hover:bg-muted'
            }`}
          >
            📉 Tendências
          </button>
          <button
            onClick={() => setActiveTab('recommendations')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors whitespace-nowrap ${
              activeTab === 'recommendations'
                ? 'bg-indigo-600 text-white'
                : 'bg-background hover:bg-muted'
            }`}
          >
            💡 Recomendações
          </button>
        </div>

        {/* Period Selector */}
        <div className="mb-6 flex items-center gap-4">
          <label className="text-sm font-medium">Período:</label>
          <select
            value={days}
            onChange={(e) => setDays(parseInt(e.target.value))}
            className="px-3 py-2 bg-background border border-border rounded-lg"
          >
            <option value={7}>7 dias</option>
            <option value={30}>30 dias</option>
            <option value={60}>60 dias</option>
            <option value={90}>90 dias</option>
            <option value={180}>180 dias</option>
            <option value={365}>1 ano</option>
          </select>
        </div>

        {/* Content */}
        {activeTab === 'overview' && <OverviewTab days={days} />}
        {activeTab === 'insights' && <InsightsTab days={days} />}
        {activeTab === 'categories' && <CategoriesTab days={days} />}
        {activeTab === 'patterns' && <PatternsTab days={days} />}
        {activeTab === 'trends' && <TrendsTab days={days} />}
        {activeTab === 'recommendations' && <RecommendationsTab days={days} />}
      </div>
    </div>
  )
}

// ========== Overview Tab ==========
function OverviewTab({ days }: { days: number }) {
  const [loading, setLoading] = useState(true)
  const [summary, setSummary] = useState<any>(null)

  useEffect(() => {
    loadSummary()
  }, [days])

  const loadSummary = async () => {
    setLoading(true)
    try {
      const response = await apiClient.get(`/insights/summary?days=${days}`)
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
          <p className="text-sm text-muted-foreground mb-1">Receitas Totais</p>
          <p className="text-2xl font-bold text-green-400">
            {new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(summary.total_income)}
          </p>
        </div>
        <div className="glass rounded-xl p-4">
          <p className="text-sm text-muted-foreground mb-1">Despesas Totais</p>
          <p className="text-2xl font-bold text-red-400">
            {new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(summary.total_expenses)}
          </p>
        </div>
        <div className="glass rounded-xl p-4">
          <p className="text-sm text-muted-foreground mb-1">Economia</p>
          <p className={`text-2xl font-bold ${summary.savings >= 0 ? 'text-green-400' : 'text-red-400'}`}>
            {new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(summary.savings)}
          </p>
        </div>
        <div className="glass rounded-xl p-4">
          <p className="text-sm text-muted-foreground mb-1">Taxa de Economia</p>
          <p className={`text-2xl font-bold ${summary.savings_rate >= 20 ? 'text-green-400' : summary.savings_rate >= 10 ? 'text-yellow-400' : 'text-red-400'}`}>
            {summary.savings_rate.toFixed(1)}%
          </p>
        </div>
      </div>

      {/* Estatísticas Adicionais */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="glass rounded-xl p-4">
          <p className="text-sm text-muted-foreground mb-1">Média Diária de Receitas</p>
          <p className="text-xl font-bold">
            {new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(summary.avg_daily_income)}
          </p>
        </div>
        <div className="glass rounded-xl p-4">
          <p className="text-sm text-muted-foreground mb-1">Média Diária de Despesas</p>
          <p className="text-xl font-bold">
            {new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(summary.avg_daily_expense)}
          </p>
        </div>
        <div className="glass rounded-xl p-4">
          <p className="text-sm text-muted-foreground mb-1">Total de Transações</p>
          <p className="text-xl font-bold">{summary.total_transactions}</p>
        </div>
      </div>
    </div>
  )
}

// ========== Insights Tab ==========
function InsightsTab({ days }: { days: number }) {
  const [loading, setLoading] = useState(true)
  const [insights, setInsights] = useState<any[]>([])

  useEffect(() => {
    loadInsights()
  }, [days])

  const loadInsights = async () => {
    setLoading(true)
    try {
      const response = await apiClient.get(`/insights?days=${days}`)
      setInsights(response.data.insights || [])
    } catch (error: any) {
      toast.error('Erro ao carregar insights')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="glass rounded-xl p-12 text-center">Carregando...</div>
  }

  if (insights.length === 0) {
    return (
      <div className="glass rounded-xl p-12 text-center">
        <p className="text-muted-foreground">Nenhum insight disponível para este período</p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {insights.map((insight, index) => (
        <div
          key={index}
          className={`glass rounded-xl p-6 border ${SEVERITY_COLORS[insight.severity] || SEVERITY_COLORS.info}`}
        >
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <h3 className="font-bold text-lg mb-2">{insight.title}</h3>
              <p className="text-muted-foreground">{insight.message}</p>
              {insight.category && (
                <p className="text-sm mt-2">
                  <span className="font-medium">Categoria:</span> {insight.category}
                </p>
              )}
              {insight.amount && (
                <p className="text-sm mt-2">
                  <span className="font-medium">Valor:</span>{' '}
                  {new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(insight.amount)}
                </p>
              )}
            </div>
            <div className="ml-4">
              <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                insight.severity === 'warning' ? 'bg-yellow-500/20 text-yellow-400' :
                insight.severity === 'error' ? 'bg-red-500/20 text-red-400' :
                insight.severity === 'success' ? 'bg-green-500/20 text-green-400' :
                'bg-blue-500/20 text-blue-400'
              }`}>
                {insight.severity === 'warning' ? '⚠️ Atenção' :
                 insight.severity === 'error' ? '❌ Crítico' :
                 insight.severity === 'success' ? '✅ Positivo' :
                 'ℹ️ Informativo'}
              </span>
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}

// ========== Categories Tab ==========
function CategoriesTab({ days }: { days: number }) {
  const [loading, setLoading] = useState(true)
  const [analysis, setAnalysis] = useState<any>(null)

  useEffect(() => {
    loadAnalysis()
  }, [days])

  const loadAnalysis = async () => {
    setLoading(true)
    try {
      const response = await apiClient.get(`/insights/categories?days=${days}`)
      setAnalysis(response.data)
    } catch (error: any) {
      toast.error('Erro ao carregar análise de categorias')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="glass rounded-xl p-12 text-center">Carregando...</div>
  }

  if (!analysis || !analysis.categories || analysis.categories.length === 0) {
    return (
      <div className="glass rounded-xl p-12 text-center">
        <p className="text-muted-foreground">Nenhuma categoria encontrada</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Gráfico de Pizza */}
      <div className="glass rounded-xl p-6">
        <h3 className="text-lg font-bold mb-4">Distribuição por Categoria</h3>
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie
              data={analysis.categories.slice(0, 8).map((cat: any) => ({
                name: cat.name,
                value: cat.amount
              }))}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(1)}%`}
              outerRadius={100}
              fill="#8884d8"
              dataKey="value"
            >
              {analysis.categories.slice(0, 8).map((_: any, index: number) => (
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

      {/* Tabela de Categorias */}
      <div className="glass rounded-xl overflow-hidden">
        <div className="p-6">
          <h3 className="text-lg font-bold mb-4">Detalhes por Categoria</h3>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-border">
                  <th className="text-left p-3 font-semibold">Categoria</th>
                  <th className="text-right p-3 font-semibold">Total</th>
                  <th className="text-right p-3 font-semibold">Transações</th>
                  <th className="text-right p-3 font-semibold">Média</th>
                  <th className="text-right p-3 font-semibold">%</th>
                </tr>
              </thead>
              <tbody>
                {analysis.categories.map((cat: any, index: number) => (
                  <tr key={index} className="border-b border-border/50 hover:bg-background/50">
                    <td className="p-3 font-medium">{cat.name}</td>
                    <td className="p-3 text-right">
                      {new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(cat.amount)}
                    </td>
                    <td className="p-3 text-right">{cat.count}</td>
                    <td className="p-3 text-right">
                      {new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(cat.average)}
                    </td>
                    <td className="p-3 text-right">
                      <div className="flex items-center justify-end gap-2">
                        <div className="w-24 bg-background rounded-full h-2">
                          <div
                            className="h-2 rounded-full"
                            style={{
                              width: `${cat.percentage}%`,
                              backgroundColor: COLORS[index % COLORS.length]
                            }}
                          />
                        </div>
                        <span className="text-sm font-medium">{cat.percentage.toFixed(1)}%</span>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  )
}

// ========== Patterns Tab ==========
function PatternsTab({ days }: { days: number }) {
  const [loading, setLoading] = useState(true)
  const [patterns, setPatterns] = useState<any>(null)

  useEffect(() => {
    loadPatterns()
  }, [days])

  const loadPatterns = async () => {
    setLoading(true)
    try {
      const response = await apiClient.get(`/insights/patterns?days=${days}`)
      setPatterns(response.data)
    } catch (error: any) {
      toast.error('Erro ao carregar padrões')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="glass rounded-xl p-12 text-center">Carregando...</div>
  }

  if (!patterns) {
    return <div className="glass rounded-xl p-12 text-center">Nenhum dado disponível</div>
  }

  return (
    <div className="space-y-6">
      {/* Por Dia da Semana */}
      {patterns.by_weekday && (
        <div className="glass rounded-xl p-6">
          <h3 className="text-lg font-bold mb-4">Gastos por Dia da Semana</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={patterns.by_weekday}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="day" stroke="#9ca3af" />
              <YAxis stroke="#9ca3af" />
              <Tooltip
                contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: '8px' }}
                formatter={(value: any) => new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value)}
              />
              <Bar dataKey="amount" fill="#3b82f6" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Por Hora */}
      {patterns.by_hour && (
        <div className="glass rounded-xl p-6">
          <h3 className="text-lg font-bold mb-4">Gastos por Hora do Dia</h3>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={patterns.by_hour}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="hour" stroke="#9ca3af" />
              <YAxis stroke="#9ca3af" />
              <Tooltip
                contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: '8px' }}
                formatter={(value: any) => new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value)}
              />
              <Area type="monotone" dataKey="amount" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.3} />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  )
}

// ========== Trends Tab ==========
function TrendsTab({ days }: { days: number }) {
  const [loading, setLoading] = useState(true)
  const [trends, setTrends] = useState<any>(null)
  const [months, setMonths] = useState(6)

  useEffect(() => {
    loadTrends()
  }, [months])

  const loadTrends = async () => {
    setLoading(true)
    try {
      const response = await apiClient.get(`/insights/trends?months=${months}`)
      setTrends(response.data)
    } catch (error: any) {
      toast.error('Erro ao carregar tendências')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="glass rounded-xl p-12 text-center">Carregando...</div>
  }

  if (!trends) {
    return <div className="glass rounded-xl p-12 text-center">Nenhum dado disponível</div>
  }

  const trendData = trends.monthly_expenses.map((exp: any, index: number) => ({
    month: new Date(exp.month + '-01').toLocaleDateString('pt-BR', { month: 'short', year: 'numeric' }),
    expenses: exp.amount,
    income: trends.monthly_income[index]?.amount || 0,
  })).reverse()

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <label className="text-sm font-medium">Período:</label>
        <select
          value={months}
          onChange={(e) => setMonths(parseInt(e.target.value))}
          className="px-3 py-2 bg-background border border-border rounded-lg"
        >
          <option value={3}>3 meses</option>
          <option value={6}>6 meses</option>
          <option value={12}>12 meses</option>
        </select>
      </div>

      <div className="glass rounded-xl p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-bold">Tendência de Gastos e Receitas</h3>
          <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
            trends.trend === 'increasing' ? 'bg-red-500/20 text-red-400' :
            trends.trend === 'decreasing' ? 'bg-green-500/20 text-green-400' :
            'bg-blue-500/20 text-blue-400'
          }`}>
            {trends.trend === 'increasing' ? '📈 Aumentando' :
             trends.trend === 'decreasing' ? '📉 Diminuindo' :
             '➡️ Estável'}
          </span>
        </div>
        <ResponsiveContainer width="100%" height={400}>
          <LineChart data={trendData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis dataKey="month" stroke="#9ca3af" />
            <YAxis stroke="#9ca3af" />
            <Tooltip
              contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: '8px' }}
              formatter={(value: any) => new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value)}
            />
            <Legend />
            <Line type="monotone" dataKey="income" stroke="#10b981" strokeWidth={2} name="Receitas" />
            <Line type="monotone" dataKey="expenses" stroke="#ef4444" strokeWidth={2} name="Despesas" />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}

// ========== Recommendations Tab ==========
function RecommendationsTab({ days }: { days: number }) {
  const [loading, setLoading] = useState(true)
  const [recommendations, setRecommendations] = useState<any[]>([])

  useEffect(() => {
    loadRecommendations()
  }, [days])

  const loadRecommendations = async () => {
    setLoading(true)
    try {
      const response = await apiClient.get(`/insights/recommendations?days=${days}`)
      setRecommendations(response.data.recommendations || [])
    } catch (error: any) {
      toast.error('Erro ao carregar recomendações')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="glass rounded-xl p-12 text-center">Carregando...</div>
  }

  if (recommendations.length === 0) {
    return (
      <div className="glass rounded-xl p-12 text-center">
        <p className="text-muted-foreground">Nenhuma recomendação disponível</p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {recommendations.map((rec, index) => (
        <div
          key={index}
          className={`glass rounded-xl p-6 border ${SEVERITY_COLORS[rec.severity] || SEVERITY_COLORS.info}`}
        >
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <h3 className="font-bold text-lg mb-2">{rec.title}</h3>
              <p className="text-muted-foreground mb-3">{rec.message}</p>
              {rec.action && (
                <button className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 text-sm font-medium">
                  {rec.action}
                </button>
              )}
            </div>
            <div className="ml-4">
              <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                rec.severity === 'warning' ? 'bg-yellow-500/20 text-yellow-400' :
                rec.severity === 'error' ? 'bg-red-500/20 text-red-400' :
                'bg-blue-500/20 text-blue-400'
              }`}>
                {rec.severity === 'warning' ? '⚠️' : '💡'}
              </span>
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}
