'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
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

export default function NewCategoryPage() {
  const router = useRouter()
  const [loading, setLoading] = useState(false)
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    category_type: 'expense' as 'income' | 'expense' | 'transfer',
    icon: '💰',
    color: '#6366f1',
  })

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
      }

      await apiClient.post('/categories/', payload)
      
      toast.success('Categoria criada com sucesso!')
      router.push('/categories')
    } catch (error: any) {
      console.error('Erro ao criar categoria:', error)
      const errorMessage = error.response?.data?.detail || error.message || 'Erro ao criar categoria'
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
              href="/categories"
              className="text-muted-foreground hover:text-foreground transition-colors"
            >
              ← Voltar
            </Link>
          </div>
          <h1 className="text-3xl font-bold mb-2">Nova Categoria</h1>
          <p className="text-muted-foreground">Crie uma nova categoria para organizar suas transações</p>
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
              {loading ? 'Criando...' : 'Criar Categoria'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

