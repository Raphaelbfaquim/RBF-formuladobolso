'use client'

import { useEffect, useState } from 'react'
import { useRouter, useParams } from 'next/navigation'
import apiClient from '@/lib/api/client'
import toast from 'react-hot-toast'

const ACCOUNT_TYPES = [
  { value: 'stock_broker', label: 'Corretora' },
  { value: 'bank', label: 'Banco' },
  { value: 'crypto_exchange', label: 'Exchange' },
  { value: 'investment_platform', label: 'Plataforma' },
  { value: 'other', label: 'Outros' }
]

export default function EditInvestmentAccountPage() {
  const router = useRouter()
  const params = useParams()
  const accountId = params.id as string
  const [loading, setLoading] = useState(false)
  const [loadingData, setLoadingData] = useState(true)
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    account_type: 'stock_broker',
    institution_name: '',
    account_number: '',
    is_active: true
  })

  useEffect(() => {
    loadAccount()
  }, [accountId])

  const loadAccount = async () => {
    setLoadingData(true)
    try {
      const response = await apiClient.get(`/investments/accounts/${accountId}`)
      const account = response.data
      setFormData({
        name: account.name || '',
        description: account.description || '',
        account_type: account.account_type || 'stock_broker',
        institution_name: account.institution_name || '',
        account_number: account.account_number || '',
        is_active: account.is_active !== undefined ? account.is_active : true
      })
    } catch (error: any) {
      toast.error('Erro ao carregar conta')
      router.push('/investments/accounts')
    } finally {
      setLoadingData(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    try {
      await apiClient.put(`/investments/accounts/${accountId}`, formData)
      toast.success('Conta atualizada com sucesso!')
      router.push('/investments/accounts')
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Erro ao atualizar conta')
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
        <h1 className="text-3xl font-bold mb-6">Editar Conta de Investimento</h1>

        <form onSubmit={handleSubmit} className="glass rounded-xl p-6 space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">Nome da Conta *</label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="w-full px-3 py-2 bg-background border border-border rounded-lg"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Tipo de Conta *</label>
            <select
              value={formData.account_type}
              onChange={(e) => setFormData({ ...formData, account_type: e.target.value })}
              className="w-full px-3 py-2 bg-background border border-border rounded-lg"
              required
            >
              {ACCOUNT_TYPES.map((type) => (
                <option key={type.value} value={type.value}>
                  {type.label}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Instituição</label>
            <input
              type="text"
              value={formData.institution_name}
              onChange={(e) => setFormData({ ...formData, institution_name: e.target.value })}
              className="w-full px-3 py-2 bg-background border border-border rounded-lg"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Número da Conta</label>
            <input
              type="text"
              value={formData.account_number}
              onChange={(e) => setFormData({ ...formData, account_number: e.target.value })}
              className="w-full px-3 py-2 bg-background border border-border rounded-lg"
            />
          </div>

          <div>
            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={formData.is_active}
                onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                className="w-4 h-4"
              />
              <span className="text-sm font-medium">Conta Ativa</span>
            </label>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Descrição</label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
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


