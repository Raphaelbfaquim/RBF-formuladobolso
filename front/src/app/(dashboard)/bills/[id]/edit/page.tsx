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

export default function EditBillPage() {
  const router = useRouter()
  const params = useParams()
  const billId = params?.id as string

  const [loading, setLoading] = useState(false)
  const [loadingData, setLoadingData] = useState(true)
  const [accounts, setAccounts] = useState<Account[]>([])
  const [categories, setCategories] = useState<Category[]>([])
  const [billData, setBillData] = useState<any>(null)
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    bill_type: 'expense' as 'expense' | 'income',
    amount: '',
    due_date: new Date().toISOString().split('T')[0],
    account_id: '',
    category_id: '',
    status: 'pending',
    is_recurring: false,
    recurrence_type: 'none',
    recurrence_day: '',
    recurrence_end_date: '',
  })

  useEffect(() => {
    if (billId) {
      loadBill()
      loadAccounts()
      loadCategories()
    }
  }, [billId])

  const loadBill = async () => {
    try {
      const response = await apiClient.get(`/bills/${billId}`)
      const bill = response.data
      setBillData(bill)
      
      // Converter data para formato do input
      const dueDate = new Date(bill.due_date)
      const dateStr = dueDate.toISOString().split('T')[0]

      setFormData({
        name: bill.name || '',
        description: bill.description || '',
        bill_type: bill.bill_type || 'expense',
        amount: bill.amount.toString(),
        due_date: dateStr,
        account_id: bill.account_id || '',
        category_id: bill.category_id || '',
        status: bill.status || 'pending',
        is_recurring: bill.is_recurring || false,
        recurrence_type: bill.recurrence_type || 'none',
        recurrence_day: bill.recurrence_day?.toString() || '',
        recurrence_end_date: bill.recurrence_end_date 
          ? new Date(bill.recurrence_end_date).toISOString().split('T')[0]
          : '',
      })
    } catch (error: any) {
      console.error('Erro ao carregar conta:', error)
      if (error.response?.status === 401) {
        router.push('/login')
      } else if (error.response?.status === 404) {
        toast.error('Conta não encontrada')
        router.push('/bills')
      } else {
        toast.error('Erro ao carregar conta')
      }
    } finally {
      setLoadingData(false)
    }
  }

  const loadAccounts = async () => {
    try {
      const response = await apiClient.get('/accounts/')
      if (response.data && Array.isArray(response.data)) {
        setAccounts(response.data)
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

    setLoading(true)

    try {
      const payload: any = {}
      
      // Apenas enviar campos que foram alterados
      if (formData.name) payload.name = formData.name
      if (formData.description !== undefined) payload.description = formData.description || null
      if (formData.amount) payload.amount = parseFloat(formData.amount)
      if (formData.due_date) payload.due_date = new Date(formData.due_date).toISOString()
      if (formData.status) payload.status = formData.status
      if (formData.account_id) payload.account_id = formData.account_id
      if (formData.category_id !== undefined) payload.category_id = formData.category_id || null

      await apiClient.put(`/bills/${billId}`, payload)
      
      toast.success('Conta atualizada com sucesso!')
      router.push('/bills')
    } catch (error: any) {
      console.error('Erro ao atualizar conta:', error)
      const errorMessage = error.response?.data?.detail || error.message || 'Erro ao atualizar conta'
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

  if (loadingData) {
    return (
      <div className="min-h-screen bg-background p-6">
        <div className="max-w-3xl mx-auto">
          <div className="glass rounded-xl p-8 text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-500 mx-auto"></div>
            <p className="mt-4 text-muted-foreground">Carregando conta...</p>
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
              href="/bills"
              className="text-muted-foreground hover:text-foreground transition-colors"
            >
              ← Voltar
            </Link>
          </div>
          <h1 className="text-3xl font-bold mb-2">Editar Conta</h1>
          <p className="text-muted-foreground">Atualize os dados da conta</p>
        </div>

        {/* Aviso sobre transação relacionada */}
        {billData?.transaction_id && (
          <div className="mb-6 glass rounded-xl p-4 bg-blue-500/10 border border-blue-500/20">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <span className="text-2xl">ℹ️</span>
                <div>
                  <p className="font-medium text-blue-400">Esta conta possui uma transação relacionada</p>
                  <p className="text-sm text-muted-foreground">
                    Quando uma conta é paga, uma transação é criada automaticamente. 
                    Editar a conta não atualiza a transação relacionada.
                  </p>
                </div>
              </div>
              <Link
                href={`/transactions/${billData.transaction_id}/edit`}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium"
              >
                Ver Transação
              </Link>
            </div>
          </div>
        )}

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
              <option value="pending">Pendente</option>
              <option value="paid">Pago</option>
              <option value="received">Recebido</option>
              <option value="cancelled">Cancelado</option>
            </select>
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
              {loading ? 'Salvando...' : 'Salvar Alterações'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

