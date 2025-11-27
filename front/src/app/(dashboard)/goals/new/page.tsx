'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import apiClient from '@/lib/api/client'
import toast from 'react-hot-toast'

interface Category {
  id: string
  name: string
  category_type: string
}

const GOAL_TYPES = [
  { value: 'house', label: '🏠 Casa', color: '#3B82F6' },
  { value: 'car', label: '🚗 Carro', color: '#A855F7' },
  { value: 'trip', label: '✈️ Viagem', color: '#06B6D4' },
  { value: 'wedding', label: '💍 Casamento', color: '#EC4899' },
  { value: 'education', label: '📚 Educação', color: '#10B981' },
  { value: 'emergency', label: '🚨 Emergência', color: '#EF4444' },
  { value: 'retirement', label: '👴 Aposentadoria', color: '#F97316' },
  { value: 'other', label: '🎯 Outros', color: '#6366F1' }
]

const COMMON_ICONS = ['🎯', '💰', '🏆', '⭐', '💎', '🌟', '🎁', '🎊', '🎉', '💪', '🚀', '✨']

export default function NewGoalPage() {
  const router = useRouter()
  const [loading, setLoading] = useState(false)
  const [categories, setCategories] = useState<Category[]>([])
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    goal_type: 'other',
    target_amount: '',
    target_date: '',
    icon: '🎯',
    color: '#6366F1',
    savings_category_id: '',
    auto_contribution_percentage: ''
  })

  useEffect(() => {
    loadCategories()
  }, [])

  const loadCategories = async () => {
    try {
      const response = await apiClient.get('/categories/')
      // Filtrar apenas categorias de despesa (poupança geralmente é despesa)
      const expenseCategories = (Array.isArray(response.data) ? response.data : [])
        .filter((cat: Category) => cat.category_type === 'expense')
      setCategories(expenseCategories)
    } catch (error: any) {
      console.error('Erro ao carregar categorias:', error)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    try {
      const payload: any = {
        name: formData.name,
        goal_type: formData.goal_type,
        target_amount: parseFloat(formData.target_amount),
        icon: formData.icon,
        color: formData.color
      }

      if (formData.description.trim()) {
        payload.description = formData.description
      }

      if (formData.target_date) {
        payload.target_date = new Date(formData.target_date).toISOString()
      }

      if (formData.savings_category_id) {
        payload.savings_category_id = formData.savings_category_id
      }

      if (formData.auto_contribution_percentage) {
        payload.auto_contribution_percentage = parseFloat(formData.auto_contribution_percentage)
      }

      await apiClient.post('/goals/', payload)
      toast.success('Meta criada com sucesso!')
      router.push('/goals')
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Erro ao criar meta')
    } finally {
      setLoading(false)
    }
  }

  const selectedType = GOAL_TYPES.find(t => t.value === formData.goal_type)

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-3xl mx-auto">
        <div className="mb-8">
          <button
            onClick={() => router.back()}
            className="mb-4 text-muted-foreground hover:text-foreground flex items-center gap-2"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            Voltar
          </button>
          <h1 className="text-3xl font-bold mb-2">Nova Meta</h1>
          <p className="text-muted-foreground">Crie uma nova meta financeira</p>
        </div>

        <form onSubmit={handleSubmit} className="glass rounded-xl p-6 space-y-6">
          {/* Nome */}
          <div>
            <label className="block text-sm font-medium mb-2">
              Nome da Meta <span className="text-red-400">*</span>
            </label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              required
              placeholder="Ex: Comprar casa própria"
              className="w-full px-4 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>

          {/* Descrição */}
          <div>
            <label className="block text-sm font-medium mb-2">Descrição</label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              placeholder="Descreva sua meta..."
              rows={3}
              className="w-full px-4 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>

          {/* Tipo */}
          <div>
            <label className="block text-sm font-medium mb-2">
              Tipo <span className="text-red-400">*</span>
            </label>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              {GOAL_TYPES.map((type) => (
                <button
                  key={type.value}
                  type="button"
                  onClick={() => setFormData({ ...formData, goal_type: type.value, color: type.color })}
                  className={`p-4 rounded-lg border-2 transition-all ${
                    formData.goal_type === type.value
                      ? 'border-indigo-500 bg-indigo-500/10'
                      : 'border-border hover:border-indigo-500/50'
                  }`}
                >
                  <div className="text-2xl mb-1">{type.label.split(' ')[0]}</div>
                  <div className="text-xs text-muted-foreground">{type.label.split(' ').slice(1).join(' ')}</div>
                </button>
              ))}
            </div>
          </div>

          {/* Valor e Data */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">
                Valor da Meta <span className="text-red-400">*</span>
              </label>
              <input
                type="number"
                value={formData.target_amount}
                onChange={(e) => setFormData({ ...formData, target_amount: e.target.value })}
                required
                step="0.01"
                min="0.01"
                placeholder="0.00"
                className="w-full px-4 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Data Objetivo</label>
              <input
                type="date"
                value={formData.target_date}
                onChange={(e) => setFormData({ ...formData, target_date: e.target.value })}
                className="w-full px-4 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>
          </div>

          {/* Ícone e Cor */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">Ícone</label>
              <div className="flex flex-wrap gap-2">
                {COMMON_ICONS.map((icon) => (
                  <button
                    key={icon}
                    type="button"
                    onClick={() => setFormData({ ...formData, icon })}
                    className={`w-12 h-12 text-2xl rounded-lg border-2 transition-all ${
                      formData.icon === icon
                        ? 'border-indigo-500 bg-indigo-500/10'
                        : 'border-border hover:border-indigo-500/50'
                    }`}
                  >
                    {icon}
                  </button>
                ))}
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Cor</label>
              <div className="flex items-center gap-3">
                <input
                  type="color"
                  value={formData.color}
                  onChange={(e) => setFormData({ ...formData, color: e.target.value })}
                  className="w-16 h-12 rounded-lg border border-border cursor-pointer"
                />
                <div
                  className="flex-1 h-12 rounded-lg border border-border"
                  style={{ backgroundColor: formData.color }}
                ></div>
              </div>
            </div>
          </div>

          {/* Vinculação com Categoria de Poupança */}
          <div className="p-4 bg-indigo-500/10 border border-indigo-500/20 rounded-lg">
            <h3 className="text-sm font-semibold mb-3 text-indigo-300">💡 Contribuições Automáticas</h3>
            <p className="text-xs text-muted-foreground mb-4">
              Vincule esta meta a uma categoria de poupança para contribuições automáticas quando houver transações nessa categoria.
            </p>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">Categoria de Poupança (opcional)</label>
                <select
                  value={formData.savings_category_id}
                  onChange={(e) => setFormData({ ...formData, savings_category_id: e.target.value })}
                  className="w-full px-4 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                >
                  <option value="">Nenhuma (contribuições manuais)</option>
                  {categories.map((category) => (
                    <option key={category.id} value={category.id}>
                      {category.name}
                    </option>
                  ))}
                </select>
              </div>

              {formData.savings_category_id && (
                <div>
                  <label className="block text-sm font-medium mb-2">
                    Porcentagem da Poupança para esta Meta (0-100%)
                  </label>
                  <div className="flex items-center gap-3">
                    <input
                      type="number"
                      value={formData.auto_contribution_percentage}
                      onChange={(e) => setFormData({ ...formData, auto_contribution_percentage: e.target.value })}
                      placeholder="Ex: 50"
                      step="0.01"
                      min="0"
                      max="100"
                      className="flex-1 px-4 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    />
                    <span className="text-sm text-muted-foreground">%</span>
                  </div>
                  <p className="text-xs text-muted-foreground mt-1">
                    Exemplo: Se você economizar R$ 1.000 na categoria selecionada, {formData.auto_contribution_percentage || 'X'}% (R$ {(parseFloat(formData.auto_contribution_percentage || '0') / 100 * 1000).toFixed(2)}) irá automaticamente para esta meta.
                  </p>
                </div>
              )}
            </div>
          </div>

          {/* Preview */}
          <div className="p-4 bg-background/50 rounded-lg border border-border">
            <p className="text-sm text-muted-foreground mb-2">Preview:</p>
            <div className="flex items-center gap-3">
              <span className="text-3xl">{formData.icon}</span>
              <div>
                <p className="font-semibold">{formData.name || 'Nome da Meta'}</p>
                <p className="text-sm text-muted-foreground">
                  {selectedType?.label || 'Tipo'} • {formData.target_amount ? `R$ ${parseFloat(formData.target_amount).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}` : 'R$ 0,00'}
                </p>
                {formData.savings_category_id && (
                  <p className="text-xs text-indigo-400 mt-1">
                    ✓ Contribuições automáticas ativadas
                  </p>
                )}
              </div>
            </div>
          </div>

          {/* Botões */}
          <div className="flex items-center gap-4 pt-4">
            <button
              type="button"
              onClick={() => router.back()}
              className="flex-1 px-6 py-3 bg-background border border-border rounded-lg hover:bg-muted font-medium transition-colors"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={loading}
              className="flex-1 px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 font-medium transition-colors disabled:opacity-50"
            >
              {loading ? 'Criando...' : 'Criar Meta'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

