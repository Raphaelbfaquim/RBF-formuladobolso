'use client'

import { useState } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { authApi } from '@/lib/api/auth'
import toast from 'react-hot-toast'

export default function ForgotPasswordPage() {
  const router = useRouter()
  const [email, setEmail] = useState('')
  const [loading, setLoading] = useState(false)
  const [success, setSuccess] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setLoading(true)
    
    try {
      await authApi.forgotPassword(email)
      setSuccess(true)
      toast.success('Email de recuperação enviado! Verifique sua caixa de entrada.')
    } catch (error: any) {
      console.error('Erro ao solicitar recuperação:', error)
      let errorMessage = 'Erro ao solicitar recuperação de senha'
      
      if (error.response) {
        // Erro da API
        if (error.response.status === 404) {
          errorMessage = 'Endpoint não encontrado. Verifique se o backend está rodando e reinicie o servidor.'
        } else {
          errorMessage = error.response.data?.detail || error.response.data?.message || errorMessage
        }
      } else if (error.request) {
        // Erro de rede
        errorMessage = 'Não foi possível conectar ao servidor. Verifique se o backend está rodando.'
      } else {
        errorMessage = error.message || errorMessage
      }
      
      setError(errorMessage)
      toast.error(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  if (success) {
    return (
      <main className="min-h-screen bg-background flex items-center justify-center p-4">
        <div className="w-full max-w-md">
          <div className="glass rounded-2xl p-8 shadow-2xl">
            <div className="text-center mb-8">
              <div className="mx-auto w-16 h-16 bg-green-500/20 rounded-full flex items-center justify-center mb-4">
                <svg className="w-8 h-8 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <h1 className="text-3xl font-display font-bold mb-2 bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 bg-clip-text text-transparent">
                Email Enviado!
              </h1>
              <p className="text-muted-foreground">
                Verifique sua caixa de entrada
              </p>
            </div>

            <div className="space-y-4">
              <div className="p-4 bg-green-500/10 border border-green-500/20 rounded-lg">
                <p className="text-sm text-green-400">
                  Enviamos um link de recuperação para <strong>{email}</strong>
                </p>
                <p className="text-sm text-muted-foreground mt-2">
                  O link é válido por 1 hora. Se não encontrar o email, verifique sua pasta de spam.
                </p>
              </div>

              <div className="flex flex-col gap-3">
                <button
                  onClick={() => {
                    setSuccess(false)
                    setEmail('')
                  }}
                  className="w-full py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors font-medium"
                >
                  Enviar outro email
                </button>
                <Link
                  href="/login"
                  className="w-full py-3 text-center border border-border rounded-lg hover:bg-background/50 transition-colors font-medium"
                >
                  Voltar para login
                </Link>
              </div>
            </div>
          </div>
        </div>
      </main>
    )
  }

  return (
    <main className="min-h-screen bg-background flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="glass rounded-2xl p-8 shadow-2xl">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-display font-bold mb-2 bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 bg-clip-text text-transparent">
              Esqueceu a senha?
            </h1>
            <p className="text-muted-foreground">
              Digite seu email e enviaremos um link para redefinir sua senha
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label htmlFor="email" className="block text-sm font-medium mb-2">
                Email
              </label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="w-full px-4 py-3 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
                placeholder="seu@email.com"
              />
            </div>

            {error && (
              <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-lg text-red-400 text-sm">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium"
            >
              {loading ? 'Enviando...' : 'Enviar link de recuperação'}
            </button>
          </form>

          <div className="mt-6 text-center">
            <p className="text-sm text-muted-foreground">
              Lembrou sua senha?{' '}
              <Link href="/login" className="text-indigo-400 hover:text-indigo-300 font-medium">
                Fazer login
              </Link>
            </p>
          </div>
        </div>
      </div>
    </main>
  )
}

