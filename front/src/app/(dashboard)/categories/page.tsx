'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import apiClient from '@/lib/api/client'
import toast from 'react-hot-toast'

interface Category {
  id: string
  name: string
  description?: string
  category_type: 'income' | 'expense' | 'transfer'
  icon?: string
  color?: string
  is_active: boolean
  created_at: string
}

export default function CategoriesPage() {
  const router = useRouter()
  const [loading, setLoading] = useState(true)
  const [categories, setCategories] = useState<Category[]>([])
  const [filterType, setFilterType] = useState<'all' | 'income' | 'expense' | 'transfer'>('all')

  useEffect(() => {
    loadCategories()
  }, [])

  const loadCategories = async () => {
    try {
      const response = await apiClient.get('/categories/')
      const categoriesData = Array.isArray(response.data) ? response.data : []
      setCategories(categoriesData)
    } catch (error: any) {
      if (error.response?.status === 401) {
        router.push('/login')
      } else {
        toast.error('Erro ao carregar categorias')
      }
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (categoryId: string, categoryName: string) => {
    if (!confirm(`Tem certeza que deseja excluir a categoria "${categoryName}"?`)) {
      return
    }

    try {
      await apiClient.delete(`/categories/${categoryId}`)
      toast.success('Categoria excluída com sucesso!')
      loadCategories()
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'Erro ao excluir categoria'
      toast.error(errorMessage)
    }
  }

  const getTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      income: 'Receita',
      expense: 'Despesa',
      transfer: 'Transferência',
    }
    return labels[type] || type
  }

  const getTypeColor = (type: string) => {
    const colors: Record<string, string> = {
      income: 'bg-green-500/20 text-green-400 border-green-500/30',
      expense: 'bg-red-500/20 text-red-400 border-red-500/30',
      transfer: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
    }
    return colors[type] || 'bg-gray-500/20 text-gray-400 border-gray-500/30'
  }

  const filteredCategories = filterType === 'all'
    ? categories
    : categories.filter(cat => cat.category_type === filterType)

  const groupedCategories = {
    income: filteredCategories.filter(cat => cat.category_type === 'income'),
    expense: filteredCategories.filter(cat => cat.category_type === 'expense'),
    transfer: filteredCategories.filter(cat => cat.category_type === 'transfer'),
  }

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold mb-2">Categorias</h1>
            <p className="text-muted-foreground">Gerencie suas categorias de transações</p>
          </div>
          <button
            onClick={() => router.push('/categories/new')}
            className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors font-medium"
          >
            + Nova Categoria
          </button>
        </div>

        {/* Filtros */}
        <div className="mb-6 flex gap-2">
          <button
            onClick={() => setFilterType('all')}
            className={`px-4 py-2 rounded-lg transition-colors ${
              filterType === 'all'
                ? 'bg-indigo-600 text-white'
                : 'bg-background border border-border hover:bg-background/50'
            }`}
          >
            Todas
          </button>
          <button
            onClick={() => setFilterType('income')}
            className={`px-4 py-2 rounded-lg transition-colors ${
              filterType === 'income'
                ? 'bg-green-600 text-white'
                : 'bg-background border border-border hover:bg-background/50'
            }`}
          >
            Receitas
          </button>
          <button
            onClick={() => setFilterType('expense')}
            className={`px-4 py-2 rounded-lg transition-colors ${
              filterType === 'expense'
                ? 'bg-red-600 text-white'
                : 'bg-background border border-border hover:bg-background/50'
            }`}
          >
            Despesas
          </button>
          <button
            onClick={() => setFilterType('transfer')}
            className={`px-4 py-2 rounded-lg transition-colors ${
              filterType === 'transfer'
                ? 'bg-blue-600 text-white'
                : 'bg-background border border-border hover:bg-background/50'
            }`}
          >
            Transferências
          </button>
        </div>

        {loading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-500 mx-auto"></div>
          </div>
        ) : filteredCategories.length > 0 ? (
          <div className="space-y-6">
            {/* Receitas */}
            {groupedCategories.income.length > 0 && (filterType === 'all' || filterType === 'income') && (
              <div>
                <h2 className="text-xl font-semibold mb-4 text-green-400">📈 Receitas</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {groupedCategories.income.map((category) => (
                    <div key={category.id} className="glass rounded-xl p-6">
                      <div className="flex items-start justify-between mb-4">
                        <div className="flex items-center gap-3">
                          {category.icon && (
                            <div className="text-2xl">{category.icon}</div>
                          )}
                          <div>
                            <h3 className="text-lg font-semibold">{category.name}</h3>
                            {category.description && (
                              <p className="text-sm text-muted-foreground">{category.description}</p>
                            )}
                          </div>
                        </div>
                        <span className={`px-2 py-1 rounded text-xs border ${getTypeColor(category.category_type)}`}>
                          {getTypeLabel(category.category_type)}
                        </span>
                      </div>
                      <div className="flex gap-2">
                        <button
                          onClick={() => router.push(`/categories/${category.id}/edit`)}
                          className="flex-1 px-3 py-2 bg-indigo-500/20 text-indigo-400 rounded-lg hover:bg-indigo-500/30 text-sm transition-colors"
                        >
                          Editar
                        </button>
                        <button
                          onClick={() => handleDelete(category.id, category.name)}
                          className="px-3 py-2 bg-red-500/20 text-red-400 rounded-lg hover:bg-red-500/30 text-sm transition-colors"
                        >
                          Excluir
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Despesas */}
            {groupedCategories.expense.length > 0 && (filterType === 'all' || filterType === 'expense') && (
              <div>
                <h2 className="text-xl font-semibold mb-4 text-red-400">📉 Despesas</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {groupedCategories.expense.map((category) => (
                    <div key={category.id} className="glass rounded-xl p-6">
                      <div className="flex items-start justify-between mb-4">
                        <div className="flex items-center gap-3">
                          {category.icon && (
                            <div className="text-2xl">{category.icon}</div>
                          )}
                          <div>
                            <h3 className="text-lg font-semibold">{category.name}</h3>
                            {category.description && (
                              <p className="text-sm text-muted-foreground">{category.description}</p>
                            )}
                          </div>
                        </div>
                        <span className={`px-2 py-1 rounded text-xs border ${getTypeColor(category.category_type)}`}>
                          {getTypeLabel(category.category_type)}
                        </span>
                      </div>
                      <div className="flex gap-2">
                        <button
                          onClick={() => router.push(`/categories/${category.id}/edit`)}
                          className="flex-1 px-3 py-2 bg-indigo-500/20 text-indigo-400 rounded-lg hover:bg-indigo-500/30 text-sm transition-colors"
                        >
                          Editar
                        </button>
                        <button
                          onClick={() => handleDelete(category.id, category.name)}
                          className="px-3 py-2 bg-red-500/20 text-red-400 rounded-lg hover:bg-red-500/30 text-sm transition-colors"
                        >
                          Excluir
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Transferências */}
            {groupedCategories.transfer.length > 0 && (filterType === 'all' || filterType === 'transfer') && (
              <div>
                <h2 className="text-xl font-semibold mb-4 text-blue-400">🔄 Transferências</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {groupedCategories.transfer.map((category) => (
                    <div key={category.id} className="glass rounded-xl p-6">
                      <div className="flex items-start justify-between mb-4">
                        <div className="flex items-center gap-3">
                          {category.icon && (
                            <div className="text-2xl">{category.icon}</div>
                          )}
                          <div>
                            <h3 className="text-lg font-semibold">{category.name}</h3>
                            {category.description && (
                              <p className="text-sm text-muted-foreground">{category.description}</p>
                            )}
                          </div>
                        </div>
                        <span className={`px-2 py-1 rounded text-xs border ${getTypeColor(category.category_type)}`}>
                          {getTypeLabel(category.category_type)}
                        </span>
                      </div>
                      <div className="flex gap-2">
                        <button
                          onClick={() => router.push(`/categories/${category.id}/edit`)}
                          className="flex-1 px-3 py-2 bg-indigo-500/20 text-indigo-400 rounded-lg hover:bg-indigo-500/30 text-sm transition-colors"
                        >
                          Editar
                        </button>
                        <button
                          onClick={() => handleDelete(category.id, category.name)}
                          className="px-3 py-2 bg-red-500/20 text-red-400 rounded-lg hover:bg-red-500/30 text-sm transition-colors"
                        >
                          Excluir
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="glass rounded-xl p-12 text-center">
            <p className="text-muted-foreground mb-4">Nenhuma categoria encontrada</p>
            <button
              onClick={() => router.push('/categories/new')}
              className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
            >
              Criar Primeira Categoria
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
