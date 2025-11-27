'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import apiClient from '@/lib/api/client'
import toast from 'react-hot-toast'

export default function NewAccountPage() {
  const router = useRouter()
  const [loading, setLoading] = useState(false)
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    account_type: 'checking',
    initial_balance: '0',
    currency: 'BRL',
    bank_name: '',
    account_number: '',
  })

  const accountTypes = [
    { value: 'checking', label: 'Conta Corrente', icon: '🏦' },
    { value: 'savings', label: 'Conta Poupança', icon: '💰' },
    { value: 'credit_card', label: 'Cartão de Crédito', icon: '💳' },
    { value: 'cash', label: 'Dinheiro', icon: '💵' },
    { value: 'other', label: 'Outros', icon: '📁' },
  ]

  const currencies = [
    { value: 'BRL', label: 'Real (BRL)' },
    { value: 'USD', label: 'Dólar (USD)' },
    { value: 'EUR', label: 'Euro (EUR)' },
  ]

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!formData.name.trim()) {
      toast.error('Nome da conta é obrigatório')
      return
    }

    setLoading(true)

    try {
      const payload = {
        name: formData.name,
        description: formData.description || null,
        account_type: formData.account_type,
        initial_balance: parseFloat(formData.initial_balance) || 0,
        currency: formData.currency,
        bank_name: formData.bank_name || null,
        account_number: formData.account_number || null,
      }

      await apiClient.post('/accounts/', payload)
      
      toast.success('Conta criada com sucesso!')
      router.push('/accounts')
    } catch (error: any) {
      console.error('Erro ao criar conta:', error)
      const errorMessage = error.response?.data?.detail || error.message || 'Erro ao criar conta'
      toast.error(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
  }

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-3xl mx-auto">
        <div className="mb-8">
          <div className="flex items-center gap-4 mb-4">
            <Link
              href="/accounts"
              className="text-muted-foreground hover:text-foreground transition-colors"
            >
              ← Voltar
            </Link>
          </div>
          <h1 className="text-3xl font-bold mb-2">Nova Conta</h1>
          <p className="text-muted-foreground">Adicione uma nova conta financeira</p>
        </div>

        <form onSubmit={handleSubmit} className="glass rounded-xl p-6 space-y-6">
          {/* Nome */}
          <div>
            <label htmlFor="name" className="block text-sm font-medium mb-2">
              Nome da Conta *
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
              placeholder="Ex: Conta Principal, Cartão Nubank..."
            />
          </div>

          {/* Tipo de Conta */}
          <div>
            <label className="block text-sm font-medium mb-2">
              Tipo de Conta *
            </label>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
              {accountTypes.map((type) => (
                <label key={type.value} className="cursor-pointer">
                  <input
                    type="radio"
                    name="account_type"
                    value={type.value}
                    checked={formData.account_type === type.value}
                    onChange={handleChange}
                    className="sr-only"
                  />
                  <div className={`p-4 rounded-lg border-2 transition-all ${
                    formData.account_type === type.value
                      ? 'border-indigo-500 bg-indigo-500/10'
                      : 'border-border hover:border-indigo-500/50'
                  }`}>
                    <div className="text-center">
                      <div className="text-2xl mb-2">{type.icon}</div>
                      <p className="text-sm font-medium">{type.label}</p>
                    </div>
                  </div>
                </label>
              ))}
            </div>
          </div>

          {/* Saldo Inicial */}
          <div>
            <label htmlFor="initial_balance" className="block text-sm font-medium mb-2">
              Saldo Inicial
            </label>
            <input
              id="initial_balance"
              type="number"
              name="initial_balance"
              value={formData.initial_balance}
              onChange={handleChange}
              min="0"
              step="0.01"
              className="w-full px-4 py-3 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
              placeholder="0,00"
            />
            <p className="text-xs text-muted-foreground mt-1">
              Saldo atual da conta ao criar
            </p>
          </div>

          {/* Moeda */}
          <div>
            <label htmlFor="currency" className="block text-sm font-medium mb-2">
              Moeda
            </label>
            <select
              id="currency"
              name="currency"
              value={formData.currency}
              onChange={handleChange}
              className="w-full px-4 py-3 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
            >
              {currencies.map((currency) => (
                <option key={currency.value} value={currency.value}>
                  {currency.label}
                </option>
              ))}
            </select>
          </div>

          {/* Banco */}
          <div>
            <label htmlFor="bank_name" className="block text-sm font-medium mb-2">
              Nome do Banco
            </label>
            <input
              id="bank_name"
              type="text"
              name="bank_name"
              value={formData.bank_name}
              onChange={handleChange}
              maxLength={255}
              className="w-full px-4 py-3 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
              placeholder="Ex: Banco do Brasil, Nubank..."
            />
          </div>

          {/* Número da Conta */}
          <div>
            <label htmlFor="account_number" className="block text-sm font-medium mb-2">
              Número da Conta
            </label>
            <input
              id="account_number"
              type="text"
              name="account_number"
              value={formData.account_number}
              onChange={handleChange}
              maxLength={100}
              className="w-full px-4 py-3 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
              placeholder="Ex: 12345-6"
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
              rows={4}
              maxLength={500}
              className="w-full px-4 py-3 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all resize-none"
              placeholder="Informações adicionais sobre esta conta..."
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
              disabled={loading}
              className="flex-1 px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium"
            >
              {loading ? 'Criando...' : 'Criar Conta'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

