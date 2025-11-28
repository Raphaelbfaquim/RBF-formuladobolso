'use client'

import { useEffect, useRef } from 'react'
import { useTheme } from 'next-themes'
import apiClient from '@/lib/api/client'

// Flag global para garantir que só carregue uma vez
let globalThemeLoaded = false

/**
 * Hook para carregar e aplicar o tema do usuário do backend
 */
export function useUserTheme() {
  const { setTheme } = useTheme()
  const hasLoadedRef = useRef(false)

  useEffect(() => {
    // Só carregar uma vez (globalmente)
    if (hasLoadedRef.current || globalThemeLoaded) {
      return
    }

    const loadUserTheme = async () => {
      try {
        // Verificar se há token no localStorage (usuário logado)
        const token = localStorage.getItem('access_token')
        if (!token) {
          globalThemeLoaded = true
          hasLoadedRef.current = true
          return
        }

        // Tentar carregar tema do usuário do backend
        const response = await apiClient.get('/users/me')
        if (response.data?.theme_preference) {
          const userTheme = response.data.theme_preference as 'light' | 'dark' | 'system'
          
          // Aplicar imediatamente na DOM
          if (userTheme === 'system') {
            const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
            if (prefersDark) {
              document.documentElement.classList.add('dark')
            } else {
              document.documentElement.classList.remove('dark')
            }
          } else if (userTheme === 'dark') {
            document.documentElement.classList.add('dark')
          } else {
            document.documentElement.classList.remove('dark')
          }
          
          // Atualizar tema no next-themes
          setTheme(userTheme)
        }
        
        globalThemeLoaded = true
        hasLoadedRef.current = true
      } catch (error) {
        // Se não conseguir carregar (usuário não logado, etc), usar tema padrão
        // Não fazer nada, apenas silenciar o erro
        globalThemeLoaded = true
        hasLoadedRef.current = true
      }
    }

    loadUserTheme()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []) // Array vazio = executa apenas uma vez na montagem
}

