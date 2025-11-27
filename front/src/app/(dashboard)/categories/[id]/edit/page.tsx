'use client'

import { useState, useEffect } from 'react'
import { useRouter, useParams } from 'next/navigation'
import Link from 'next/link'
import apiClient from '@/lib/api/client'
import toast from 'react-hot-toast'

const categoryIcons = [
  '💰', '🍔', '🚗', '🏠', '💊', '👕', '🎮', '📱', '💻', '🎬',
  '✈️', '🏖️', '🎓', '💼', '🏥', '🛒', '🍕', '☕', '🍺', '🎁',
  '💳', '📺', '🎵', '📚', '⚽', '🏋️', '💅', '✂️', '🔧', '⚡'
]

const categoryColors = [
  '#6366f1', '#8b5cf6', '#ec4899', '#f43f5e', '#ef4444',
  '#f59e0b', '#eab308', '#84cc16', '#22c55e', '#10b981',
  '#14b8a6', '#06b6d4', '#3b82f6', '#2563eb', '#6366f1'
]

export default function EditCategoryPage() {
  const router = useRouter()
  const params = useParams()
  const categoryId = params?.id as string
  
  const [loading, setLoading] = useState(false)
  const [loadingData, setLoadingData] = useState(true)
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    category_type: 'expense' as 'income' | 'expense' | 'transfer',
    icon: '💰',
    color: '#6366f1',
    is_active: true,
  })

  useEffect(() => {
    if (categoryId) {
      loadCategory()
    }
  }, [categoryId])

  const loadCategory = async () => {
    try {
      const response = await apiClient.get(`/categories/${categoryId}`)
      const category = response.data
      setFormData({
        name: category.name || '',
        description: category.description || '',
        category_type: category.category_type || 'expense',
        icon: category.icon || '💰',
        color: category.color || '#6366f1',
        is_active: category.is_active !== undefined ? category.is_active : true,
      })
    } catch (error: any) {
      if (error.response?.status === 401) {
        router.push('/login')
      } else if (error.response?.status === 404) {
        toast.error('Categoria não encontrada')
        router.push('/categories')
      } else {
        toast.error('Erro ao carregar categoria')
      }
    } finally {
      setLoadingData(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!formData.name.trim()) {
      toast.error('Nome da categoria é obrigatório')
      return
    }

    setLoading(true)

    try {
      const payload = {
        name: formData.name,
        description: formData.description || null,
        category_type: formData.category_type,
        icon: formData.icon || null,
        color: formData.color || null,
        is_active: formData.is_active,
      }

      await apiClient.put(`/categories/${categoryId}`, payload)
      
      toast.success('Categoria atualizada com sucesso!')
      router.push('/categories')
    } catch (error: any) {
      console.error('Erro ao atualizar categoria:', error)
      const errorMessage = error.response?.data?.detail || error.message || 'Erro ao atualizar categoria'
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

  if (loadingData) {
    return (
      <div className="min-h-screen bg-background p-6">
        <div className="max-w-3xl mx-auto">
          <div className="glass rounded-xl p-8 text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-500 mx-auto"></div>
            <p className="mt-4 text-muted-foreground">Carregando categoria...</p>
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
              href="/categories"
              className="text-muted-foreground hover:text-foreground transition-colors"
            >
              ← Voltar
            </Link>
          </div>
          <h1 className="text-3xl font-bold mb-2">Editar Categoria</h1>
          <p className="text-muted-foreground">Atualize as informações da categoria</p>
        </div>

        <form onSubmit={handleSubmit} className="glass rounded-xl p-6 space-y-6">
          {/* Nome */}
          <div>
            <label htmlFor="name" className="block text-sm font-medium mb-2">
              Nome da Categoria *
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
              placeholder="Ex: Alimentação, Transporte, Salário..."
            />
          </div>

          {/* Tipo de Categoria */}
          <div>
            <label className="block text-sm font-medium mb-2">
              Tipo de Categoria *
            </label>
            <div className="grid grid-cols-3 gap-3">
              <label className="cursor-pointer">
                <input
                  type="radio"
                  name="category_type"
                  value="income"
                  checked={formData.category_type === 'income'}
                  onChange={handleChange}
                  className="sr-only"
                />
                <div className={`p-4 rounded-lg border-2 transition-all ${
                  formData.category_type === 'income'
                    ? 'border-green-500 bg-green-500/10'
                    : 'border-border hover:border-green-500/50'
                }`}>
                  <div className="text-center">
                    <div className="text-2xl mb-2">📈</div>
                    <p className="text-sm font-medium">Receita</p>
                  </div>
                </div>
              </label>
              <label className="cursor-pointer">
                <input
                  type="radio"
                  name="category_type"
                  value="expense"
                  checked={formData.category_type === 'expense'}
                  onChange={handleChange}
                  className="sr-only"
                />
                <div className={`p-4 rounded-lg border-2 transition-all ${
                  formData.category_type === 'expense'
                    ? 'border-red-500 bg-red-500/10'
                    : 'border-border hover:border-red-500/50'
                }`}>
                  <div className="text-center">
                    <div className="text-2xl mb-2">📉</div>
                    <p className="text-sm font-medium">Despesa</p>
                  </div>
                </div>
              </label>
              <label className="cursor-pointer">
                <input
                  type="radio"
                  name="category_type"
                  value="transfer"
                  checked={formData.category_type === 'transfer'}
                  onChange={handleChange}
                  className="sr-only"
                />
                <div className={`p-4 rounded-lg border-2 transition-all ${
                  formData.category_type === 'transfer'
                    ? 'border-blue-500 bg-blue-500/10'
                    : 'border-border hover:border-blue-500/50'
                }`}>
                  <div className="text-center">
                    <div className="text-2xl mb-2">🔄</div>
                    <p className="text-sm font-medium">Transferência</p>
                  </div>
                </div>
              </label>
            </div>
          </div>

          {/* Ícone */}
          <div>
            <label className="block text-sm font-medium mb-2">
              Ícone
            </label>
            <div className="grid grid-cols-10 gap-2">
              {categoryIcons.map((icon) => (
                <label key={icon} className="cursor-pointer">
                  <input
                    type="radio"
                    name="icon"
                    value={icon}
                    checked={formData.icon === icon}
                    onChange={handleChange}
                    className="sr-only"
                  />
                  <div className={`w-12 h-12 rounded-lg border-2 flex items-center justify-center text-2xl transition-all ${
                    formData.icon === icon
                      ? 'border-indigo-500 bg-indigo-500/10'
                      : 'border-border hover:border-indigo-500/50'
                  }`}>
                    {icon}
                  </div>
                </label>
              ))}
            </div>
          </div>

          {/* Cor */}
          <div>
            <label className="block text-sm font-medium mb-2">
              Cor
            </label>
            <div className="grid grid-cols-10 gap-2 mb-3">
              {categoryColors.map((color) => (
                <label key={color} className="cursor-pointer">
                  <input
                    type="radio"
                    name="color"
                    value={color}
                    checked={formData.color === color}
                    onChange={handleChange}
                    className="sr-only"
                  />
                  <div
                    className={`w-10 h-10 rounded-lg border-2 transition-all ${
                      formData.color === color
                        ? 'border-white scale-110'
                        : 'border-border hover:scale-105'
                    }`}
                    style={{ backgroundColor: color }}
                  />
                </label>
              ))}
            </div>
            <input
              type="color"
              name="color"
              value={formData.color}
              onChange={handleChange}
              className="w-full h-12 rounded-lg cursor-pointer"
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
              placeholder="Descrição opcional da categoria..."
            />
          </div>

          {/* Status */}
          <div>
            <label className="flex items-center gap-3 cursor-pointer">
              <input
                type="checkbox"
                name="is_active"
                checked={formData.is_active}
                onChange={handleChange}
                className="w-5 h-5 rounded border-border text-indigo-600 focus:ring-indigo-500"
              />
              <span className="text-sm font-medium">Categoria ativa</span>
            </label>
            <p className="text-xs text-muted-foreground mt-1 ml-8">
              Categorias inativas não aparecerão nas listagens
            </p>
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
              {loading ? 'Salvando...' : 'Salvar Alterações'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

