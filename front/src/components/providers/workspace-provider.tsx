'use client'

import { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import apiClient from '@/lib/api/client'

interface Workspace {
  id: string
  name: string
  description: string | null
  workspace_type: string
  owner_id: string
  family_id: string | null
  is_active: boolean
  color: string | null
  icon: string | null
  created_at: string
  updated_at: string
}

interface WorkspaceContextType {
  currentWorkspace: Workspace | null
  workspaces: Workspace[]
  setCurrentWorkspace: (workspace: Workspace | null) => void
  loadWorkspaces: () => Promise<void>
  loading: boolean
}

const WorkspaceContext = createContext<WorkspaceContextType | undefined>(undefined)

export function WorkspaceProvider({ children }: { children: ReactNode }) {
  const [currentWorkspace, setCurrentWorkspaceState] = useState<Workspace | null>(null)
  const [workspaces, setWorkspaces] = useState<Workspace[]>([])
  const [loading, setLoading] = useState(true)

  const loadWorkspaces = async () => {
    try {
      // Verificar se há token antes de fazer a requisição
      if (typeof window === 'undefined') {
        setLoading(false)
        return
      }
      
      const token = localStorage.getItem('access_token') || sessionStorage.getItem('access_token')
      if (!token) {
        setLoading(false)
        setWorkspaces([])
        setCurrentWorkspaceState(null)
        return
      }

      const response = await apiClient.get('/workspaces')
      setWorkspaces(response.data || [])
      
      // Restaurar workspace selecionado do localStorage
      const savedWorkspaceId = localStorage.getItem('selectedWorkspaceId')
      if (savedWorkspaceId && response.data) {
        const saved = response.data.find((w: Workspace) => w.id === savedWorkspaceId)
        if (saved) {
          setCurrentWorkspaceState(saved)
        } else {
          // Se o workspace salvo não existe mais, usar o primeiro disponível
          if (response.data.length > 0) {
            setCurrentWorkspaceState(response.data[0])
            localStorage.setItem('selectedWorkspaceId', response.data[0].id)
          } else {
            setCurrentWorkspaceState(null)
            localStorage.removeItem('selectedWorkspaceId')
          }
        }
      } else if (response.data && response.data.length > 0) {
        // Se não há workspace salvo, usar o primeiro
        setCurrentWorkspaceState(response.data[0])
        localStorage.setItem('selectedWorkspaceId', response.data[0].id)
      } else {
        setCurrentWorkspaceState(null)
        localStorage.removeItem('selectedWorkspaceId')
      }
    } catch (error: any) {
      // Se der erro 401 ou qualquer erro, o usuário não está autenticado ou há problema
      console.error('Erro ao carregar workspaces:', error)
      setWorkspaces([])
      setCurrentWorkspaceState(null)
      localStorage.removeItem('selectedWorkspaceId')
    } finally {
      setLoading(false)
    }
  }

  const setCurrentWorkspace = (workspace: Workspace | null) => {
    setCurrentWorkspaceState(workspace)
    if (workspace) {
      localStorage.setItem('selectedWorkspaceId', workspace.id)
    } else {
      localStorage.removeItem('selectedWorkspaceId')
    }
  }

  useEffect(() => {
    // Só carregar workspaces se houver token de autenticação
    const checkAndLoad = () => {
      if (typeof window === 'undefined') {
        setLoading(false)
        return
      }
      
      const token = localStorage.getItem('access_token') || sessionStorage.getItem('access_token')
      if (token) {
        loadWorkspaces()
      } else {
        setLoading(false)
        setWorkspaces([])
        setCurrentWorkspaceState(null)
      }
    }
    
    checkAndLoad()
  }, [])

  return (
    <WorkspaceContext.Provider
      value={{
        currentWorkspace,
        workspaces,
        setCurrentWorkspace,
        loadWorkspaces,
        loading,
      }}
    >
      {children}
    </WorkspaceContext.Provider>
  )
}

export function useWorkspace() {
  const context = useContext(WorkspaceContext)
  if (context === undefined) {
    throw new Error('useWorkspace must be used within a WorkspaceProvider')
  }
  return context
}

