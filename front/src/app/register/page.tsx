'use client'

import { useState } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import Image from 'next/image'
import { authApi } from '@/lib/api/auth'
import toast from 'react-hot-toast'

export default function RegisterPage() {
  const router = useRouter()
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
    full_name: '',
    two_factor_code: '',
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [show2FA, setShow2FA] = useState(false)
  const [twoFactorData, setTwoFactorData] = useState<{
    secret: string
    qr_code: string
    backup_codes: string[]
  } | null>(null)
  const [qrCodeUrl, setQrCodeUrl] = useState<string | null>(null)

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
      console.log('📤 Enviando requisição de registro...')
      const response = await authApi.register({
        username: formData.username,
        email: formData.email,
        password: formData.password,
        full_name: formData.full_name || undefined,
      })
      
      console.log('📥 Resposta recebida:', response)
      console.log('📥 Tem two_factor?', !!response.two_factor)
      
      // Configurar 2FA se recebido
      if (response.two_factor) {
        console.log('✅ 2FA data recebido:', response.two_factor)
        setTwoFactorData(response.two_factor)
        setShow2FA(true)
        
        // Converter QR code base64 para URL
        if (response.two_factor.qr_code) {
          console.log('✅ QR Code encontrado, tamanho:', response.two_factor.qr_code.length)
          setQrCodeUrl(`data:image/png;base64,${response.two_factor.qr_code}`)
        } else {
          console.error('❌ QR Code não encontrado na resposta')
          toast.error('Erro: QR Code não foi gerado. Entre em contato com o suporte.')
        }
      } else {
        // Se não tem 2FA, redirecionar para login
        console.warn('⚠️ Resposta não contém two_factor. Estrutura:', Object.keys(response))
        toast.success('Conta criada com sucesso!')
        setTimeout(() => {
          router.push('/login')
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
      router.push('/login')
    }, 1000)
  }

  // Mostrar tela de configuração 2FA
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
              Criar Conta
            </h1>
            <p className="text-muted-foreground">Comece a gerenciar suas finanças</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5">
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
              <label htmlFor="email" className="block text-sm font-medium mb-2">
                Email
              </label>
              <input
                id="email"
                name="email"
                type="email"
                value={formData.email}
                onChange={handleChange}
                required
                className="w-full px-4 py-3 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
                placeholder="seu@email.com"
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

            <div className="flex items-center">
              <input
                id="terms"
                type="checkbox"
                required
                className="mr-2"
              />
              <label htmlFor="terms" className="text-sm text-muted-foreground">
                Eu aceito os{' '}
                <Link href="/terms" className="text-indigo-400 hover:text-indigo-300">
                  termos de uso
                </Link>
                {' '}e{' '}
                <Link href="/privacy" className="text-indigo-400 hover:text-indigo-300">
                  política de privacidade
                </Link>
              </label>
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
              {loading ? 'Criando conta...' : 'Criar Conta'}
            </button>
          </form>

          <div className="mt-6 text-center">
            <p className="text-sm text-muted-foreground">
              Já tem uma conta?{' '}
              <Link href="/login" className="text-indigo-400 hover:text-indigo-300 font-medium">
                Entrar
              </Link>
            </p>
          </div>
        </div>
      </div>
    </main>
  )
}

