'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import apiClient from '@/lib/api/client'
import toast from 'react-hot-toast'
import { useWorkspace } from '@/components/providers/workspace-provider'

const WORKSPACE_TYPES = [
  { value: 'personal', label: 'Pessoal', icon: '👤' },
  { value: 'family', label: 'Familiar', icon: '👨‍👩‍👧‍👦' },
  { value: 'shared', label: 'Compartilhado', icon: '👥' }
]

const ICONS = ['💼', '🏠', '💳', '💰', '📊', '🎯', '✈️', '🎓', '🏥', '🚗', '🛍️', '🍔', '🎬', '⚽', '📱']

const COLORS = [
  '#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6',
  '#ec4899', '#06b6d4', '#84cc16', '#f97316', '#6366f1'
]

export default function NewWorkspacePage() {
  const router = useRouter()
  const { loadWorkspaces, setCurrentWorkspace } = useWorkspace()
  const [loading, setLoading] = useState(false)
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    workspace_type: 'personal',
    color: '#3b82f6',
    icon: '💼'
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    try {
      const response = await apiClient.post('/workspaces', formData)
      toast.success('Workspace criado com sucesso!')
      await loadWorkspaces()
      setCurrentWorkspace(response.data)
      router.push('/workspaces')
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Erro ao criar workspace')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-2xl mx-auto">
        <h1 className="text-3xl font-bold mb-6">Novo Workspace</h1>

        <form onSubmit={handleSubmit} className="glass rounded-xl p-6 space-y-6">
          <div>
            <label className="block text-sm font-medium mb-1">Nome do Workspace *</label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="w-full px-3 py-2 bg-background border border-border rounded-lg"
              required
              placeholder="Ex: Finanças Pessoais, Casa, Viagem..."
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Tipo de Workspace *</label>
            <div className="grid grid-cols-3 gap-3">
              {WORKSPACE_TYPES.map((type) => (
                <button
                  key={type.value}
                  type="button"
                  onClick={() => setFormData({ ...formData, workspace_type: type.value })}
                  className={`p-4 rounded-lg border-2 transition-colors ${
                    formData.workspace_type === type.value
                      ? 'border-indigo-500 bg-indigo-500/10'
                      : 'border-border hover:border-indigo-500/50'
                  }`}
                >
                  <div className="text-2xl mb-2">{type.icon}</div>
                  <div className="text-sm font-medium">{type.label}</div>
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Ícone</label>
            <div className="flex flex-wrap gap-2">
              {ICONS.map((icon) => (
                <button
                  key={icon}
                  type="button"
                  onClick={() => setFormData({ ...formData, icon })}
                  className={`w-10 h-10 rounded-lg text-xl flex items-center justify-center transition-colors ${
                    formData.icon === icon
                      ? 'bg-indigo-500 text-white'
                      : 'bg-background border border-border hover:bg-muted'
                  }`}
                >
                  {icon}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Cor</label>
            <div className="flex flex-wrap gap-2">
              {COLORS.map((color) => (
                <button
                  key={color}
                  type="button"
                  onClick={() => setFormData({ ...formData, color })}
                  className={`w-10 h-10 rounded-lg transition-all ${
                    formData.color === color
                      ? 'ring-2 ring-offset-2 ring-indigo-500'
                      : ''
                  }`}
                  style={{ backgroundColor: color }}
                />
              ))}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Descrição</label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              className="w-full px-3 py-2 bg-background border border-border rounded-lg"
              rows={3}
              placeholder="Descreva o propósito deste workspace..."
            />
          </div>

          <div className="flex gap-3 pt-4">
            <button
              type="submit"
              disabled={loading}
              className="flex-1 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 font-medium disabled:opacity-50"
            >
              {loading ? 'Criando...' : 'Criar Workspace'}
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

