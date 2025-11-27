'use client'

import { useEffect, useState } from 'react'
import { useRouter, useParams } from 'next/navigation'
import apiClient from '@/lib/api/client'
import toast from 'react-hot-toast'

const INVESTMENT_TYPES = [
  { value: 'stock', label: 'Ações' },
  { value: 'bond', label: 'Títulos' },
  { value: 'fund', label: 'Fundos' },
  { value: 'crypto', label: 'Criptomoedas' },
  { value: 'fixed_income', label: 'Renda Fixa' },
  { value: 'real_estate', label: 'Imóveis' },
  { value: 'other', label: 'Outros' }
]

const TRANSACTION_TYPES = [
  { value: 'buy', label: 'Compra' },
  { value: 'sell', label: 'Venda' },
  { value: 'dividend', label: 'Dividendo' },
  { value: 'interest', label: 'Juros' },
  { value: 'fee', label: 'Taxa' },
  { value: 'transfer', label: 'Transferência' }
]

export default function EditInvestmentTransactionPage() {
  const router = useRouter()
  const params = useParams()
  const transactionId = params.id as string
  const [loading, setLoading] = useState(false)
  const [loadingData, setLoadingData] = useState(true)
  const [formData, setFormData] = useState({
    investment_type: 'stock',
    transaction_type: 'buy',
    symbol: '',
    quantity: '1',
    unit_price: '0',
    total_amount: '0',
    fees: '0',
    transaction_date: new Date().toISOString().split('T')[0],
    notes: ''
  })

  useEffect(() => {
    loadTransaction()
  }, [transactionId])

  useEffect(() => {
    // Calcular total_amount quando quantity ou unit_price mudar
    const qty = parseFloat(formData.quantity) || 0
    const price = parseFloat(formData.unit_price) || 0
    const total = qty * price
    setFormData({ ...formData, total_amount: total.toFixed(2) })
  }, [formData.quantity, formData.unit_price])

  const loadTransaction = async () => {
    setLoadingData(true)
    try {
      const response = await apiClient.get(`/investments/transactions/${transactionId}`)
      const transaction = response.data
      const date = new Date(transaction.transaction_date).toISOString().split('T')[0]
      setFormData({
        investment_type: transaction.investment_type || 'stock',
        transaction_type: transaction.transaction_type || 'buy',
        symbol: transaction.symbol || '',
        quantity: transaction.quantity?.toString() || '1',
        unit_price: transaction.unit_price?.toString() || '0',
        total_amount: transaction.total_amount?.toString() || '0',
        fees: transaction.fees?.toString() || '0',
        transaction_date: date,
        notes: transaction.notes || ''
      })
    } catch (error: any) {
      toast.error('Erro ao carregar transação')
      router.push('/investments/transactions')
    } finally {
      setLoadingData(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    try {
      await apiClient.put(`/investments/transactions/${transactionId}`, {
        ...formData,
        quantity: parseFloat(formData.quantity),
        unit_price: parseFloat(formData.unit_price),
        total_amount: parseFloat(formData.total_amount),
        fees: parseFloat(formData.fees) || 0,
        transaction_date: new Date(formData.transaction_date + 'T12:00:00').toISOString()
      })
      toast.success('Transação atualizada com sucesso!')
      router.push('/investments/transactions')
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Erro ao atualizar transação')
    } finally {
      setLoading(false)
    }
  }

  if (loadingData) {
    return (
      <div className="min-h-screen bg-background p-6">
        <div className="max-w-2xl mx-auto">
          <div className="glass rounded-xl p-12 text-center">Carregando...</div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-2xl mx-auto">
        <h1 className="text-3xl font-bold mb-6">Editar Transação de Investimento</h1>

        <form onSubmit={handleSubmit} className="glass rounded-xl p-6 space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">Tipo de Investimento *</label>
              <select
                value={formData.investment_type}
                onChange={(e) => setFormData({ ...formData, investment_type: e.target.value })}
                className="w-full px-3 py-2 bg-background border border-border rounded-lg"
                required
              >
                {INVESTMENT_TYPES.map((type) => (
                  <option key={type.value} value={type.value}>
                    {type.label}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">Tipo de Transação *</label>
              <select
                value={formData.transaction_type}
                onChange={(e) => setFormData({ ...formData, transaction_type: e.target.value })}
                className="w-full px-3 py-2 bg-background border border-border rounded-lg"
                required
              >
                {TRANSACTION_TYPES.map((type) => (
                  <option key={type.value} value={type.value}>
                    {type.label}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Símbolo/Ticker</label>
            <input
              type="text"
              value={formData.symbol}
              onChange={(e) => setFormData({ ...formData, symbol: e.target.value.toUpperCase() })}
              className="w-full px-3 py-2 bg-background border border-border rounded-lg font-mono"
            />
          </div>

          <div className="grid grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">Quantidade *</label>
              <input
                type="number"
                step="0.000001"
                min="0"
                value={formData.quantity}
                onChange={(e) => setFormData({ ...formData, quantity: e.target.value })}
                className="w-full px-3 py-2 bg-background border border-border rounded-lg"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">Preço Unitário (R$) *</label>
              <input
                type="number"
                step="0.01"
                min="0"
                value={formData.unit_price}
                onChange={(e) => setFormData({ ...formData, unit_price: e.target.value })}
                className="w-full px-3 py-2 bg-background border border-border rounded-lg"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">Valor Total (R$)</label>
              <input
                type="number"
                step="0.01"
                value={formData.total_amount}
                readOnly
                className="w-full px-3 py-2 bg-background/50 border border-border rounded-lg"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">Taxas (R$)</label>
              <input
                type="number"
                step="0.01"
                min="0"
                value={formData.fees}
                onChange={(e) => setFormData({ ...formData, fees: e.target.value })}
                className="w-full px-3 py-2 bg-background border border-border rounded-lg"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">Data da Transação *</label>
              <input
                type="date"
                value={formData.transaction_date}
                onChange={(e) => setFormData({ ...formData, transaction_date: e.target.value })}
                className="w-full px-3 py-2 bg-background border border-border rounded-lg"
                required
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Observações</label>
            <textarea
              value={formData.notes}
              onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
              className="w-full px-3 py-2 bg-background border border-border rounded-lg"
              rows={3}
            />
          </div>

          <div className="flex gap-3 pt-4">
            <button
              type="submit"
              disabled={loading}
              className="flex-1 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 font-medium disabled:opacity-50"
            >
              {loading ? 'Salvando...' : 'Salvar'}
            </button>
            <button
              type="button"
              onClick={() => router.back()}
              className="flex-1 px-4 py-2 bg-background border border-border rounded-lg hover:bg-muted font-medium"
            >
              Cancelar
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}


