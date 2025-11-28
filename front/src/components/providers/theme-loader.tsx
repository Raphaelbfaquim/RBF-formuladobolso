'use client'

import { useUserTheme } from '@/components/hooks/use-user-theme'

/**
 * Componente que carrega o tema do usuário do backend
 * Deve ser usado dentro do ThemeProvider
 */
export function ThemeLoader() {
  useUserTheme()
  return null
}

