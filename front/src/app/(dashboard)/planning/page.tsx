'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import apiClient from '@/lib/api/client'
import toast from 'react-hot-toast'

interface CategoryBudget {
  category_id: string
  category_name: string
  category_type: string
  budget_group: string | null
  target_amount: number
  actual_amount: number
  percentage: number
  remaining_amount: number
  is_over_budget: boolean
}

interface GoalSummary {
  id: string
  name: string
  icon: string | null
  target_amount: number
  current_amount: number
  remaining_amount: number
  percentage: number
  suggested_monthly_contribution: number | null
  is_below_target: boolean
  current_month_contribution: number
}

interface MonthlyBudgetSummary {
  month: number
  year: number
  total_income: number
  planned_income: number | null
  total_planned_expenses: number
  total_actual_expenses: number
  balance: number
  rule_50_30_20_enabled: boolean
  necessities: {
    planned: number
    actual: number
    percentage: number
    limit: number
  } | null
  wants: {
    planned: number
    actual: number
    percentage: number
    limit: number
  } | null
  savings: {
    planned: number
    actual: number
    percentage: number
    limit: number
  } | null
  category_budgets: CategoryBudget[]
  goals: GoalSummary[]
  total_goals_amount: number
  total_goals_current: number
  alerts: string[]
}

export default function PlanningPage() {
  const router = useRouter()
  const [loading, setLoading] = useState(true)
  const [data, setData] = useState<MonthlyBudgetSummary | null>(null)
  const [ruleEnabled, setRuleEnabled] = useState(false)
  const [currentMonth, setCurrentMonth] = useState(new Date().getMonth() + 1)
  const [currentYear, setCurrentYear] = useState(new Date().getFullYear())
  const [editingBudget, setEditingBudget] = useState<string | null>(null)
  const [newBudgetAmount, setNewBudgetAmount] = useState('')
  const [showRuleInfo, setShowRuleInfo] = useState(false)
  const [editingIncome, setEditingIncome] = useState(false)
  const [newIncomeAmount, setNewIncomeAmount] = useState('')

  useEffect(() => {
    loadBudgetSummary()
  }, [currentMonth, currentYear, ruleEnabled])

  const loadBudgetSummary = async () => {
    setLoading(true)
    try {
      const response = await apiClient.get('/monthly-budget/summary', {
        params: {
          month: currentMonth,
          year: currentYear,
          rule_50_30_20_enabled: ruleEnabled
        }
      })
      console.log('[DEBUG] Resposta da API:', response.data)
      console.log('[DEBUG] Total de categorias:', response.data?.category_budgets?.length)
      setData(response.data)
    } catch (error: any) {
      console.error('[DEBUG] Erro ao carregar:', error)
      if (error.response?.status === 401) {
        router.push('/login')
      } else {
        toast.error('Erro ao carregar planejamento')
      }
    } finally {
      setLoading(false)
    }
  }

  const handleUpdateBudget = async (categoryId: string, amount: number) => {
    try {
      await apiClient.post('/monthly-budget/category', {
        category_id: categoryId,
        target_amount: amount,
        month: currentMonth,
        year: currentYear
      })
      toast.success('Orçamento atualizado!')
      loadBudgetSummary()
      setEditingBudget(null)
      setNewBudgetAmount('')
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Erro ao atualizar orçamento')
    }
  }

  const handleUpdateBudgetGroup = async (categoryId: string, budgetGroup: string | null) => {
    try {
      await apiClient.put(`/monthly-budget/category/${categoryId}/budget-group`, {
        category_id: categoryId,
        budget_group: budgetGroup
      })
      toast.success('Grupo de orçamento atualizado!')
      loadBudgetSummary()
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Erro ao atualizar grupo')
    }
  }

  const handleUpdateIncome = async (amount: number) => {
    try {
      await apiClient.put('/monthly-budget/income', {
        month: currentMonth,
        year: currentYear,
        planned_income: amount
      })
      toast.success('Receita planejada atualizada!')
      loadBudgetSummary()
      setEditingIncome(false)
      setNewIncomeAmount('')
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Erro ao atualizar receita')
    }
  }

  const handleMonthChange = (offset: number) => {
    let newMonth = currentMonth + offset
    let newYear = currentYear
    
    if (newMonth > 12) {
      newMonth = 1
      newYear++
    } else if (newMonth < 1) {
      newMonth = 12
      newYear--
    }
    
    setCurrentMonth(newMonth)
    setCurrentYear(newYear)
  }

  const getStatusColor = (percentage: number, isOver: boolean) => {
    if (isOver) return 'text-red-400 bg-red-500/20 border-red-500/30'
    if (percentage >= 100) return 'text-yellow-400 bg-yellow-500/20 border-yellow-500/30'
    if (percentage >= 80) return 'text-orange-400 bg-orange-500/20 border-orange-500/30'
    return 'text-green-400 bg-green-500/20 border-green-500/30'
  }

  const getStatusIcon = (percentage: number, isOver: boolean) => {
    if (isOver) return '🔴'
    if (percentage >= 100) return '⚠️'
    if (percentage >= 80) return '⚡'
    return '✅'
  }

  const groupCategoriesByBudgetGroup = () => {
    if (!data) return { necessities: [], wants: [], savings: [], ungrouped: [] }
    
    const grouped = {
      necessities: [] as CategoryBudget[],
      wants: [] as CategoryBudget[],
      savings: [] as CategoryBudget[],
      ungrouped: [] as CategoryBudget[]
    }
    
    console.log('[DEBUG] Total de budgets recebidos:', data.category_budgets?.length)
    
    data.category_budgets.forEach(budget => {
      console.log('[DEBUG] Budget:', budget.category_name, 'group:', budget.budget_group)
      if (budget.budget_group === 'necessities') {
        grouped.necessities.push(budget)
      } else if (budget.budget_group === 'wants') {
        grouped.wants.push(budget)
      } else if (budget.budget_group === 'savings') {
        grouped.savings.push(budget)
      } else {
        grouped.ungrouped.push(budget)
      }
    })
    
    console.log('[DEBUG] Agrupado:', {
      necessities: grouped.necessities.length,
      wants: grouped.wants.length,
      savings: grouped.savings.length,
      ungrouped: grouped.ungrouped.length
    })
    
    return grouped
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-500 mx-auto"></div>
          <p className="mt-4 text-muted-foreground">Carregando planejamento...</p>
        </div>
      </div>
    )
  }

  if (!data) {
    return (
      <div className="min-h-screen bg-background p-6">
        <div className="max-w-7xl mx-auto">
          <p className="text-muted-foreground">Nenhum dado disponível</p>
        </div>
      </div>
    )
  }

  const grouped = groupCategoriesByBudgetGroup()
  const monthNames = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 
                      'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
  
  // Calcular quanto falta planejar no total
  const totalRemainingToPlan = Math.max(0, (data.planned_income || data.total_income) - data.total_planned_expenses)
  // Calcular quanto falta planejar por categoria (distribuído igualmente entre categorias sem orçamento)
  const categoriesWithoutBudget = data.category_budgets.filter(b => b.target_amount === 0).length
  const remainingPerCategory = categoriesWithoutBudget > 0 ? totalRemainingToPlan / categoriesWithoutBudget : 0
  
  // Função para obter quanto falta planejar para uma categoria específica
  const getRemainingToPlanForCategory = (categoryBudget: CategoryBudget) => {
    if (categoryBudget.target_amount > 0) {
      // Se já tem orçamento, não mostra quanto falta planejar
      return 0
    }
    // Se não tem orçamento, mostra a parte proporcional do que falta planejar
    return remainingPerCategory
  }

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold mb-2">Planejamento Financeiro</h1>
            <p className="text-muted-foreground">Gerencie seu orçamento mensal por categoria</p>
          </div>
          <div className="flex items-center gap-4">
            {/* Navegação de Mês */}
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
              <span className="px-4 py-2 text-sm font-medium">
                {monthNames[currentMonth - 1]} {currentYear}
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
          </div>
        </div>

        {/* Regra 50-30-20 */}
        <div className="mb-6 glass rounded-xl p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <input
                type="checkbox"
                id="rule_50_30_20"
                checked={ruleEnabled}
                onChange={(e) => {
                  const newValue = e.target.checked
                  setRuleEnabled(newValue)
                  if (newValue && !showRuleInfo) {
                    setShowRuleInfo(true)
                    toast.success('Regra 50-30-20 ativada! Configure as categorias nos grupos corretos.', {
                      duration: 5000,
                      icon: '💡'
                    })
                  }
                }}
                className="w-5 h-5 rounded border-border text-indigo-600 focus:ring-indigo-500"
              />
              <label htmlFor="rule_50_30_20" className="text-sm font-medium cursor-pointer">
                Ativar Regra 50-30-20
              </label>
              {ruleEnabled && (
                <button
                  onClick={() => setShowRuleInfo(!showRuleInfo)}
                  className="text-xs text-indigo-400 hover:text-indigo-300 underline"
                >
                  {showRuleInfo ? 'Ocultar' : 'Ver'} informações
                </button>
              )}
            </div>
            {ruleEnabled && (
              <div className="text-xs text-muted-foreground">
                💡 50% Necessidades | 30% Desejos | 20% Poupança
              </div>
            )}
          </div>
          
          {showRuleInfo && ruleEnabled && (
            <div className="mt-4 p-4 bg-indigo-500/10 border border-indigo-500/20 rounded-lg">
              <h3 className="font-semibold mb-2">📋 Como funciona a Regra 50-30-20:</h3>
              <ul className="text-sm space-y-1 text-muted-foreground">
                <li>• <strong>50% Necessidades:</strong> Moradia, Alimentação, Transporte, Saúde, Educação, Contas</li>
                <li>• <strong>30% Desejos:</strong> Lazer, Restaurantes, Compras, Viagens, Entretenimento</li>
                <li>• <strong>20% Poupança:</strong> Reserva de Emergência, Investimentos, Metas Financeiras</li>
              </ul>
              <p className="text-xs mt-3 text-muted-foreground">
                💡 Configure as categorias nos grupos corretos para que a regra funcione adequadamente.
              </p>
            </div>
          )}
          
          {ruleEnabled && data.necessities && data.wants && data.savings && (
            <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-4">
              {/* Necessidades */}
              <div className="p-4 bg-background/50 rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium">Necessidades (50%)</span>
                  <span className={`text-xs px-2 py-1 rounded ${
                    data.necessities.percentage > 100 
                      ? 'bg-red-500/20 text-red-400'
                      : data.necessities.percentage > 80
                      ? 'bg-yellow-500/20 text-yellow-400'
                      : 'bg-green-500/20 text-green-400'
                  }`}>
                    {data.necessities.percentage.toFixed(1)}%
                  </span>
                </div>
                <div className="text-2xl font-bold mb-1">
                  {new Intl.NumberFormat('pt-BR', {
                    style: 'currency',
                    currency: 'BRL'
                  }).format(data.necessities.actual)}
                </div>
                <div className="text-xs text-muted-foreground">
                  de {new Intl.NumberFormat('pt-BR', {
                    style: 'currency',
                    currency: 'BRL'
                  }).format(data.necessities.limit)}
                </div>
                <div className="mt-2 w-full bg-background rounded-full h-2">
                  <div
                    className={`h-2 rounded-full transition-all ${
                      data.necessities.percentage > 100 
                        ? 'bg-red-500'
                        : data.necessities.percentage > 80
                        ? 'bg-yellow-500'
                        : 'bg-green-500'
                    }`}
                    style={{ width: `${Math.min(data.necessities.percentage, 100)}%` }}
                  ></div>
                </div>
              </div>

              {/* Desejos */}
              <div className="p-4 bg-background/50 rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium">Desejos (30%)</span>
                  <span className={`text-xs px-2 py-1 rounded ${
                    data.wants.percentage > 100 
                      ? 'bg-red-500/20 text-red-400'
                      : data.wants.percentage > 80
                      ? 'bg-yellow-500/20 text-yellow-400'
                      : 'bg-green-500/20 text-green-400'
                  }`}>
                    {data.wants.percentage.toFixed(1)}%
                  </span>
                </div>
                <div className="text-2xl font-bold mb-1">
                  {new Intl.NumberFormat('pt-BR', {
                    style: 'currency',
                    currency: 'BRL'
                  }).format(data.wants.actual)}
                </div>
                <div className="text-xs text-muted-foreground">
                  de {new Intl.NumberFormat('pt-BR', {
                    style: 'currency',
                    currency: 'BRL'
                  }).format(data.wants.limit)}
                </div>
                <div className="mt-2 w-full bg-background rounded-full h-2">
                  <div
                    className={`h-2 rounded-full transition-all ${
                      data.wants.percentage > 100 
                        ? 'bg-red-500'
                        : data.wants.percentage > 80
                        ? 'bg-yellow-500'
                        : 'bg-green-500'
                    }`}
                    style={{ width: `${Math.min(data.wants.percentage, 100)}%` }}
                  ></div>
                </div>
              </div>

              {/* Poupança */}
              <div className="p-4 bg-background/50 rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium">Poupança (20%)</span>
                  <span className={`text-xs px-2 py-1 rounded ${
                    data.savings.percentage < 80 
                      ? 'bg-yellow-500/20 text-yellow-400'
                      : 'bg-green-500/20 text-green-400'
                  }`}>
                    {data.savings.percentage.toFixed(1)}%
                  </span>
                </div>
                <div className="text-2xl font-bold mb-1">
                  {new Intl.NumberFormat('pt-BR', {
                    style: 'currency',
                    currency: 'BRL'
                  }).format(data.savings.actual)}
                </div>
                <div className="text-xs text-muted-foreground">
                  de {new Intl.NumberFormat('pt-BR', {
                    style: 'currency',
                    currency: 'BRL'
                  }).format(data.savings.limit)}
                </div>
                <div className="mt-2 w-full bg-background rounded-full h-2">
                  <div
                    className={`h-2 rounded-full transition-all ${
                      data.savings.percentage < 80 
                        ? 'bg-yellow-500'
                        : 'bg-green-500'
                    }`}
                    style={{ width: `${Math.min(data.savings.percentage, 100)}%` }}
                  ></div>
                </div>
              </div>
            </div>
          )}
        </div>


        {/* Resumo Geral */}
        <div className="mb-6 grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Lado Esquerdo - Planejamento */}
          <div className="space-y-4">
            <h2 className="text-lg font-semibold mb-3">Planejamento</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className={`glass rounded-xl p-4 ${editingIncome ? 'min-h-[140px]' : ''}`}>
                <div className="flex items-center justify-between mb-2">
                  <p className="text-sm text-muted-foreground">Receita Planejada</p>
                  {!editingIncome && (
                    <button
                      onClick={() => {
                        setEditingIncome(true)
                        setNewIncomeAmount((data.planned_income || data.total_income).toString())
                      }}
                      className="text-xs text-indigo-400 hover:text-indigo-300 transition-colors"
                      title="Editar receita planejada"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                      </svg>
                    </button>
                  )}
                </div>
                {editingIncome ? (
                  <div className="space-y-3">
                    <input
                      type="number"
                      value={newIncomeAmount}
                      onChange={(e) => setNewIncomeAmount(e.target.value)}
                      placeholder="0.00"
                      step="0.01"
                      min="0"
                      className="w-full px-3 py-2.5 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 text-lg font-bold"
                      autoFocus
                    />
                    <div className="flex items-center gap-2 w-full">
                      <button
                        onClick={() => {
                          const amount = parseFloat(newIncomeAmount)
                          if (amount > 0) {
                            handleUpdateIncome(amount)
                          }
                        }}
                        className="flex-1 px-4 py-2.5 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 text-sm font-medium transition-colors"
                      >
                        Salvar
                      </button>
                      <button
                        onClick={() => {
                          setEditingIncome(false)
                          setNewIncomeAmount('')
                        }}
                        className="flex-1 px-4 py-2.5 bg-background border border-border rounded-lg hover:bg-muted text-sm font-medium transition-colors"
                      >
                        Cancelar
                      </button>
                    </div>
                  </div>
                ) : (
                  <p className="text-2xl font-bold text-green-400">
                    {new Intl.NumberFormat('pt-BR', {
                      style: 'currency',
                      currency: 'BRL'
                    }).format(data.planned_income || data.total_income)}
                  </p>
                )}
              </div>
              <div className="glass rounded-xl p-4">
                <p className="text-sm text-muted-foreground mb-1">Despesas Planejadas</p>
                <p className="text-2xl font-bold">
                  {new Intl.NumberFormat('pt-BR', {
                    style: 'currency',
                    currency: 'BRL'
                  }).format(data.total_planned_expenses)}
                </p>
              </div>
              {(data.planned_income || data.total_income) > 0 && (
                <div className="glass rounded-xl p-4">
                  <p className="text-sm text-muted-foreground mb-1">Falta Planejar</p>
                  <p className={`text-2xl font-bold ${
                    ((data.planned_income || data.total_income) - data.total_planned_expenses) > 0 
                      ? 'text-yellow-400' 
                      : 'text-green-400'
                  }`}>
                    {new Intl.NumberFormat('pt-BR', {
                      style: 'currency',
                      currency: 'BRL'
                    }).format(Math.max(0, (data.planned_income || data.total_income) - data.total_planned_expenses))}
                  </p>
                  <p className="text-xs text-muted-foreground mt-1">
                    {((((data.planned_income || data.total_income) - data.total_planned_expenses) / (data.planned_income || data.total_income)) * 100).toFixed(1)}% da receita
                  </p>
                </div>
              )}
              <div className="glass rounded-xl p-4">
                <p className="text-sm text-muted-foreground mb-1">Saldo Planejado</p>
                <p className={`text-2xl font-bold ${
                  ((data.planned_income || data.total_income) - data.total_planned_expenses) >= 0 ? 'text-green-400' : 'text-red-400'
                }`}>
                  {new Intl.NumberFormat('pt-BR', {
                    style: 'currency',
                    currency: 'BRL'
                  }).format((data.planned_income || data.total_income) - data.total_planned_expenses)}
                </p>
              </div>
            </div>
          </div>

          {/* Lado Direito - Real */}
          <div className="space-y-4">
            <h2 className="text-lg font-semibold mb-3">Real</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="glass rounded-xl p-4">
                <p className="text-sm text-muted-foreground mb-1">Receita Real</p>
                <p className="text-2xl font-bold text-green-400">
                  {new Intl.NumberFormat('pt-BR', {
                    style: 'currency',
                    currency: 'BRL'
                  }).format(data.total_income)}
                </p>
              </div>
              <div className="glass rounded-xl p-4">
                <p className="text-sm text-muted-foreground mb-1">Gasto Real</p>
                <p className="text-2xl font-bold text-red-400">
                  {new Intl.NumberFormat('pt-BR', {
                    style: 'currency',
                    currency: 'BRL'
                  }).format(data.total_actual_expenses)}
                </p>
              </div>
              <div className="glass rounded-xl p-4">
                <p className="text-sm text-muted-foreground mb-1">Saldo Real</p>
                <p className={`text-2xl font-bold ${
                  data.balance >= 0 ? 'text-green-400' : 'text-red-400'
                }`}>
                  {new Intl.NumberFormat('pt-BR', {
                    style: 'currency',
                    currency: 'BRL'
                  }).format(data.balance)}
                </p>
              </div>
              <div className="glass rounded-xl p-4">
                <p className="text-sm text-muted-foreground mb-1">Diferença</p>
                <p className={`text-2xl font-bold ${
                  (data.total_income - data.total_actual_expenses - ((data.planned_income || data.total_income) - data.total_planned_expenses)) >= 0 
                    ? 'text-green-400' 
                    : 'text-red-400'
                }`}>
                  {new Intl.NumberFormat('pt-BR', {
                    style: 'currency',
                    currency: 'BRL'
                  }).format(data.balance - ((data.planned_income || data.total_income) - data.total_planned_expenses))}
                </p>
                <p className="text-xs text-muted-foreground mt-1">
                  Real vs Planejado
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Orçamentos por Categoria */}
        <div className="space-y-6">
          {/* Mostrar todas as categorias quando regra desativada */}
          {!ruleEnabled && data.category_budgets.length > 0 && (
            <div className="glass rounded-xl p-6">
              <h2 className="text-xl font-semibold mb-4">Todas as Categorias</h2>
              <div className="space-y-3">
                {data.category_budgets.map((budget) => (
                  <CategoryBudgetRow
                    key={budget.category_id}
                    budget={budget}
                    editingBudget={editingBudget}
                    setEditingBudget={setEditingBudget}
                    newBudgetAmount={newBudgetAmount}
                    setNewBudgetAmount={setNewBudgetAmount}
                    onUpdate={handleUpdateBudget}
                    onUpdateBudgetGroup={undefined}
                    totalRemainingToPlan={getRemainingToPlanForCategory(budget)}
                    ruleEnabled={ruleEnabled}
                    plannedIncome={data.planned_income || data.total_income}
                    budgetGroupData={{
                      necessities: data.necessities ? { limit: data.necessities.limit } : undefined,
                      wants: data.wants ? { limit: data.wants.limit } : undefined,
                      savings: data.savings ? { limit: data.savings.limit } : undefined
                    }}
                  />
                ))}
              </div>
            </div>
          )}

          {/* Necessidades */}
          {ruleEnabled && grouped.necessities.length > 0 && (
            <div className="glass rounded-xl p-6">
              <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
                📦 Necessidades (50%)
                {data.necessities && (
                  <span className={`text-sm px-2 py-1 rounded ${
                    data.necessities.percentage > 100 
                      ? 'bg-red-500/20 text-red-400'
                      : data.necessities.percentage > 80
                      ? 'bg-yellow-500/20 text-yellow-400'
                      : 'bg-green-500/20 text-green-400'
                  }`}>
                    {data.necessities.percentage.toFixed(1)}%
                  </span>
                )}
              </h2>
              <div className="space-y-3">
                {grouped.necessities.map((budget) => (
                  <CategoryBudgetRow
                    key={budget.category_id}
                    budget={budget}
                    editingBudget={editingBudget}
                    setEditingBudget={setEditingBudget}
                    newBudgetAmount={newBudgetAmount}
                    setNewBudgetAmount={setNewBudgetAmount}
                    onUpdate={handleUpdateBudget}
                    onUpdateBudgetGroup={ruleEnabled ? handleUpdateBudgetGroup : undefined}
                    totalRemainingToPlan={getRemainingToPlanForCategory(budget)}
                    ruleEnabled={ruleEnabled}
                    plannedIncome={data.planned_income || data.total_income}
                    budgetGroupData={{
                      necessities: data.necessities ? { limit: data.necessities.limit } : undefined,
                      wants: data.wants ? { limit: data.wants.limit } : undefined,
                      savings: data.savings ? { limit: data.savings.limit } : undefined
                    }}
                  />
                ))}
              </div>
            </div>
          )}

          {/* Desejos */}
          {ruleEnabled && grouped.wants.length > 0 && (
            <div className="glass rounded-xl p-6">
              <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
                🎮 Desejos (30%)
                {data.wants && (
                  <span className={`text-sm px-2 py-1 rounded ${
                    data.wants.percentage > 100 
                      ? 'bg-red-500/20 text-red-400'
                      : data.wants.percentage > 80
                      ? 'bg-yellow-500/20 text-yellow-400'
                      : 'bg-green-500/20 text-green-400'
                  }`}>
                    {data.wants.percentage.toFixed(1)}%
                  </span>
                )}
              </h2>
              <div className="space-y-3">
                {grouped.wants.map((budget) => (
                  <CategoryBudgetRow
                    key={budget.category_id}
                    budget={budget}
                    editingBudget={editingBudget}
                    setEditingBudget={setEditingBudget}
                    newBudgetAmount={newBudgetAmount}
                    setNewBudgetAmount={setNewBudgetAmount}
                    onUpdate={handleUpdateBudget}
                    onUpdateBudgetGroup={ruleEnabled ? handleUpdateBudgetGroup : undefined}
                    totalRemainingToPlan={getRemainingToPlanForCategory(budget)}
                    ruleEnabled={ruleEnabled}
                    plannedIncome={data.planned_income || data.total_income}
                    budgetGroupData={{
                      necessities: data.necessities ? { limit: data.necessities.limit } : undefined,
                      wants: data.wants ? { limit: data.wants.limit } : undefined,
                      savings: data.savings ? { limit: data.savings.limit } : undefined
                    }}
                  />
                ))}
              </div>
            </div>
          )}

          {/* Poupança */}
          {ruleEnabled && grouped.savings.length > 0 && (
            <div className="glass rounded-xl p-6">
              <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
                💰 Poupança/Investimentos (20%)
                {data.savings && (
                  <span className={`text-sm px-2 py-1 rounded ${
                    data.savings.percentage < 80 
                      ? 'bg-yellow-500/20 text-yellow-400'
                      : 'bg-green-500/20 text-green-400'
                  }`}>
                    {data.savings.percentage.toFixed(1)}%
                  </span>
                )}
              </h2>
              <div className="space-y-3">
                {grouped.savings.map((budget) => (
                  <CategoryBudgetRow
                    key={budget.category_id}
                    budget={budget}
                    editingBudget={editingBudget}
                    setEditingBudget={setEditingBudget}
                    newBudgetAmount={newBudgetAmount}
                    setNewBudgetAmount={setNewBudgetAmount}
                    onUpdate={handleUpdateBudget}
                    onUpdateBudgetGroup={ruleEnabled ? handleUpdateBudgetGroup : undefined}
                    totalRemainingToPlan={getRemainingToPlanForCategory(budget)}
                    ruleEnabled={ruleEnabled}
                    plannedIncome={data.planned_income || data.total_income}
                    budgetGroupData={{
                      necessities: data.necessities ? { limit: data.necessities.limit } : undefined,
                      wants: data.wants ? { limit: data.wants.limit } : undefined,
                      savings: data.savings ? { limit: data.savings.limit } : undefined
                    }}
                  />
                ))}
              </div>
            </div>
          )}

          {/* Categorias sem grupo */}
          {grouped.ungrouped.length > 0 && (
            <div className="glass rounded-xl p-6">
              <h2 className="text-xl font-semibold mb-4">Outras Categorias</h2>
              <div className="space-y-3">
                {grouped.ungrouped.map((budget) => (
                  <CategoryBudgetRow
                    key={budget.category_id}
                    budget={budget}
                    editingBudget={editingBudget}
                    setEditingBudget={setEditingBudget}
                    newBudgetAmount={newBudgetAmount}
                    setNewBudgetAmount={setNewBudgetAmount}
                    onUpdate={handleUpdateBudget}
                    onUpdateBudgetGroup={ruleEnabled ? handleUpdateBudgetGroup : undefined}
                    totalRemainingToPlan={getRemainingToPlanForCategory(budget)}
                    ruleEnabled={ruleEnabled}
                    plannedIncome={data.planned_income || data.total_income}
                    budgetGroupData={{
                      necessities: data.necessities ? { limit: data.necessities.limit } : undefined,
                      wants: data.wants ? { limit: data.wants.limit } : undefined,
                      savings: data.savings ? { limit: data.savings.limit } : undefined
                    }}
                  />
                ))}
              </div>
            </div>
          )}

          {/* Mensagem se não houver categorias */}
          {!ruleEnabled && grouped.ungrouped.length === 0 && grouped.necessities.length === 0 && grouped.wants.length === 0 && grouped.savings.length === 0 && (
            <div className="glass rounded-xl p-6 text-center">
              <p className="text-muted-foreground">
                Nenhuma categoria de despesa encontrada. Crie categorias em Configurações primeiro.
              </p>
            </div>
          )}
        </div>

        {/* Seção de Metas */}
        {data.goals && data.goals.length > 0 && (
          <div className="mt-8 glass rounded-xl p-6">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h2 className="text-2xl font-bold mb-2">🎯 Metas Financeiras</h2>
                <p className="text-muted-foreground">
                  Total economizado: {new Intl.NumberFormat('pt-BR', {
                    style: 'currency',
                    currency: 'BRL'
                  }).format(data.total_goals_current)} / {new Intl.NumberFormat('pt-BR', {
                    style: 'currency',
                    currency: 'BRL'
                  }).format(data.total_goals_amount)}
                </p>
              </div>
              <button
                onClick={() => router.push('/goals/new')}
                className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 text-sm font-medium"
              >
                + Nova Meta
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {data.goals.map((goal) => (
                <div
                  key={goal.id}
                  className="p-4 bg-background/50 rounded-lg border border-border hover:border-indigo-500/50 transition-colors cursor-pointer"
                  onClick={() => router.push(`/goals/${goal.id}`)}
                >
                  <div className="flex items-center gap-3 mb-3">
                    <span className="text-3xl">{goal.icon || '🎯'}</span>
                    <div className="flex-1">
                      <h3 className="font-semibold">{goal.name}</h3>
                      <p className="text-xs text-muted-foreground">{goal.percentage.toFixed(1)}% completo</p>
                    </div>
                  </div>

                  <div className="mb-3">
                    <div className="w-full bg-background rounded-full h-2 overflow-hidden">
                      <div
                        className={`h-2 rounded-full transition-all ${
                          goal.percentage >= 100 ? 'bg-green-500' :
                          goal.percentage >= 75 ? 'bg-blue-500' :
                          goal.percentage >= 50 ? 'bg-indigo-500' :
                          goal.percentage >= 25 ? 'bg-yellow-500' :
                          'bg-orange-500'
                        }`}
                        style={{ width: `${Math.min(goal.percentage, 100)}%` }}
                      ></div>
                    </div>
                  </div>

                  <div className="space-y-2 text-sm">
                    <div className="flex items-center justify-between">
                      <span className="text-muted-foreground">Atual</span>
                      <span className="font-semibold text-green-400">
                        {new Intl.NumberFormat('pt-BR', {
                          style: 'currency',
                          currency: 'BRL'
                        }).format(goal.current_amount)}
                      </span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-muted-foreground">Meta</span>
                      <span className="font-semibold">
                        {new Intl.NumberFormat('pt-BR', {
                          style: 'currency',
                          currency: 'BRL'
                        }).format(goal.target_amount)}
                      </span>
                    </div>
                    <div className="pt-2 border-t border-border space-y-1">
                      {goal.suggested_monthly_contribution && (
                        <div className="flex items-center justify-between">
                          <span className="text-xs text-muted-foreground">Sugestão mensal</span>
                          <span className="text-xs font-medium text-yellow-400">
                            {new Intl.NumberFormat('pt-BR', {
                              style: 'currency',
                              currency: 'BRL'
                            }).format(goal.suggested_monthly_contribution)}
                          </span>
                        </div>
                      )}
                      <div className="flex items-center justify-between">
                        <span className="text-xs text-muted-foreground">Este mês</span>
                        <span className={`text-xs font-medium ${
                          goal.is_below_target ? 'text-red-400' : 'text-green-400'
                        }`}>
                          {new Intl.NumberFormat('pt-BR', {
                            style: 'currency',
                            currency: 'BRL'
                          }).format(goal.current_month_contribution)}
                        </span>
                      </div>
                      {goal.is_below_target && goal.suggested_monthly_contribution && (
                        <p className="text-xs text-red-400 mt-1">
                          ⚠️ Abaixo da meta mensal
                        </p>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

// Componente para linha de orçamento de categoria
function CategoryBudgetRow({
  budget,
  editingBudget,
  setEditingBudget,
  newBudgetAmount,
  setNewBudgetAmount,
  onUpdate,
  onUpdateBudgetGroup,
  totalRemainingToPlan,
  ruleEnabled,
  plannedIncome,
  budgetGroupData
}: {
  budget: CategoryBudget
  editingBudget: string | null
  setEditingBudget: (id: string | null) => void
  newBudgetAmount: string
  setNewBudgetAmount: (amount: string) => void
  onUpdate: (categoryId: string, amount: number) => void
  onUpdateBudgetGroup?: (categoryId: string, budgetGroup: string | null) => void
  totalRemainingToPlan?: number
  ruleEnabled?: boolean
  plannedIncome?: number
  budgetGroupData?: {
    necessities?: { limit: number }
    wants?: { limit: number }
    savings?: { limit: number }
  }
}) {
  const getStatusColor = (percentage: number, isOver: boolean) => {
    if (isOver) return 'text-red-400 bg-red-500/20 border-red-500/30'
    if (percentage >= 100) return 'text-yellow-400 bg-yellow-500/20 border-yellow-500/30'
    if (percentage >= 80) return 'text-orange-400 bg-orange-500/20 border-orange-500/30'
    return 'text-green-400 bg-green-500/20 border-green-500/30'
  }

  const isEditing = editingBudget === budget.category_id

  // Calcular valores da regra 50-30-20 se ativada
  let totalToPlan = 0
  let remainingToPlan = 0
  let percentageRemaining = 0

  if (ruleEnabled && plannedIncome && budgetGroupData && budget.budget_group) {
    if (budget.budget_group === 'necessities' && budgetGroupData.necessities) {
      totalToPlan = budgetGroupData.necessities.limit
    } else if (budget.budget_group === 'wants' && budgetGroupData.wants) {
      totalToPlan = budgetGroupData.wants.limit
    } else if (budget.budget_group === 'savings' && budgetGroupData.savings) {
      totalToPlan = budgetGroupData.savings.limit
    }
    remainingToPlan = totalToPlan - budget.target_amount
    percentageRemaining = totalToPlan > 0 ? (remainingToPlan / totalToPlan) * 100 : 0
  }

  return (
    <div className={`flex items-center justify-between p-4 bg-background/50 rounded-lg border-2 transition-all ${
      budget.is_over_budget 
        ? 'border-red-500 bg-red-500/10 shadow-lg shadow-red-500/20' 
        : 'border-transparent'
    }`}>
      <div className="flex-1">
        {ruleEnabled && budget.budget_group && totalToPlan > 0 ? (
          // Exibição com regra 50-30-20
          <>
            <div className="flex items-center gap-3 mb-2 flex-wrap">
              <h3 className="font-medium">{budget.category_name}</h3>
            </div>
            <div className="space-y-2 mb-3">
              <div className="flex items-center gap-4 text-sm flex-wrap">
                <div>
                  <span className="text-muted-foreground">Total para planejar: </span>
                  <span className="font-medium text-indigo-400">
                    {new Intl.NumberFormat('pt-BR', {
                      style: 'currency',
                      currency: 'BRL'
                    }).format(totalToPlan)}
                  </span>
                </div>
                {remainingToPlan > 0 && (
                  <>
                    <div>
                      <span className="text-muted-foreground">Falta planejar: </span>
                      <span className="font-medium text-yellow-400">
                        {new Intl.NumberFormat('pt-BR', {
                          style: 'currency',
                          currency: 'BRL'
                        }).format(remainingToPlan)}
                      </span>
                    </div>
                    <div>
                      <span className="text-muted-foreground">% faltante: </span>
                      <span className="font-medium text-yellow-400">
                        {percentageRemaining.toFixed(1)}%
                      </span>
                    </div>
                  </>
                )}
                {remainingToPlan === 0 && (
                  <div>
                    <span className="text-xs font-medium text-green-400">✓ Planejamento completo</span>
                  </div>
                )}
                {remainingToPlan < 0 && (
                  <>
                    <div>
                      <span className="text-muted-foreground">Passou do limite: </span>
                      <span className="font-medium text-red-400">
                        {new Intl.NumberFormat('pt-BR', {
                          style: 'currency',
                          currency: 'BRL'
                        }).format(Math.abs(remainingToPlan))}
                      </span>
                    </div>
                    <div>
                      <span className="text-muted-foreground">% excedente: </span>
                      <span className="font-medium text-red-400">
                        {Math.abs(percentageRemaining).toFixed(1)}%
                      </span>
                    </div>
                  </>
                )}
              </div>
            </div>
            {/* Comparação com o real */}
            <div className="pt-2 border-t border-border/50">
              <div className="flex items-center gap-4 text-sm flex-wrap">
                <div>
                  <span className="text-muted-foreground">Planejado: </span>
                  <span className="font-medium">
                    {new Intl.NumberFormat('pt-BR', {
                      style: 'currency',
                      currency: 'BRL'
                    }).format(budget.target_amount)}
                  </span>
                </div>
                <div>
                  <span className="text-muted-foreground">Real: </span>
                  <span className={`font-medium ${
                    budget.is_over_budget ? 'text-red-400' : ''
                  }`}>
                    {new Intl.NumberFormat('pt-BR', {
                      style: 'currency',
                      currency: 'BRL'
                    }).format(budget.actual_amount)}
                  </span>
                </div>
                {budget.target_amount > 0 && (
                  <>
                    {budget.remaining_amount > 0 ? (
                      <div className="flex items-center gap-1">
                        <span className="text-xs text-muted-foreground">Falta gastar: </span>
                        <span className="text-xs font-medium text-green-400">
                          {new Intl.NumberFormat('pt-BR', {
                            style: 'currency',
                            currency: 'BRL'
                          }).format(budget.remaining_amount)}
                        </span>
                        <span className="text-xs text-muted-foreground">
                          ({((budget.remaining_amount / budget.target_amount) * 100).toFixed(1)}%)
                        </span>
                      </div>
                    ) : budget.remaining_amount < 0 ? (
                      <div className="flex items-center gap-1">
                        <span className="text-xs text-muted-foreground">Excedente: </span>
                        <span className="text-xs font-medium text-red-400">
                          {new Intl.NumberFormat('pt-BR', {
                            style: 'currency',
                            currency: 'BRL'
                          }).format(Math.abs(budget.remaining_amount))}
                        </span>
                        <span className="text-xs text-muted-foreground">
                          ({((Math.abs(budget.remaining_amount) / budget.target_amount) * 100).toFixed(1)}%)
                        </span>
                      </div>
                    ) : (
                      <div className="flex items-center gap-1">
                        <span className="text-xs font-medium text-green-400">✓ Completo</span>
                      </div>
                    )}
                  </>
                )}
              </div>
              <div className="mt-2 w-full bg-background rounded-full h-2">
                <div
                  className={`h-2 rounded-full transition-all ${
                    budget.is_over_budget 
                      ? 'bg-red-500'
                      : budget.percentage >= 100
                      ? 'bg-yellow-500'
                      : budget.percentage >= 80
                      ? 'bg-orange-500'
                      : 'bg-green-500'
                  }`}
                  style={{ width: `${Math.min(budget.percentage, 100)}%` }}
                ></div>
              </div>
            </div>
          </>
        ) : (
          // Exibição normal (sem regra 50-30-20)
          <>
            <div className="flex items-center gap-3 mb-2 flex-wrap">
              <h3 className="font-medium">{budget.category_name}</h3>
              <span className={`px-2 py-1 text-xs rounded-full border font-medium ${getStatusColor(budget.percentage, budget.is_over_budget)}`}>
                {budget.is_over_budget ? '🔴' : budget.percentage >= 100 ? '⚠️' : budget.percentage >= 80 ? '⚡' : '✅'} {budget.percentage.toFixed(1)}%
              </span>
              {budget.target_amount > 0 && budget.remaining_amount > 0 && (
                <span className="px-2 py-1 text-xs rounded-full bg-blue-500/20 text-blue-300 border border-blue-500/30 font-medium">
                  Falta {((budget.remaining_amount / budget.target_amount) * 100).toFixed(1)}% para completar
                </span>
              )}
            </div>
            <div className="flex items-center gap-4 text-sm flex-wrap">
              <div>
                <span className="text-muted-foreground">Planejado: </span>
                <span className="font-medium">
                  {new Intl.NumberFormat('pt-BR', {
                    style: 'currency',
                    currency: 'BRL'
                  }).format(budget.target_amount)}
                </span>
              </div>
              <div>
                <span className="text-muted-foreground">Real: </span>
                <span className={`font-medium ${
                  budget.is_over_budget ? 'text-red-400' : ''
                }`}>
                  {new Intl.NumberFormat('pt-BR', {
                    style: 'currency',
                    currency: 'BRL'
                  }).format(budget.actual_amount)}
                </span>
              </div>
              {budget.target_amount > 0 && (
                <>
                  {budget.remaining_amount > 0 ? (
                    <div className="flex items-center gap-1">
                      <span className="text-xs text-muted-foreground">Falta gastar: </span>
                      <span className="text-xs font-medium text-green-400">
                        {new Intl.NumberFormat('pt-BR', {
                          style: 'currency',
                          currency: 'BRL'
                        }).format(budget.remaining_amount)}
                      </span>
                      <span className="text-xs text-muted-foreground">
                        ({((budget.remaining_amount / budget.target_amount) * 100).toFixed(1)}%)
                      </span>
                    </div>
                  ) : budget.remaining_amount < 0 ? (
                    <div className="flex items-center gap-1">
                      <span className="text-xs text-muted-foreground">Excedente: </span>
                      <span className="text-xs font-medium text-red-400">
                        {new Intl.NumberFormat('pt-BR', {
                          style: 'currency',
                          currency: 'BRL'
                        }).format(Math.abs(budget.remaining_amount))}
                      </span>
                      <span className="text-xs text-muted-foreground">
                        ({((Math.abs(budget.remaining_amount) / budget.target_amount) * 100).toFixed(1)}%)
                      </span>
                    </div>
                  ) : (
                    <div className="flex items-center gap-1">
                      <span className="text-xs font-medium text-green-400">✓ Completo</span>
                    </div>
                  )}
                </>
              )}
              {totalRemainingToPlan !== undefined && totalRemainingToPlan > 0 && (
                <div className="flex items-center gap-1 mt-1">
                  <span className="text-xs text-muted-foreground">
                    {budget.target_amount === 0 ? 'Falta planejar: ' : 'Pode planejar mais: '}
                  </span>
                  <span className="text-xs font-medium text-yellow-400">
                    {new Intl.NumberFormat('pt-BR', {
                      style: 'currency',
                      currency: 'BRL'
                    }).format(totalRemainingToPlan)}
                  </span>
                  {budget.target_amount === 0 && (
                    <span className="text-xs text-muted-foreground">
                      (sugestão)
                    </span>
                  )}
                </div>
              )}
            </div>
            <div className="mt-2 w-full bg-background rounded-full h-2">
              <div
                className={`h-2 rounded-full transition-all ${
                  budget.is_over_budget 
                    ? 'bg-red-500'
                    : budget.percentage >= 100
                    ? 'bg-yellow-500'
                    : budget.percentage >= 80
                    ? 'bg-orange-500'
                    : 'bg-green-500'
                }`}
                style={{ width: `${Math.min(budget.percentage, 100)}%` }}
              ></div>
            </div>
          </>
        )}
      </div>
      <div className="ml-4 flex items-center gap-2">
        {onUpdateBudgetGroup && (
          <select
            value={budget.budget_group || ''}
            onChange={(e) => {
              const value = e.target.value || null
              onUpdateBudgetGroup(budget.category_id, value)
            }}
            className="px-3 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm"
            title="Grupo de orçamento"
          >
            <option value="">Sem grupo</option>
            <option value="necessities">Necessidades (50%)</option>
            <option value="wants">Desejos (30%)</option>
            <option value="savings">Poupança (20%)</option>
          </select>
        )}
        {isEditing ? (
          <div className="flex items-center gap-2">
            <input
              type="number"
              value={newBudgetAmount}
              onChange={(e) => setNewBudgetAmount(e.target.value)}
              placeholder="0.00"
              step="0.01"
              min="0"
              className="w-32 px-3 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
              autoFocus
            />
            <button
              onClick={() => {
                const amount = parseFloat(newBudgetAmount)
                if (amount > 0) {
                  onUpdate(budget.category_id, amount)
                }
              }}
              className="px-3 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
            >
              Salvar
            </button>
            <button
              onClick={() => {
                setEditingBudget(null)
                setNewBudgetAmount('')
              }}
              className="px-3 py-2 bg-background border border-border rounded-lg hover:bg-muted"
            >
              Cancelar
            </button>
          </div>
        ) : (
          <button
            onClick={() => {
              setEditingBudget(budget.category_id)
              setNewBudgetAmount(budget.target_amount.toString())
            }}
            className="px-4 py-2 text-indigo-400 hover:text-indigo-300 hover:bg-indigo-500/10 rounded-lg transition-colors"
            title="Editar orçamento"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
            </svg>
          </button>
        )}
      </div>
    </div>
  )
}
