'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import apiClient from '@/lib/api/client'
import toast from 'react-hot-toast'

interface DashboardData {
  total_balance: number
  monthly_income: number
  monthly_expenses: number
  monthly_savings: number
  accounts_count: number
  transactions_count: number
  recent_transactions: any[]
  upcoming_bills: any[]
  goals_progress: any[]
}

export default function DashboardPage() {
  const router = useRouter()
  const [loading, setLoading] = useState(true)
  const [data, setData] = useState<DashboardData | null>(null)

  useEffect(() => {
    loadDashboard()
  }, [])

  const loadDashboard = async () => {
    try {
      const response = await apiClient.get('/dashboard/summary')
      setData(response.data)
    } catch (error: any) {
      if (error.response?.status === 401) {
        router.push('/login')
      } else {
        toast.error('Erro ao carregar dashboard')
      }
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-500 mx-auto"></div>
          <p className="mt-4 text-muted-foreground">Carregando dashboard...</p>
        </div>
      </div>
    )
  }

  if (!data) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <p className="text-muted-foreground">Nenhum dado disponível</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">Dashboard</h1>
          <p className="text-muted-foreground">Visão geral das suas finanças</p>
        </div>

        {/* Cards de Resumo */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="glass rounded-xl p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground mb-1">Saldo Total</p>
                <p className="text-2xl font-bold">
                  {new Intl.NumberFormat('pt-BR', {
                    style: 'currency',
                    currency: 'BRL'
                  }).format(data.total_balance)}
                </p>
              </div>
              <div className="w-12 h-12 bg-indigo-500/20 rounded-lg flex items-center justify-center">
                <span className="text-2xl">💰</span>
              </div>
            </div>
          </div>

          <div className="glass rounded-xl p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground mb-1">Receitas (Mês)</p>
                <p className="text-2xl font-bold text-green-400">
                  {new Intl.NumberFormat('pt-BR', {
                    style: 'currency',
                    currency: 'BRL'
                  }).format(data.monthly_income)}
                </p>
              </div>
              <div className="w-12 h-12 bg-green-500/20 rounded-lg flex items-center justify-center">
                <span className="text-2xl">📈</span>
              </div>
            </div>
          </div>

          <div className="glass rounded-xl p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground mb-1">Despesas (Mês)</p>
                <p className="text-2xl font-bold text-red-400">
                  {new Intl.NumberFormat('pt-BR', {
                    style: 'currency',
                    currency: 'BRL'
                  }).format(data.monthly_expenses)}
                </p>
              </div>
              <div className="w-12 h-12 bg-red-500/20 rounded-lg flex items-center justify-center">
                <span className="text-2xl">📉</span>
              </div>
            </div>
          </div>

          <div className="glass rounded-xl p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground mb-1">Economia (Mês)</p>
                <p className="text-2xl font-bold text-blue-400">
                  {new Intl.NumberFormat('pt-BR', {
                    style: 'currency',
                    currency: 'BRL'
                  }).format(data.monthly_savings)}
                </p>
              </div>
              <div className="w-12 h-12 bg-blue-500/20 rounded-lg flex items-center justify-center">
                <span className="text-2xl">💎</span>
              </div>
            </div>
          </div>
        </div>

        {/* Grid de Conteúdo */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Transações Recentes */}
          <div className="lg:col-span-2 glass rounded-xl p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold">Transações Recentes</h2>
              <button
                onClick={() => router.push('/transactions')}
                className="text-sm text-indigo-400 hover:text-indigo-300"
              >
                Ver todas
              </button>
            </div>
            {data.recent_transactions && data.recent_transactions.length > 0 ? (
              <div className="space-y-3">
                {data.recent_transactions.slice(0, 5).map((transaction: any) => (
                  <div
                    key={transaction.id}
                    className="flex items-center justify-between p-3 bg-background/50 rounded-lg"
                  >
                    <div className="flex items-center gap-3">
                      <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                        transaction.transaction_type === 'income' 
                          ? 'bg-green-500/20' 
                          : 'bg-red-500/20'
                      }`}>
                        <span>
                          {transaction.transaction_type === 'income' ? '📈' : '📉'}
                        </span>
                      </div>
                      <div>
                        <p className="font-medium">{transaction.description}</p>
                        <p className="text-sm text-muted-foreground">
                          {new Date(transaction.transaction_date).toLocaleDateString('pt-BR')}
                        </p>
                      </div>
                    </div>
                    <div className={`font-semibold ${
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
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-muted-foreground text-center py-8">
                Nenhuma transação recente
              </p>
            )}
          </div>

          {/* Contas a Pagar */}
          <div className="glass rounded-xl p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold">Contas a Pagar</h2>
              <button
                onClick={() => router.push('/bills')}
                className="text-sm text-indigo-400 hover:text-indigo-300"
              >
                Ver todas
              </button>
            </div>
            {data.upcoming_bills && data.upcoming_bills.length > 0 ? (
              <div className="space-y-3">
                {data.upcoming_bills.slice(0, 5).map((bill: any) => {
                  const isOverdue = bill.is_overdue || new Date(bill.due_date) < new Date()
                  return (
                    <div
                      key={bill.id}
                      className={`p-3 rounded-lg ${
                        isOverdue 
                          ? 'bg-red-500/10 border border-red-500/20' 
                          : 'bg-background/50'
                      }`}
                    >
                      <div className="flex items-center justify-between mb-1">
                        <p className={`font-medium ${isOverdue ? 'text-red-400' : ''}`}>
                          {bill.description}
                        </p>
                        {isOverdue && (
                          <span className="text-xs bg-red-500/20 text-red-400 px-2 py-1 rounded">
                            Vencida
                          </span>
                        )}
                      </div>
                      <div className="flex items-center justify-between mt-2">
                        <p className={`text-sm ${isOverdue ? 'text-red-300' : 'text-muted-foreground'}`}>
                          {new Date(bill.due_date).toLocaleDateString('pt-BR')}
                        </p>
                        <p className={`font-semibold ${isOverdue ? 'text-red-400' : ''}`}>
                          {new Intl.NumberFormat('pt-BR', {
                            style: 'currency',
                            currency: 'BRL'
                          }).format(bill.amount)}
                        </p>
                      </div>
                    </div>
                  )
                })}
              </div>
            ) : (
              <p className="text-muted-foreground text-center py-8">
                Nenhuma conta a pagar
              </p>
            )}
          </div>
        </div>

        {/* Metas */}
        {data.goals_progress && data.goals_progress.length > 0 && (
          <div className="mt-6 glass rounded-xl p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold">Metas e Sonhos</h2>
              <button
                onClick={() => router.push('/goals')}
                className="text-sm text-indigo-400 hover:text-indigo-300"
              >
                Ver todas
              </button>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {data.goals_progress.slice(0, 3).map((goal: any) => (
                <div key={goal.id} className="p-4 bg-background/50 rounded-lg">
                  <p className="font-medium mb-2">{goal.name}</p>
                  <div className="w-full bg-background rounded-full h-2 mb-2">
                    <div
                      className="bg-indigo-500 h-2 rounded-full transition-all"
                      style={{ width: `${goal.progress_percentage}%` }}
                    ></div>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground">
                      {goal.progress_percentage.toFixed(0)}%
                    </span>
                    <span className="font-semibold">
                      {new Intl.NumberFormat('pt-BR', {
                        style: 'currency',
                        currency: 'BRL'
                      }).format(goal.current_amount)} / {new Intl.NumberFormat('pt-BR', {
                        style: 'currency',
                        currency: 'BRL'
                      }).format(goal.target_amount)}
                    </span>
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

