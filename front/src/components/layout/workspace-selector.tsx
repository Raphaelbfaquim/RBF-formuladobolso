'use client'

import { useState, useEffect } from 'react'
import { useWorkspace } from '../providers/workspace-provider'
import toast from 'react-hot-toast'

export default function WorkspaceSelector() {
  const [isOpen, setIsOpen] = useState(false)
  const [isMounted, setIsMounted] = useState(false)
  
  // Garantir que só verifica autenticação após montagem (evita erro de hidratação)
  useEffect(() => {
    setIsMounted(true)
  }, [])
  
  // Verificar se está autenticado apenas no cliente
  const isAuthenticated = isMounted && (
    typeof window !== 'undefined' && (
      localStorage.getItem('access_token') || sessionStorage.getItem('access_token')
    )
  )
  
  // Durante SSR ou antes da montagem, retornar estrutura vazia mas consistente
  if (!isMounted || !isAuthenticated) {
    return <div className="h-10" /> // Espaçador para manter layout consistente
  }

  let workspaceContext
  try {
    workspaceContext = useWorkspace()
  } catch (error) {
    // Se não estiver dentro do provider, não renderizar
    return <div className="h-10" />
  }

  const { currentWorkspace, workspaces, setCurrentWorkspace, loading } = workspaceContext

  const handleSelectWorkspace = async (workspace: any) => {
    setCurrentWorkspace(workspace)
    setIsOpen(false)
    toast.success(`Workspace "${workspace.name}" selecionado`)
  }

  const handleCreateWorkspace = () => {
    window.location.href = '/workspaces/new'
  }

  if (loading) {
    return (
      <div className="px-4 py-2 bg-background border border-border rounded-lg h-10 flex items-center">
        <span className="text-sm text-muted-foreground">Carregando...</span>
      </div>
    )
  }

  if (!currentWorkspace) {
    return <div className="h-10" /> // Espaçador consistente
  }

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-4 py-2 bg-background border border-border rounded-lg hover:bg-muted transition-colors"
      >
        <span className="text-lg">{currentWorkspace.icon || '💼'}</span>
        <span className="font-medium text-sm max-w-[150px] truncate">
          {currentWorkspace.name}
        </span>
        <span className="text-xs text-muted-foreground">▼</span>
      </button>

      {isOpen && (
        <>
          <div
            className="fixed inset-0 z-10"
            onClick={() => setIsOpen(false)}
          />
          <div className="absolute top-full left-0 mt-2 w-64 bg-card border border-border rounded-lg shadow-lg z-20 max-h-96 overflow-y-auto">
            <div className="p-2">
              <button
                onClick={handleCreateWorkspace}
                className="w-full px-3 py-2 text-left text-sm font-medium text-indigo-400 hover:bg-indigo-500/10 rounded-lg mb-2"
              >
                + Criar Novo Workspace
              </button>
              <div className="border-t border-border my-2" />
              {workspaces.map((workspace) => (
                <button
                  key={workspace.id}
                  onClick={() => handleSelectWorkspace(workspace)}
                  className={`w-full flex items-center gap-2 px-3 py-2 rounded-lg text-sm transition-colors ${
                    currentWorkspace.id === workspace.id
                      ? 'bg-indigo-500/20 text-indigo-400'
                      : 'hover:bg-background text-foreground'
                  }`}
                >
                  <span className="text-lg">{workspace.icon || '💼'}</span>
                  <div className="flex-1 text-left">
                    <div className="font-medium">{workspace.name}</div>
                    <div className="text-xs text-muted-foreground">
                      {workspace.workspace_type === 'personal' ? 'Pessoal' :
                       workspace.workspace_type === 'family' ? 'Familiar' :
                       'Compartilhado'}
                    </div>
                  </div>
                  {currentWorkspace.id === workspace.id && (
                    <span className="text-xs">✓</span>
                  )}
                </button>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  )
}

