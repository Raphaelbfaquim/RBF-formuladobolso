'use client'

import { useState, useEffect } from 'react'
import { useRouter, useParams } from 'next/navigation'
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

export default function EditTransactionPage() {
  const router = useRouter()
  const params = useParams()
  const transactionId = params?.id as string

  const [loading, setLoading] = useState(false)
  const [loadingData, setLoadingData] = useState(true)
  const [accounts, setAccounts] = useState<Account[]>([])
  const [categories, setCategories] = useState<Category[]>([])
  const [relatedBill, setRelatedBill] = useState<any>(null)
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
  })

  useEffect(() => {
    if (transactionId) {
      loadTransaction()
      loadAccounts()
      loadCategories()
      loadRelatedBill()
    }
  }, [transactionId])

  const loadRelatedBill = async () => {
    try {
      const response = await apiClient.get(`/bills/by-transaction/${transactionId}`)
      setRelatedBill(response.data)
    } catch (error: any) {
      // Não é um erro se não houver bill relacionada
      if (error.response?.status !== 404) {
        console.error('Erro ao carregar conta relacionada:', error)
      }
      setRelatedBill(null)
    }
  }

  const loadTransaction = async () => {
    try {
      const response = await apiClient.get(`/transactions/${transactionId}`)
      const transaction = response.data
      
      // Converter data para formato do input
      const transactionDate = new Date(transaction.transaction_date)
      const dateStr = transactionDate.toISOString().split('T')[0]
      const timeStr = transactionDate.toTimeString().slice(0, 5)

      setFormData({
        description: transaction.description || '',
        amount: transaction.amount.toString(),
        transaction_type: transaction.transaction_type || 'expense',
        transaction_date: dateStr,
        transaction_time: timeStr,
        account_id: transaction.account_id || '',
        category_id: transaction.category_id || '',
        notes: transaction.notes || '',
        status: transaction.status || 'completed',
      })
    } catch (error: any) {
      console.error('Erro ao carregar transação:', error)
      if (error.response?.status === 401) {
        router.push('/login')
      } else if (error.response?.status === 404) {
        toast.error('Transação não encontrada')
        router.push('/transactions')
      } else {
        toast.error('Erro ao carregar transação')
      }
    } finally {
      setLoadingData(false)
    }
  }

  const loadAccounts = async () => {
    try {
      const response = await apiClient.get('/accounts/')
      setAccounts(response.data)
    } catch (error: any) {
      if (error.response?.status === 401) {
        router.push('/login')
      } else {
        toast.error('Erro ao carregar contas')
      }
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
    
    if (!formData.description.trim()) {
      toast.error('Descrição é obrigatória')
      return
    }

    if (!formData.amount || parseFloat(formData.amount) <= 0) {
      toast.error('Valor deve ser maior que zero')
      return
    }

    setLoading(true)

    try {
      // Combinar data e hora
      const transactionDateTime = new Date(
        `${formData.transaction_date}T${formData.transaction_time}:00`
      ).toISOString()

      const payload: any = {}
      
      // Apenas enviar campos que foram alterados ou são obrigatórios
      if (formData.description) payload.description = formData.description
      if (formData.amount) payload.amount = parseFloat(formData.amount)
      if (transactionDateTime) payload.transaction_date = transactionDateTime
      if (formData.status) payload.status = formData.status
      if (formData.category_id) payload.category_id = formData.category_id
      if (formData.notes !== undefined) payload.notes = formData.notes || null

      await apiClient.put(`/transactions/${transactionId}`, payload)
      
      toast.success('Transação atualizada com sucesso!')
      router.push('/transactions')
    } catch (error: any) {
      console.error('Erro ao atualizar transação:', error)
      const errorMessage = error.response?.data?.detail || error.message || 'Erro ao atualizar transação'
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

  if (loadingData) {
    return (
      <div className="min-h-screen bg-background p-6">
        <div className="max-w-3xl mx-auto">
          <div className="glass rounded-xl p-8 text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-500 mx-auto"></div>
            <p className="mt-4 text-muted-foreground">Carregando transação...</p>
          </div>
        </div>
      </div>
    )
  }

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
          <h1 className="text-3xl font-bold mb-2">Editar Transação</h1>
          <p className="text-muted-foreground">Atualize os dados da transação</p>
        </div>

        {/* Aviso sobre conta relacionada */}
        {relatedBill && (
          <div className="mb-6 glass rounded-xl p-4 bg-blue-500/10 border border-blue-500/20">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <span className="text-2xl">ℹ️</span>
                <div>
                  <p className="font-medium text-blue-400">Esta transação está relacionada a uma conta</p>
                  <p className="text-sm text-muted-foreground">
                    Esta transação foi criada automaticamente quando a conta "{relatedBill.name}" foi paga. 
                    Editar a transação não atualiza a conta relacionada.
                  </p>
                </div>
              </div>
              <Link
                href={`/bills/${relatedBill.id}/edit`}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium"
              >
                Ver Conta
              </Link>
            </div>
          </div>
        )}

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

          {/* Status */}
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
              onClick={() => router.push('/transactions')}
              className="flex-1 px-6 py-3 border border-border rounded-lg hover:bg-background/50 transition-colors font-medium"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={loading}
              className="flex-1 px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium"
            >
              {loading ? 'Salvando...' : 'Salvar Alterações'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

