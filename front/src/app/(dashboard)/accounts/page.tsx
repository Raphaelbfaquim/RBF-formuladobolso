'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import apiClient from '@/lib/api/client'
import toast from 'react-hot-toast'

export default function AccountsPage() {
  const router = useRouter()
  const [loading, setLoading] = useState(true)
  const [accounts, setAccounts] = useState<any[]>([])

  useEffect(() => {
    loadAccounts()
  }, [])

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
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold mb-2">Contas</h1>
            <p className="text-muted-foreground">Gerencie suas contas financeiras</p>
          </div>
          <button
            onClick={() => router.push('/accounts/new')}
            className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
          >
            Nova Conta
          </button>
        </div>

        {loading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-500 mx-auto"></div>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {accounts.length > 0 ? (
              accounts.map((account) => (
                <div key={account.id} className="glass rounded-xl p-6">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-xl font-semibold">{account.name}</h3>
                    <span className="text-2xl">🏦</span>
                  </div>
                  <p className="text-sm text-muted-foreground mb-2 capitalize">
                    {account.account_type}
                  </p>
                  <p className="text-3xl font-bold mb-4">
                    {new Intl.NumberFormat('pt-BR', {
                      style: 'currency',
                      currency: account.currency || 'BRL'
                    }).format(account.balance)}
                  </p>
                  <div className="flex gap-2">
                    <button className="flex-1 px-3 py-2 bg-indigo-500/20 text-indigo-400 rounded-lg hover:bg-indigo-500/30 text-sm">
                      Ver Detalhes
                    </button>
                  </div>
                </div>
              ))
            ) : (
              <div className="col-span-full text-center py-12 glass rounded-xl">
                <p className="text-muted-foreground mb-4">Nenhuma conta encontrada</p>
                <button
                  onClick={() => router.push('/accounts/new')}
                  className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
                >
                  Criar Primeira Conta
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

