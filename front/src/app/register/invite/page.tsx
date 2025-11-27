'use client'

import { useState, useEffect, Suspense } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import apiClient from '@/lib/api/client'
import toast from 'react-hot-toast'
import Image from 'next/image'

function InviteRegisterPageContent() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const [token, setToken] = useState<string | null>(null)
  const [inviteData, setInviteData] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [validating, setValidating] = useState(true)
  const [error, setError] = useState<string | null>(null)
  
  const [formData, setFormData] = useState({
    username: '',
    password: '',
    confirmPassword: '',
    full_name: '',
    two_factor_code: '',
  })
  
  const [twoFactorData, setTwoFactorData] = useState<any>(null)
  const [show2FA, setShow2FA] = useState(false)
  const [qrCodeUrl, setQrCodeUrl] = useState<string | null>(null)

  useEffect(() => {
    const tokenParam = searchParams.get('token')
    if (tokenParam) {
      setToken(tokenParam)
      validateToken(tokenParam)
    } else {
      setError('Token de convite não encontrado')
      setValidating(false)
      setLoading(false)
    }
  }, [searchParams])

  const validateToken = async (tokenValue: string) => {
    try {
      const response = await apiClient.get(`/family/invite/validate?token=${tokenValue}`)
      if (response.data.valid) {
        setInviteData(response.data)
        setFormData(prev => ({ ...prev, email: response.data.email }))
      } else {
        setError(response.data.message || 'Token inválido')
      }
    } catch (error: any) {
      setError(error.response?.data?.message || 'Erro ao validar token')
    } finally {
      setValidating(false)
      setLoading(false)
    }
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    })
    setError(null)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    
    if (!token) {
      setError('Token de convite não encontrado')
      return
    }

    if (formData.password !== formData.confirmPassword) {
      setError('As senhas não coincidem!')
      return
    }

    if (formData.password.length < 8) {
      setError('A senha deve ter no mínimo 8 caracteres')
      return
    }

    setLoading(true)
    
    try {
      const response = await apiClient.post('/family/invite/register', {
        token: token,
        username: formData.username,
        password: formData.password,
        full_name: formData.full_name || null,
        two_factor_code: formData.two_factor_code || null,
      })
      
      // Salvar tokens
      if (response.data.tokens) {
        localStorage.setItem('access_token', response.data.tokens.access_token)
        localStorage.setItem('refresh_token', response.data.tokens.refresh_token)
      }
      
      // Configurar 2FA
      if (response.data.two_factor) {
        console.log('2FA data recebido:', response.data.two_factor)
        setTwoFactorData(response.data.two_factor)
        setShow2FA(true)
        
        // Converter QR code base64 para URL
        if (response.data.two_factor.qr_code) {
          console.log('QR Code encontrado, tamanho:', response.data.two_factor.qr_code.length)
          setQrCodeUrl(`data:image/png;base64,${response.data.two_factor.qr_code}`)
        } else {
          console.error('QR Code não encontrado na resposta')
          toast.error('Erro: QR Code não foi gerado. Entre em contato com o suporte.')
        }
      } else {
        // Se não tem 2FA, redirecionar direto
        toast.success('Conta criada com sucesso!')
        setTimeout(() => {
          router.push('/dashboard')
        }, 1000)
      }
      
    } catch (error: any) {
      console.error('Erro no registro:', error)
      const errorMessage = error.response?.data?.detail || error.message || 'Erro ao criar conta'
      setError(errorMessage)
      toast.error(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  const handle2FASetup = async () => {
    if (!formData.two_factor_code) {
      toast.error('Por favor, insira o código do autenticador')
      return
    }

    // TODO: Verificar código 2FA com backend
    // Por enquanto, apenas redirecionar
    toast.success('Autenticação de dois fatores configurada!')
    setTimeout(() => {
      router.push('/dashboard')
    }, 1000)
  }

  if (validating || loading) {
    return (
      <main className="min-h-screen bg-background flex items-center justify-center p-4">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-500 mx-auto"></div>
          <p className="mt-4 text-muted-foreground">
            {validating ? 'Validando convite...' : 'Criando conta...'}
          </p>
        </div>
      </main>
    )
  }

  if (error && !inviteData) {
    return (
      <main className="min-h-screen bg-background flex items-center justify-center p-4">
        <div className="w-full max-w-md">
          <div className="glass rounded-2xl p-8 shadow-2xl text-center">
            <div className="text-6xl mb-4">❌</div>
            <h1 className="text-2xl font-bold mb-4">Convite Inválido</h1>
            <p className="text-muted-foreground mb-6">{error}</p>
            <button
              onClick={() => router.push('/login')}
              className="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
            >
              Ir para Login
            </button>
          </div>
        </div>
      </main>
    )
  }

  if (show2FA && twoFactorData) {
    return (
      <main className="min-h-screen bg-background flex items-center justify-center p-4">
        <div className="w-full max-w-md">
          <div className="glass rounded-2xl p-8 shadow-2xl">
            <div className="text-center mb-6">
              <h1 className="text-2xl font-bold mb-2">Configure Autenticação de Dois Fatores</h1>
              <p className="text-muted-foreground text-sm">
                Escaneie o QR Code com seu app autenticador
              </p>
            </div>

            {qrCodeUrl && (
              <div className="flex justify-center mb-6">
                <div className="bg-white p-4 rounded-lg">
                  <Image
                    src={qrCodeUrl}
                    alt="QR Code 2FA"
                    width={200}
                    height={200}
                    className="rounded"
                  />
                </div>
              </div>
            )}

            <div className="mb-4">
              <label className="block text-sm font-medium mb-2">
                Código do Autenticador
              </label>
              <input
                type="text"
                value={formData.two_factor_code}
                onChange={(e) => setFormData({ ...formData, two_factor_code: e.target.value })}
                placeholder="000000"
                maxLength={6}
                className="w-full px-4 py-3 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
              <p className="text-xs text-muted-foreground mt-2">
                Digite o código de 6 dígitos do seu app autenticador
              </p>
            </div>

            <div className="mb-4 p-3 bg-yellow-500/10 border border-yellow-500/20 rounded-lg">
              <p className="text-xs text-yellow-400">
                <strong>Códigos de Backup:</strong> Guarde estes códigos em local seguro
              </p>
              <div className="mt-2 grid grid-cols-2 gap-2">
                {twoFactorData.backup_codes?.map((code: string, idx: number) => (
                  <code key={idx} className="text-xs bg-background px-2 py-1 rounded">
                    {code}
                  </code>
                ))}
              </div>
            </div>

            <button
              onClick={handle2FASetup}
              className="w-full py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors font-medium"
            >
              Confirmar e Finalizar
            </button>
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
              Aceitar Convite
            </h1>
            {inviteData && (
              <div className="mt-4 p-4 bg-indigo-500/10 border border-indigo-500/20 rounded-lg">
                <p className="text-sm text-muted-foreground mb-2">
                  Você foi convidado(a) para o grupo
                </p>
                <p className="font-semibold text-indigo-400">{inviteData.family_name}</p>
                <p className="text-xs text-muted-foreground mt-2">
                  por {inviteData.inviter_name}
                </p>
              </div>
            )}
            <p className="text-muted-foreground mt-4">
              Crie sua conta para acessar o sistema
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label htmlFor="email" className="block text-sm font-medium mb-2">
                Email
              </label>
              <input
                id="email"
                type="email"
                value={inviteData?.email || ''}
                disabled
                className="w-full px-4 py-3 bg-background/50 border border-border rounded-lg opacity-60 cursor-not-allowed"
              />
              <p className="text-xs text-muted-foreground mt-1">
                Este email foi definido no convite
              </p>
            </div>

            <div>
              <label htmlFor="full_name" className="block text-sm font-medium mb-2">
                Nome completo (opcional)
              </label>
              <input
                id="full_name"
                name="full_name"
                type="text"
                value={formData.full_name}
                onChange={handleChange}
                className="w-full px-4 py-3 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
                placeholder="Seu Nome Completo"
              />
            </div>

            <div>
              <label htmlFor="username" className="block text-sm font-medium mb-2">
                Nome de usuário
              </label>
              <input
                id="username"
                name="username"
                type="text"
                value={formData.username}
                onChange={handleChange}
                required
                className="w-full px-4 py-3 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
                placeholder="seu_usuario"
              />
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium mb-2">
                Senha
              </label>
              <input
                id="password"
                name="password"
                type="password"
                value={formData.password}
                onChange={handleChange}
                required
                minLength={8}
                className="w-full px-4 py-3 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
                placeholder="••••••••"
              />
            </div>

            <div>
              <label htmlFor="confirmPassword" className="block text-sm font-medium mb-2">
                Confirmar Senha
              </label>
              <input
                id="confirmPassword"
                name="confirmPassword"
                type="password"
                value={formData.confirmPassword}
                onChange={handleChange}
                required
                minLength={8}
                className="w-full px-4 py-3 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
                placeholder="••••••••"
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
              {loading ? 'Criando conta...' : 'Criar Conta e Aceitar Convite'}
            </button>
          </form>

          <div className="mt-6 text-center">
            <p className="text-sm text-muted-foreground">
              Já tem uma conta?{' '}
              <button
                onClick={() => router.push('/login')}
                className="text-indigo-400 hover:text-indigo-300 font-medium"
              >
                Entrar
              </button>
            </p>
          </div>
        </div>
      </div>
    </main>
  )
}

export default function InviteRegisterPage() {
  return (
    <Suspense fallback={
      <main className="min-h-screen bg-background flex items-center justify-center p-4">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-500 mx-auto"></div>
          <p className="mt-4 text-muted-foreground">Carregando...</p>
        </div>
      </main>
    }>
      <InviteRegisterPageContent />
    </Suspense>
  )
}

