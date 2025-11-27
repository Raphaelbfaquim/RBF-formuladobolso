'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import apiClient from '@/lib/api/client'
import toast from 'react-hot-toast'

interface Account {
  id: string
  name: string
  account_type: string
  balance: number
}

interface Category {
  id: string
  name: string
  category_type: string
}

export default function NewTransactionPage() {
  const router = useRouter()
  const [loading, setLoading] = useState(false)
  const [accounts, setAccounts] = useState<Account[]>([])
  const [categories, setCategories] = useState<Category[]>([])
  const [loadingData, setLoadingData] = useState(true)
  const [formData, setFormData] = useState({
    description: '',
    amount: '',
    transaction_type: 'expense' as 'income' | 'expense',
    transaction_date: new Date().toISOString().split('T')[0],
    transaction_time: new Date().toTimeString().slice(0, 5),
    account_id: '',
    category_id: '',
    notes: '',
    status: 'completed',
    is_recurring: false,
    recurrence_type: 'none',
    recurrence_day: '',
    end_date: '',
  })

  useEffect(() => {
    loadAccounts()
    loadCategories()
  }, [])

  const loadAccounts = async () => {
    try {
      const response = await apiClient.get('/accounts/')
      setAccounts(response.data)
      if (response.data.length > 0 && !formData.account_id) {
        setFormData(prev => ({ ...prev, account_id: response.data[0].id }))
      }
    } catch (error: any) {
      if (error.response?.status === 401) {
        router.push('/login')
      } else {
        toast.error('Erro ao carregar contas')
      }
    } finally {
      setLoadingData(false)
    }
  }

  const loadCategories = async () => {
    try {
      const response = await apiClient.get('/categories/')
      // Garantir que seja um array
      let categoriesData: Category[] = []
      if (Array.isArray(response.data)) {
        categoriesData = response.data
      } else if (response.data && typeof response.data === 'object') {
        // Se retornar um objeto, tentar extrair array ou usar array vazio
        categoriesData = []
      }
      setCategories(categoriesData)
    } catch (error: any) {
      console.error('Erro ao carregar categorias:', error)
      // Categorias são opcionais, não mostrar erro
      setCategories([]) // Garantir que seja um array vazio em caso de erro
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!formData.description.trim()) {
      toast.error('Descrição é obrigatória')
      return
    }

    if (!formData.amount || parseFloat(formData.amount) <= 0) {
      toast.error('Valor deve ser maior que zero')
      return
    }

    if (!formData.account_id) {
      toast.error('Selecione uma conta')
      return
    }

    setLoading(true)

    try {
      // Combinar data e hora
      const transactionDateTime = new Date(
        `${formData.transaction_date}T${formData.transaction_time}:00`
      ).toISOString()

      // Se for recorrente, criar bill (conta a pagar) como pendente
      if (formData.is_recurring && formData.recurrence_type !== 'none') {
        // Criar bill (conta a pagar) como pendente
        const billPayload = {
          name: formData.description,
          description: formData.notes || null,
          bill_type: formData.transaction_type, // Já está em lowercase ('expense' ou 'income')
          amount: parseFloat(formData.amount),
          due_date: transactionDateTime,
          account_id: formData.account_id || null,
          category_id: formData.category_id || null,
          is_recurring: true,
          recurrence_type: formData.recurrence_type, // Já está em lowercase (daily, weekly, monthly, yearly)
          recurrence_day: formData.recurrence_day ? parseInt(formData.recurrence_day) : null,
          recurrence_end_date: formData.end_date ? new Date(`${formData.end_date}T23:59:59`).toISOString() : null,
        }

        await apiClient.post('/bills/', billPayload)
        
        toast.success('Conta recorrente criada com sucesso!')
      } else {
        // Transação normal
        const payload = {
          description: formData.description,
          amount: parseFloat(formData.amount),
          transaction_type: formData.transaction_type,
          transaction_date: transactionDateTime,
          account_id: formData.account_id,
          category_id: formData.category_id || null,
          notes: formData.notes || null,
          status: formData.status,
        }

        await apiClient.post('/transactions/', payload)
        
        toast.success('Transação criada com sucesso!')
      }
      
      router.push('/transactions')
    } catch (error: any) {
      console.error('Erro ao criar transação:', error)
      const errorMessage = error.response?.data?.detail || error.message || 'Erro ao criar transação'
      toast.error(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
  }

  const filteredCategories = Array.isArray(categories) 
    ? categories.filter(cat => cat.category_type === formData.transaction_type)
    : []

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-3xl mx-auto">
        <div className="mb-8">
          <div className="flex items-center gap-4 mb-4">
            <Link
              href="/transactions"
              className="text-muted-foreground hover:text-foreground transition-colors"
            >
              ← Voltar
            </Link>
          </div>
          <h1 className="text-3xl font-bold mb-2">Nova Transação</h1>
          <p className="text-muted-foreground">Registre uma nova receita ou despesa</p>
        </div>

        {loadingData ? (
          <div className="glass rounded-xl p-8 text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-500 mx-auto"></div>
            <p className="mt-4 text-muted-foreground">Carregando dados...</p>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="glass rounded-xl p-6 space-y-6">
            {/* Tipo de Transação */}
            <div>
              <label className="block text-sm font-medium mb-2">
                Tipo de Transação *
              </label>
              <div className="flex gap-4">
                <label className="flex-1 cursor-pointer">
                  <input
                    type="radio"
                    name="transaction_type"
                    value="income"
                    checked={formData.transaction_type === 'income'}
                    onChange={handleChange}
                    className="sr-only"
                  />
                  <div className={`p-4 rounded-lg border-2 transition-all ${
                    formData.transaction_type === 'income'
                      ? 'border-green-500 bg-green-500/10'
                      : 'border-border hover:border-green-500/50'
                  }`}>
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-lg bg-green-500/20 flex items-center justify-center">
                        <span className="text-xl">📈</span>
                      </div>
                      <div>
                        <p className="font-medium">Receita</p>
                        <p className="text-sm text-muted-foreground">Dinheiro entrando</p>
                      </div>
                    </div>
                  </div>
                </label>
                <label className="flex-1 cursor-pointer">
                  <input
                    type="radio"
                    name="transaction_type"
                    value="expense"
                    checked={formData.transaction_type === 'expense'}
                    onChange={handleChange}
                    className="sr-only"
                  />
                  <div className={`p-4 rounded-lg border-2 transition-all ${
                    formData.transaction_type === 'expense'
                      ? 'border-red-500 bg-red-500/10'
                      : 'border-border hover:border-red-500/50'
                  }`}>
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-lg bg-red-500/20 flex items-center justify-center">
                        <span className="text-xl">📉</span>
                      </div>
                      <div>
                        <p className="font-medium">Despesa</p>
                        <p className="text-sm text-muted-foreground">Dinheiro saindo</p>
                      </div>
                    </div>
                  </div>
                </label>
              </div>
            </div>

            {/* Descrição */}
            <div>
              <label htmlFor="description" className="block text-sm font-medium mb-2">
                Descrição *
              </label>
              <input
                id="description"
                type="text"
                name="description"
                value={formData.description}
                onChange={handleChange}
                required
                maxLength={500}
                className="w-full px-4 py-3 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
                placeholder="Ex: Salário, Aluguel, Supermercado..."
              />
            </div>

            {/* Valor */}
            <div>
              <label htmlFor="amount" className="block text-sm font-medium mb-2">
                Valor (R$) *
              </label>
              <input
                id="amount"
                type="number"
                name="amount"
                value={formData.amount}
                onChange={handleChange}
                required
                min="0.01"
                step="0.01"
                className="w-full px-4 py-3 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
                placeholder="0,00"
              />
            </div>

            {/* Conta */}
            <div>
              <label htmlFor="account_id" className="block text-sm font-medium mb-2">
                Conta *
              </label>
              <select
                id="account_id"
                name="account_id"
                value={formData.account_id}
                onChange={handleChange}
                required
                className="w-full px-4 py-3 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
              >
                <option value="">Selecione uma conta</option>
                {accounts.map((account) => (
                  <option key={account.id} value={account.id}>
                    {account.name} - {account.account_type} (Saldo: {new Intl.NumberFormat('pt-BR', {
                      style: 'currency',
                      currency: 'BRL'
                    }).format(account.balance)})
                  </option>
                ))}
              </select>
              {accounts.length === 0 && (
                <p className="text-sm text-muted-foreground mt-2">
                  Nenhuma conta encontrada. <Link href="/accounts/new" className="text-indigo-400 hover:text-indigo-300">Criar conta</Link>
                </p>
              )}
            </div>

            {/* Categoria */}
            <div>
              <label htmlFor="category_id" className="block text-sm font-medium mb-2">
                Categoria
              </label>
              <select
                id="category_id"
                name="category_id"
                value={formData.category_id}
                onChange={handleChange}
                className="w-full px-4 py-3 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
              >
                <option value="">Sem categoria</option>
                {filteredCategories.map((category) => (
                  <option key={category.id} value={category.id}>
                    {category.name}
                  </option>
                ))}
              </select>
              {filteredCategories.length === 0 && (
                <p className="text-sm text-muted-foreground mt-2">
                  Nenhuma categoria encontrada para {formData.transaction_type === 'income' ? 'receitas' : 'despesas'}. <Link href="/categories" className="text-indigo-400 hover:text-indigo-300">Criar categoria</Link>
                </p>
              )}
            </div>

            {/* Data e Hora */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label htmlFor="transaction_date" className="block text-sm font-medium mb-2">
                  Data *
                </label>
                <input
                  id="transaction_date"
                  type="date"
                  name="transaction_date"
                  value={formData.transaction_date}
                  onChange={handleChange}
                  required
                  className="w-full px-4 py-3 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
                />
              </div>
              <div>
                <label htmlFor="transaction_time" className="block text-sm font-medium mb-2">
                  Hora
                </label>
                <input
                  id="transaction_time"
                  type="time"
                  name="transaction_time"
                  value={formData.transaction_time}
                  onChange={handleChange}
                  className="w-full px-4 py-3 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
                />
              </div>
            </div>

            {/* Recorrência */}
            <div className="border-t border-border pt-6">
              <div className="flex items-center gap-3 mb-4">
                <input
                  type="checkbox"
                  id="is_recurring"
                  name="is_recurring"
                  checked={formData.is_recurring}
                  onChange={(e) => {
                    setFormData(prev => ({ 
                      ...prev, 
                      is_recurring: e.target.checked,
                      recurrence_type: e.target.checked ? 'monthly' : 'none'
                    }))
                  }}
                  className="w-5 h-5 rounded border-border text-indigo-600 focus:ring-indigo-500"
                />
                <label htmlFor="is_recurring" className="text-sm font-medium cursor-pointer">
                  Tornar esta transação recorrente
                </label>
              </div>

              {formData.is_recurring && (
                <div className="space-y-4 pl-8 border-l-2 border-indigo-500/20">
                  <div>
                    <label htmlFor="recurrence_type" className="block text-sm font-medium mb-2">
                      Tipo de Recorrência *
                    </label>
                    <select
                      id="recurrence_type"
                      name="recurrence_type"
                      value={formData.recurrence_type}
                      onChange={handleChange}
                      required={formData.is_recurring}
                      className="w-full px-4 py-3 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
                    >
                      <option value="none">Selecione...</option>
                      <option value="daily">Diária</option>
                      <option value="weekly">Semanal</option>
                      <option value="monthly">Mensal</option>
                      <option value="yearly">Anual</option>
                    </select>
                  </div>

                  {formData.recurrence_type === 'monthly' && (
                    <div>
                      <label htmlFor="recurrence_day" className="block text-sm font-medium mb-2">
                        Dia do Mês (1-31)
                      </label>
                      <input
                        id="recurrence_day"
                        type="number"
                        name="recurrence_day"
                        value={formData.recurrence_day}
                        onChange={handleChange}
                        min="1"
                        max="31"
                        className="w-full px-4 py-3 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
                        placeholder="Ex: 15"
                      />
                    </div>
                  )}

                  <div>
                    <label htmlFor="end_date" className="block text-sm font-medium mb-2">
                      Data Final (Opcional)
                    </label>
                    <input
                      id="end_date"
                      type="date"
                      name="end_date"
                      value={formData.end_date}
                      onChange={handleChange}
                      min={formData.transaction_date}
                      className="w-full px-4 py-3 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
                      placeholder="Deixe em branco para recorrência infinita"
                    />
                    <p className="text-xs text-muted-foreground mt-1">
                      Deixe em branco para recorrência infinita
                    </p>
                  </div>

                  <div className="bg-yellow-500/10 border border-yellow-500/20 rounded-lg p-3">
                    <p className="text-sm text-yellow-300">
                      ⚠️ Transações recorrentes são criadas automaticamente com status <strong>Pendente</strong>
                    </p>
                  </div>
                </div>
              )}
            </div>

            {/* Status - Oculto se for recorrente */}
            {!formData.is_recurring && (
              <div>
                <label htmlFor="status" className="block text-sm font-medium mb-2">
                  Status
                </label>
                <select
                  id="status"
                  name="status"
                  value={formData.status}
                  onChange={handleChange}
                  className="w-full px-4 py-3 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
                >
                  <option value="completed">Concluída</option>
                  <option value="pending">Pendente</option>
                  <option value="cancelled">Cancelada</option>
                </select>
              </div>
            )}

            {/* Notas */}
            <div>
              <label htmlFor="notes" className="block text-sm font-medium mb-2">
                Notas
              </label>
              <textarea
                id="notes"
                name="notes"
                value={formData.notes}
                onChange={handleChange}
                rows={4}
                maxLength={1000}
                className="w-full px-4 py-3 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all resize-none"
                placeholder="Observações adicionais sobre esta transação..."
              />
            </div>

            {/* Botões */}
            <div className="flex gap-4 pt-4">
              <button
                type="button"
                onClick={() => router.back()}
                className="flex-1 px-6 py-3 border border-border rounded-lg hover:bg-background/50 transition-colors font-medium"
              >
                Cancelar
              </button>
              <button
                type="submit"
                disabled={loading || accounts.length === 0}
                className="flex-1 px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium"
              >
                {loading ? 'Salvando...' : 'Criar Transação'}
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  )
}

