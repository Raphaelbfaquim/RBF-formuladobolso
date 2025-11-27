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

export default function NewBillPage() {
  const router = useRouter()
  const [loading, setLoading] = useState(false)
  const [loadingData, setLoadingData] = useState(true)
  const [accounts, setAccounts] = useState<Account[]>([])
  const [categories, setCategories] = useState<Category[]>([])
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    bill_type: 'expense' as 'expense' | 'income',
    amount: '',
    due_date: new Date().toISOString().split('T')[0],
    account_id: '',
    category_id: '',
    is_recurring: false,
    recurrence_type: 'none',
    recurrence_day: '',
    recurrence_end_date: '',
  })

  useEffect(() => {
    loadAccounts()
    loadCategories()
  }, [])

  const loadAccounts = async () => {
    try {
      const response = await apiClient.get('/accounts/')
      if (response.data && Array.isArray(response.data)) {
        setAccounts(response.data)
        if (response.data.length > 0 && !formData.account_id) {
          setFormData(prev => ({ ...prev, account_id: response.data[0].id }))
        }
      } else {
        setAccounts([])
      }
    } catch (error: any) {
      console.error('Erro ao carregar contas:', error)
      if (error.response?.status === 401) {
        router.push('/login')
      } else {
        const errorMessage = error.response?.data?.detail || error.message || 'Erro ao carregar contas'
        toast.error(errorMessage)
      }
      setAccounts([])
    } finally {
      setLoadingData(false)
    }
  }

  const loadCategories = async () => {
    try {
      const response = await apiClient.get('/categories/')
      let categoriesData: Category[] = []
      if (Array.isArray(response.data)) {
        categoriesData = response.data
      }
      setCategories(categoriesData)
    } catch (error: any) {
      console.error('Erro ao carregar categorias:', error)
      setCategories([])
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!formData.name.trim()) {
      toast.error('Nome é obrigatório')
      return
    }

    if (!formData.amount || parseFloat(formData.amount) <= 0) {
      toast.error('Valor deve ser maior que zero')
      return
    }

    if (!formData.due_date) {
      toast.error('Data de vencimento é obrigatória')
      return
    }

    setLoading(true)

    try {
      const payload: any = {
        name: formData.name,
        bill_type: formData.bill_type,
        amount: parseFloat(formData.amount),
        due_date: new Date(formData.due_date).toISOString(),
      }

      if (formData.description) payload.description = formData.description
      if (formData.account_id) payload.account_id = formData.account_id
      if (formData.category_id) payload.category_id = formData.category_id
      
      if (formData.is_recurring) {
        payload.is_recurring = true
        payload.recurrence_type = formData.recurrence_type
        if (formData.recurrence_day) payload.recurrence_day = parseInt(formData.recurrence_day)
        if (formData.recurrence_end_date) {
          payload.recurrence_end_date = new Date(formData.recurrence_end_date).toISOString()
        }
      }

      await apiClient.post('/bills/', payload)
      
      toast.success('Conta criada com sucesso!')
      router.push('/bills')
    } catch (error: any) {
      console.error('Erro ao criar conta:', error)
      const errorMessage = error.response?.data?.detail || error.message || 'Erro ao criar conta'
      toast.error(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value, type } = e.target
    if (type === 'checkbox') {
      const checked = (e.target as HTMLInputElement).checked
      setFormData(prev => ({ ...prev, [name]: checked }))
    } else {
      setFormData(prev => ({ ...prev, [name]: value }))
    }
  }

  const filteredCategories = Array.isArray(categories) 
    ? categories.filter(cat => cat.category_type === formData.bill_type)
    : []

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-3xl mx-auto">
        <div className="mb-8">
          <div className="flex items-center gap-4 mb-4">
            <Link
              href="/bills"
              className="text-muted-foreground hover:text-foreground transition-colors"
            >
              ← Voltar
            </Link>
          </div>
          <h1 className="text-3xl font-bold mb-2">Nova Conta</h1>
          <p className="text-muted-foreground">Registre uma nova conta a pagar ou receber</p>
        </div>

        {loadingData ? (
          <div className="glass rounded-xl p-8 text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-500 mx-auto"></div>
            <p className="mt-4 text-muted-foreground">Carregando dados...</p>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="glass rounded-xl p-6 space-y-6">
            {/* Tipo de Conta */}
            <div>
              <label className="block text-sm font-medium mb-2">
                Tipo de Conta *
              </label>
              <div className="flex gap-4">
                <label className="flex-1 cursor-pointer">
                  <input
                    type="radio"
                    name="bill_type"
                    value="expense"
                    checked={formData.bill_type === 'expense'}
                    onChange={handleChange}
                    className="sr-only"
                  />
                  <div className={`p-4 rounded-lg border-2 transition-all ${
                    formData.bill_type === 'expense'
                      ? 'border-red-500 bg-red-500/10'
                      : 'border-border hover:border-red-500/50'
                  }`}>
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-lg bg-red-500/20 flex items-center justify-center">
                        <span className="text-xl">📉</span>
                      </div>
                      <div>
                        <p className="font-medium">Conta a Pagar</p>
                        <p className="text-sm text-muted-foreground">Despesa recorrente</p>
                      </div>
                    </div>
                  </div>
                </label>
                <label className="flex-1 cursor-pointer">
                  <input
                    type="radio"
                    name="bill_type"
                    value="income"
                    checked={formData.bill_type === 'income'}
                    onChange={handleChange}
                    className="sr-only"
                  />
                  <div className={`p-4 rounded-lg border-2 transition-all ${
                    formData.bill_type === 'income'
                      ? 'border-green-500 bg-green-500/10'
                      : 'border-border hover:border-green-500/50'
                  }`}>
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-lg bg-green-500/20 flex items-center justify-center">
                        <span className="text-xl">📈</span>
                      </div>
                      <div>
                        <p className="font-medium">Conta a Receber</p>
                        <p className="text-sm text-muted-foreground">Receita recorrente</p>
                      </div>
                    </div>
                  </div>
                </label>
              </div>
            </div>

            {/* Nome */}
            <div>
              <label htmlFor="name" className="block text-sm font-medium mb-2">
                Nome *
              </label>
              <input
                id="name"
                type="text"
                name="name"
                value={formData.name}
                onChange={handleChange}
                required
                maxLength={255}
                className="w-full px-4 py-3 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
                placeholder="Ex: Aluguel, Salário, Internet..."
              />
            </div>

            {/* Descrição */}
            <div>
              <label htmlFor="description" className="block text-sm font-medium mb-2">
                Descrição
              </label>
              <textarea
                id="description"
                name="description"
                value={formData.description}
                onChange={handleChange}
                rows={3}
                maxLength={1000}
                className="w-full px-4 py-3 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all resize-none"
                placeholder="Observações sobre esta conta..."
              />
            </div>

            {/* Valor e Data */}
            <div className="grid grid-cols-2 gap-4">
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
              <div>
                <label htmlFor="due_date" className="block text-sm font-medium mb-2">
                  Data de Vencimento *
                </label>
                <input
                  id="due_date"
                  type="date"
                  name="due_date"
                  value={formData.due_date}
                  onChange={handleChange}
                  required
                  className="w-full px-4 py-3 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
                />
              </div>
            </div>

            {/* Conta */}
            <div>
              <label htmlFor="account_id" className="block text-sm font-medium mb-2">
                Conta
              </label>
              <select
                id="account_id"
                name="account_id"
                value={formData.account_id}
                onChange={handleChange}
                className="w-full px-4 py-3 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
              >
                <option value="">Selecione uma conta (opcional)</option>
                {accounts.map((account) => (
                  <option key={account.id} value={account.id}>
                    {account.name} - {account.account_type}
                  </option>
                ))}
              </select>
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
            </div>

            {/* Recorrência */}
            <div className="border-t border-border pt-6">
              <div className="flex items-center gap-2 mb-4">
                <input
                  type="checkbox"
                  id="is_recurring"
                  name="is_recurring"
                  checked={formData.is_recurring}
                  onChange={handleChange}
                  className="w-4 h-4"
                />
                <label htmlFor="is_recurring" className="text-sm font-medium cursor-pointer">
                  Conta recorrente
                </label>
              </div>

              {formData.is_recurring && (
                <div className="space-y-4 pl-6 border-l-2 border-indigo-500/30">
                  <div>
                    <label htmlFor="recurrence_type" className="block text-sm font-medium mb-2">
                      Tipo de Recorrência
                    </label>
                    <select
                      id="recurrence_type"
                      name="recurrence_type"
                      value={formData.recurrence_type}
                      onChange={handleChange}
                      className="w-full px-4 py-3 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
                    >
                      <option value="none">Sem recorrência</option>
                      <option value="daily">Diária</option>
                      <option value="weekly">Semanal</option>
                      <option value="monthly">Mensal</option>
                      <option value="yearly">Anual</option>
                    </select>
                  </div>

                  {formData.recurrence_type === 'monthly' && (
                    <div>
                      <label htmlFor="recurrence_day" className="block text-sm font-medium mb-2">
                        Dia do Mês
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
                        placeholder="Ex: 5 (todo dia 5)"
                      />
                    </div>
                  )}

                  <div>
                    <label htmlFor="recurrence_end_date" className="block text-sm font-medium mb-2">
                      Data Final (opcional)
                    </label>
                    <input
                      id="recurrence_end_date"
                      type="date"
                      name="recurrence_end_date"
                      value={formData.recurrence_end_date}
                      onChange={handleChange}
                      className="w-full px-4 py-3 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
                    />
                  </div>
                </div>
              )}
            </div>

            {/* Botões */}
            <div className="flex gap-4 pt-4">
              <button
                type="button"
                onClick={() => router.push('/bills')}
                className="flex-1 px-6 py-3 border border-border rounded-lg hover:bg-background/50 transition-colors font-medium"
              >
                Cancelar
              </button>
              <button
                type="submit"
                disabled={loading}
                className="flex-1 px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium"
              >
                {loading ? 'Salvando...' : 'Criar Conta'}
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  )
}

