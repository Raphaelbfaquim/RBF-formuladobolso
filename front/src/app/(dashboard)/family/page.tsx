'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import apiClient from '@/lib/api/client'
import toast from 'react-hot-toast'

interface Family {
  id: string
  name: string
  description: string | null
  created_by: string
  created_at: string
  updated_at: string
}

interface Permission {
  id: string
  family_member_id: string
  module: string
  can_view: boolean
  can_edit: boolean
  can_delete: boolean
}

interface FamilyMember {
  id: string
  family_id: string
  user_id: string
  role: 'owner' | 'admin' | 'member' | 'viewer'
  joined_at: string
  user_username: string | null
  user_email: string | null
  permissions: Permission[]
}

const MODULES = [
  { id: 'dashboard', name: 'Dashboard', icon: '📊' },
  { id: 'transactions', name: 'Transações', icon: '💸' },
  { id: 'accounts', name: 'Contas', icon: '🏦' },
  { id: 'categories', name: 'Categorias', icon: '📁' },
  { id: 'planning', name: 'Planejamento', icon: '📅' },
  { id: 'goals', name: 'Metas', icon: '🎯' },
  { id: 'bills', name: 'Contas a Pagar', icon: '📋' },
  { id: 'transfers', name: 'Transferências', icon: '🔄' },
  { id: 'calendar', name: 'Calendário', icon: '📆' },
  { id: 'investments', name: 'Investimentos', icon: '📈' },
  { id: 'receipts', name: 'Notas Fiscais', icon: '🧾' },
  { id: 'reports', name: 'Relatórios', icon: '📊' },
  { id: 'workspaces', name: 'Workspaces', icon: '💼' },
  { id: 'ai', name: 'IA Assistant', icon: '🤖' },
  { id: 'insights', name: 'Insights', icon: '💡' },
  { id: 'open_banking', name: 'Open Banking', icon: '🏛️' },
  { id: 'education', name: 'Educação', icon: '📚' },
  { id: 'gamification', name: 'Gamificação', icon: '🏆' },
  { id: 'family', name: 'Família', icon: '👨‍👩‍👧‍👦' },
  { id: 'settings', name: 'Configurações', icon: '⚙️' },
]

const ROLE_LABELS: Record<string, string> = {
  owner: 'Proprietário',
  admin: 'Administrador',
  member: 'Membro',
  viewer: 'Visualizador',
}

const ROLE_COLORS: Record<string, string> = {
  owner: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
  admin: 'bg-purple-500/20 text-purple-400 border-purple-500/30',
  member: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
  viewer: 'bg-gray-500/20 text-gray-400 border-gray-500/30',
}

export default function FamilyPage() {
  const router = useRouter()
  const [loading, setLoading] = useState(true)
  const [families, setFamilies] = useState<Family[]>([])
  const [selectedFamily, setSelectedFamily] = useState<Family | null>(null)
  const [members, setMembers] = useState<FamilyMember[]>([])
  const [showCreateFamily, setShowCreateFamily] = useState(false)
  const [showInviteMember, setShowInviteMember] = useState(false)
  const [editingMember, setEditingMember] = useState<FamilyMember | null>(null)
  
  const [newFamilyName, setNewFamilyName] = useState('')
  const [newFamilyDescription, setNewFamilyDescription] = useState('')
  const [inviteEmail, setInviteEmail] = useState('')
  const [inviteRole, setInviteRole] = useState<'admin' | 'member' | 'viewer'>('member')

  useEffect(() => {
    loadFamilies()
  }, [])

  useEffect(() => {
    if (selectedFamily) {
      loadMembers()
    }
  }, [selectedFamily])

  const loadFamilies = async () => {
    setLoading(true)
    try {
      const response = await apiClient.get('/family')
      setFamilies(response.data || [])
      if (response.data && response.data.length > 0 && !selectedFamily) {
        setSelectedFamily(response.data[0])
      }
    } catch (error: any) {
      if (error.response?.status === 401) {
        router.push('/login')
      } else {
        toast.error('Erro ao carregar famílias')
      }
    } finally {
      setLoading(false)
    }
  }

  const loadMembers = async () => {
    if (!selectedFamily) return
    
    try {
      const response = await apiClient.get(`/family/${selectedFamily.id}/members`)
      setMembers(response.data || [])
    } catch (error: any) {
      if (error.response?.status === 401) {
        router.push('/login')
      } else {
        toast.error('Erro ao carregar membros')
      }
    }
  }

  const handleCreateFamily = async () => {
    if (!newFamilyName.trim()) {
      toast.error('Nome da família é obrigatório')
      return
    }

    try {
      const response = await apiClient.post('/family', {
        name: newFamilyName,
        description: newFamilyDescription || null,
      })
      toast.success('Família criada com sucesso!')
      setShowCreateFamily(false)
      setNewFamilyName('')
      setNewFamilyDescription('')
      await loadFamilies()
      setSelectedFamily(response.data)
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Erro ao criar família')
    }
  }

  const handleInviteMember = async () => {
    if (!selectedFamily || !inviteEmail.trim()) {
      toast.error('Email é obrigatório')
      return
    }

    try {
      const response = await apiClient.post(`/family/${selectedFamily.id}/invite`, {
        user_email: inviteEmail,
        role: inviteRole,
      })
      const data = response.data || {}
      if (data.status === 'invite_sent') {
        const message = data.resent 
          ? 'Convite reenviado por email! O usuário receberá um novo link para criar a conta.'
          : 'Convite enviado por email! O usuário receberá um link para criar a conta.'
        toast.success(message)
      } else if (data.status === 'invite_created' && data.signup_url) {
        // Email não foi enviado, mostrar link para compartilhar manualmente
        const link = data.signup_url
        // Copiar automaticamente para o clipboard
        try {
          await navigator.clipboard.writeText(link)
          // Mostrar alerta melhorado com o link
          const userConfirmed = confirm(
            `⚠️ Email não pôde ser enviado automaticamente.\n\n` +
            `O link do convite foi copiado para a área de transferência.\n\n` +
            `Link do convite:\n${link}\n\n` +
            `Clique em "OK" para continuar ou "Cancelar" para ver novamente.`
          )
          if (!userConfirmed) {
            // Se cancelar, mostrar novamente
            alert(`Link do convite:\n\n${link}\n\nCopie este link e envie manualmente para o usuário.`)
          }
          toast.success('Link copiado! Envie manualmente para o usuário.', { duration: 5000 })
        } catch (err) {
          // Fallback se clipboard não funcionar
          toast.error('Email não pôde ser enviado. Link do convite:')
          toast(link, { duration: 15000, icon: '🔗' })
          alert(`Email não pôde ser enviado automaticamente.\n\nLink do convite:\n\n${link}\n\nCopie este link e envie manualmente para o usuário.`)
        }
      } else {
        toast.success('Usuário adicionado à família com sucesso!')
        await loadMembers()
      }
      setShowInviteMember(false)
      setInviteEmail('')
      setInviteRole('member')
    } catch (error: any) {
      const status = error.response?.status
      const detail = error.response?.data?.detail || 'Erro ao convidar membro'
      
      if (status === 404) {
        toast.error(`Usuário não encontrado: ${inviteEmail}. O usuário precisa estar cadastrado no sistema antes de ser convidado.`, {
          duration: 5000,
        })
      } else if (status === 403) {
        toast.error('Você não tem permissão para convidar membros')
      } else if (status === 400) {
        toast.error(detail)
      } else {
        toast.error(detail)
      }
    }
  }

  const handleRemoveMember = async (memberId: string) => {
    if (!selectedFamily) return
    
    if (!confirm('Tem certeza que deseja remover este membro?')) {
      return
    }

    try {
      await apiClient.delete(`/family/${selectedFamily.id}/members/${memberId}`)
      toast.success('Membro removido com sucesso!')
      await loadMembers()
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Erro ao remover membro')
    }
  }

  const handleUpdatePermissions = async (member: FamilyMember, permissions: Permission[]) => {
    if (!selectedFamily) return

    try {
      const permissionUpdates = permissions.map(p => ({
        module: p.module,
        can_view: p.can_view,
        can_edit: p.can_edit,
        can_delete: p.can_delete,
      }))

      await apiClient.put(
        `/family/${selectedFamily.id}/members/${member.id}/permissions`,
        permissionUpdates
      )
      toast.success('Permissões atualizadas com sucesso!')
      setEditingMember(null)
      await loadMembers()
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Erro ao atualizar permissões')
    }
  }

  const getMemberPermission = (member: FamilyMember, moduleId: string): Permission | null => {
    return member.permissions.find(p => p.module === moduleId) || null
  }

  const updatePermission = (
    member: FamilyMember,
    moduleId: string,
    field: 'can_view' | 'can_edit' | 'can_delete',
    value: boolean
  ) => {
    const updatedMembers = members.map(m => {
      if (m.id !== member.id) return m

      const existingPerm = getMemberPermission(m, moduleId)
      const updatedPermissions = [...m.permissions]

      if (existingPerm) {
        const permIndex = updatedPermissions.findIndex(p => p.id === existingPerm.id)
        updatedPermissions[permIndex] = {
          ...existingPerm,
          [field]: value,
        }
      } else {
        updatedPermissions.push({
          id: `temp-${Date.now()}`,
          family_member_id: m.id,
          module: moduleId,
          can_view: field === 'can_view' ? value : false,
          can_edit: field === 'can_edit' ? value : false,
          can_delete: field === 'can_delete' ? value : false,
        })
      }

      return {
        ...m,
        permissions: updatedPermissions,
      }
    })

    setMembers(updatedMembers)
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-500 mx-auto"></div>
          <p className="mt-4 text-muted-foreground">Carregando...</p>
        </div>
      </div>
    )
  }

  const currentUserMember = members.find(m => m.role === 'owner' || m.role === 'admin')
  const canManage = currentUserMember && (currentUserMember.role === 'owner' || currentUserMember.role === 'admin')

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-7xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-3xl font-bold mb-2">Gerenciamento Familiar</h1>
            <p className="text-muted-foreground">Gerencie membros e permissões da família</p>
          </div>
          <div className="flex gap-2">
            {families.length > 0 && (
              <button
                onClick={() => setShowInviteMember(true)}
                disabled={!canManage || !selectedFamily}
                className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed text-sm font-medium"
              >
                + Convidar Membro
              </button>
            )}
            <button
              onClick={() => setShowCreateFamily(true)}
              className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors text-sm font-medium"
            >
              + Criar Família
            </button>
          </div>
        </div>

        {/* Family Selector */}
        {families.length > 0 && (
          <div className="mb-6">
            <label className="block text-sm font-medium mb-2">Selecione a Família</label>
            <select
              value={selectedFamily?.id || ''}
              onChange={(e) => {
                const family = families.find(f => f.id === e.target.value)
                setSelectedFamily(family || null)
              }}
              className="w-full md:w-64 px-4 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              {families.map((family) => (
                <option key={family.id} value={family.id}>
                  {family.name}
                </option>
              ))}
            </select>
          </div>
        )}

        {/* Create Family Modal */}
        {showCreateFamily && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
            <div className="bg-card border border-border rounded-xl p-6 max-w-md w-full mx-4">
              <h2 className="text-xl font-bold mb-4">Criar Nova Família</h2>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Nome da Família</label>
                  <input
                    type="text"
                    value={newFamilyName}
                    onChange={(e) => setNewFamilyName(e.target.value)}
                    placeholder="Ex: Família Silva"
                    className="w-full px-4 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">Descrição (opcional)</label>
                  <textarea
                    value={newFamilyDescription}
                    onChange={(e) => setNewFamilyDescription(e.target.value)}
                    placeholder="Descrição da família..."
                    rows={3}
                    className="w-full px-4 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  />
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={handleCreateFamily}
                    className="flex-1 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
                  >
                    Criar
                  </button>
                  <button
                    onClick={() => {
                      setShowCreateFamily(false)
                      setNewFamilyName('')
                      setNewFamilyDescription('')
                    }}
                    className="flex-1 px-4 py-2 bg-background border border-border rounded-lg hover:bg-muted transition-colors"
                  >
                    Cancelar
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Invite Member Modal */}
        {showInviteMember && selectedFamily && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
            <div className="bg-card border border-border rounded-xl p-6 max-w-md w-full mx-4">
              <h2 className="text-xl font-bold mb-4">Convidar Membro</h2>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Email do Usuário</label>
                  <input
                    type="email"
                    value={inviteEmail}
                    onChange={(e) => setInviteEmail(e.target.value)}
                    placeholder="usuario@email.com"
                    className="w-full px-4 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">Função</label>
                  <select
                    value={inviteRole}
                    onChange={(e) => setInviteRole(e.target.value as 'admin' | 'member' | 'viewer')}
                    className="w-full px-4 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  >
                    <option value="admin">Administrador</option>
                    <option value="member">Membro</option>
                    <option value="viewer">Visualizador</option>
                  </select>
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={handleInviteMember}
                    className="flex-1 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
                  >
                    Convidar
                  </button>
                  <button
                    onClick={() => {
                      setShowInviteMember(false)
                      setInviteEmail('')
                      setInviteRole('member')
                    }}
                    className="flex-1 px-4 py-2 bg-background border border-border rounded-lg hover:bg-muted transition-colors"
                  >
                    Cancelar
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Members List */}
        {selectedFamily && (
          <div className="space-y-4">
            <h2 className="text-xl font-bold">Membros da Família</h2>
            
            {members.length === 0 ? (
              <div className="glass rounded-xl p-12 text-center">
                <p className="text-muted-foreground">Nenhum membro encontrado. Convide membros para começar!</p>
              </div>
            ) : (
              <div className="space-y-4">
                {members.map((member) => {
                  const isOwner = member.role === 'owner'
                  const canEdit = canManage && !isOwner
                  
                  return (
                    <div key={member.id} className="glass rounded-xl p-6">
                      <div className="flex items-start justify-between mb-4">
                        <div className="flex-1">
                          <div className="flex items-center gap-3 mb-2">
                            <h3 className="text-lg font-bold">
                              {member.user_username || member.user_email || 'Usuário'}
                            </h3>
                            <span className={`px-2 py-1 rounded text-xs font-medium border ${ROLE_COLORS[member.role] || ROLE_COLORS.member}`}>
                              {ROLE_LABELS[member.role] || member.role}
                            </span>
                          </div>
                          <p className="text-sm text-muted-foreground">
                            {member.user_email}
                          </p>
                          <p className="text-xs text-muted-foreground mt-1">
                            Membro desde {new Date(member.joined_at).toLocaleDateString('pt-BR')}
                          </p>
                        </div>
                        <div className="flex gap-2">
                          {canEdit && (
                            <button
                              onClick={() => setEditingMember(editingMember?.id === member.id ? null : member)}
                              className="px-3 py-1.5 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors text-sm"
                            >
                              {editingMember?.id === member.id ? 'Cancelar' : 'Gerenciar Permissões'}
                            </button>
                          )}
                          {canEdit && (
                            <button
                              onClick={() => handleRemoveMember(member.id)}
                              className="px-3 py-1.5 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors text-sm"
                            >
                              Remover
                            </button>
                          )}
                        </div>
                      </div>

                      {/* Permissions Editor */}
                      {editingMember?.id === member.id && (
                        <div className="mt-4 pt-4 border-t border-border">
                          <h4 className="font-semibold mb-4">Permissões por Módulo</h4>
                          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                            {MODULES.map((module) => {
                              const permission = getMemberPermission(member, module.id)
                              const canView = permission?.can_view ?? false
                              const canEdit = permission?.can_edit ?? false
                              const canDelete = permission?.can_delete ?? false

                              return (
                                <div
                                  key={module.id}
                                  className="p-3 bg-background/50 rounded-lg border border-border"
                                >
                                  <div className="flex items-center gap-2 mb-3">
                                    <span className="text-lg">{module.icon}</span>
                                    <span className="font-medium text-sm">{module.name}</span>
                                  </div>
                                  <div className="space-y-2">
                                    <label className="flex items-center gap-2 text-xs">
                                      <input
                                        type="checkbox"
                                        checked={canView}
                                        onChange={(e) =>
                                          updatePermission(member, module.id, 'can_view', e.target.checked)
                                        }
                                        className="w-4 h-4 rounded border-border"
                                      />
                                      <span>Visualizar</span>
                                    </label>
                                    <label className="flex items-center gap-2 text-xs">
                                      <input
                                        type="checkbox"
                                        checked={canEdit}
                                        onChange={(e) =>
                                          updatePermission(member, module.id, 'can_edit', e.target.checked)
                                        }
                                        disabled={!canView}
                                        className="w-4 h-4 rounded border-border disabled:opacity-50"
                                      />
                                      <span>Editar</span>
                                    </label>
                                    <label className="flex items-center gap-2 text-xs">
                                      <input
                                        type="checkbox"
                                        checked={canDelete}
                                        onChange={(e) =>
                                          updatePermission(member, module.id, 'can_delete', e.target.checked)
                                        }
                                        disabled={!canView || !canEdit}
                                        className="w-4 h-4 rounded border-border disabled:opacity-50"
                                      />
                                      <span>Deletar</span>
                                    </label>
                                  </div>
                                </div>
                              )
                            })}
                          </div>
                          <div className="mt-4 flex gap-2">
                            <button
                              onClick={() => handleUpdatePermissions(member, member.permissions)}
                              className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors text-sm font-medium"
                            >
                              Salvar Permissões
                            </button>
                            <button
                              onClick={() => {
                                setEditingMember(null)
                                loadMembers()
                              }}
                              className="px-4 py-2 bg-background border border-border rounded-lg hover:bg-muted transition-colors text-sm font-medium"
                            >
                              Cancelar
                            </button>
                          </div>
                        </div>
                      )}

                      {/* Permissions Summary (when not editing) */}
                      {editingMember?.id !== member.id && member.permissions.length > 0 && (
                        <div className="mt-4 pt-4 border-t border-border">
                          <h4 className="font-semibold mb-2 text-sm">Permissões Ativas</h4>
                          <div className="flex flex-wrap gap-2">
                            {member.permissions
                              .filter(p => p.can_view)
                              .map((perm) => {
                                const module = MODULES.find(m => m.id === perm.module)
                                if (!module) return null
                                
                                const actions = []
                                if (perm.can_view) actions.push('Ver')
                                if (perm.can_edit) actions.push('Editar')
                                if (perm.can_delete) actions.push('Deletar')
                                
                                return (
                                  <span
                                    key={perm.id}
                                    className="px-2 py-1 bg-indigo-500/20 text-indigo-400 rounded text-xs"
                                  >
                                    {module.icon} {module.name}: {actions.join(', ')}
                                  </span>
                                )
                              })}
                          </div>
                        </div>
                      )}
                    </div>
                  )
                })}
              </div>
            )}
          </div>
        )}

        {/* No Family Message */}
        {families.length === 0 && (
          <div className="glass rounded-xl p-12 text-center">
            <p className="text-muted-foreground mb-4">
              Você ainda não possui nenhuma família criada.
            </p>
            <button
              onClick={() => setShowCreateFamily(true)}
              className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
            >
              Criar Primeira Família
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
