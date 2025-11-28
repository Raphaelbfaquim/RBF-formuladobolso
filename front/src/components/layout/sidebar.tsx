'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { usePathname, useRouter } from 'next/navigation'
import { authApi } from '@/lib/api/auth'
import apiClient from '@/lib/api/client'
import WorkspaceSelector from './workspace-selector'

const menuItems = [
  { name: 'Dashboard', path: '/dashboard', icon: '📊', module: 'dashboard' },
  { name: 'Transações', path: '/transactions', icon: '💸', module: 'transactions' },
  { name: 'Contas', path: '/accounts', icon: '🏦', module: 'accounts' },
  { name: 'Categorias', path: '/categories', icon: '📁', module: 'categories' },
  { name: 'Planejamento', path: '/planning', icon: '📅', module: 'planning' },
  { name: 'Metas', path: '/goals', icon: '🎯', module: 'goals' },
  { name: 'Contas a Pagar', path: '/bills', icon: '📋', module: 'bills' },
  { name: 'Transferências', path: '/transfers', icon: '🔄', module: 'transfers' },
  { name: 'Calendário', path: '/calendar', icon: '📆', module: 'calendar' },
  { name: 'Investimentos', path: '/investments', icon: '📈', module: 'investments' },
  { name: 'Notas Fiscais', path: '/receipts', icon: '🧾', module: 'receipts' },
  { name: 'Relatórios', path: '/reports', icon: '📊', module: 'reports' },
  { name: 'Workspaces', path: '/workspaces', icon: '💼', module: 'workspaces' },
  { name: 'IA Assistant', path: '/ai', icon: '🤖', module: 'ai' },
  { name: 'Insights', path: '/insights', icon: '💡', module: 'insights' },
  { name: 'Open Banking', path: '/open-banking', icon: '🏛️', module: 'open_banking' },
  { name: 'Educação', path: '/education', icon: '📚', module: 'education' },
  { name: 'Gamificação', path: '/gamification', icon: '🏆', module: 'gamification' },
  { name: 'Família', path: '/family', icon: '👨‍👩‍👧‍👦', module: 'family' },
  { name: 'Configurações', path: '/settings', icon: '⚙️', module: 'settings' },
  { name: 'Admin', path: '/admin', icon: '🛡️', module: 'admin', adminOnly: true },
]

export default function Sidebar() {
  const pathname = usePathname()
  const router = useRouter()
  const [userPermissions, setUserPermissions] = useState<Record<string, any>>({})
  const [hasFamily, setHasFamily] = useState(false)
  const [isOwnerOrAdmin, setIsOwnerOrAdmin] = useState(false)
  const [isMounted, setIsMounted] = useState(false)
  const [user, setUser] = useState<any>(null)

  useEffect(() => {
    setIsMounted(true)
    loadUser()
    loadPermissions()
  }, [])

  const loadUser = async () => {
    try {
      const response = await apiClient.get('/users/me')
      setUser(response.data)
    } catch (error: any) {
      console.log('Erro ao carregar usuário:', error)
    }
  }

  const loadPermissions = async () => {
    try {
      const response = await apiClient.get('/family/my-permissions')
      const data = response.data || {}
      setUserPermissions(data.permissions_by_family || {})
      setHasFamily(data.has_any_family || false)
      setIsOwnerOrAdmin(data.is_owner_or_admin || false)
    } catch (error: any) {
      // Se não tiver família ou não conseguir carregar, mostrar todos os itens
      console.log('Não foi possível carregar permissões:', error)
      setHasFamily(false)
      setIsOwnerOrAdmin(false)
    }
  }

  const hasPermission = (module: string): boolean => {
    // Se não tem família, mostrar todos os itens (usuário não está em família)
    if (!hasFamily) {
      return true
    }

    // Se for OWNER ou ADMIN, sempre mostrar todos os itens
    if (isOwnerOrAdmin) {
      return true
    }

    // Verificar permissões em todas as famílias
    // Se tiver permissão de visualização em pelo menos uma família, mostrar o item
    for (const familyId in userPermissions) {
      const familyPerms = userPermissions[familyId]
      if (familyPerms?.permissions?.[module]?.can_view) {
        return true
      }
    }

    return false
  }

  const handleLogout = () => {
    authApi.logout()
    router.push('/login')
  }

  return (
    <div className="w-64 bg-card border-r border-border h-screen fixed left-0 top-0 overflow-y-auto">
      <div className="p-6">
        <Link href="/dashboard" className="flex items-center gap-2 mb-6">
          <span className="text-2xl">💰</span>
          <h1 className="text-xl font-bold bg-gradient-to-r from-indigo-500 to-purple-500 bg-clip-text text-transparent">
            FormuladoBolso
          </h1>
        </Link>

        {/* Workspace Selector */}
        <div className="mb-6">
          <WorkspaceSelector />
        </div>

        <nav className="space-y-1">
          {menuItems.map((item) => {
            // Verificar se é item apenas para admin
            if (item.adminOnly && user?.role !== 'admin' && user?.role !== 'ADMIN') {
              return null
            }

            // Verificar se o usuário tem permissão para ver este módulo
            const canView = hasPermission(item.module || '')
            
            // Se não tiver permissão e estiver em uma família, não mostrar o item
            if (!canView && hasFamily) {
              return null
            }

            const isActive = pathname === item.path
            return (
              <Link
                key={item.path}
                href={item.path}
                className={`flex items-center gap-3 px-4 py-2 rounded-lg transition-colors ${
                  isActive
                    ? 'bg-indigo-500/20 text-indigo-400 border border-indigo-500/30'
                    : 'text-muted-foreground hover:bg-background hover:text-foreground'
                }`}
              >
                <span className="text-lg">{item.icon}</span>
                <span className="font-medium">{item.name}</span>
              </Link>
            )
          })}
        </nav>

        <div className="mt-8 pt-8 border-t border-border">
          <button
            onClick={handleLogout}
            className="w-full flex items-center gap-3 px-4 py-2 rounded-lg text-red-400 hover:bg-red-500/10 transition-colors"
          >
            <span>🚪</span>
            <span className="font-medium">Sair</span>
          </button>
        </div>
      </div>
    </div>
  )
}

