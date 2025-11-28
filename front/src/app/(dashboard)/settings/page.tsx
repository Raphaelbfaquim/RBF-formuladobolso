'use client'

import { useState, useEffect } from 'react'
import { useTheme } from 'next-themes'
import apiClient from '@/lib/api/client'
import toast from 'react-hot-toast'
import Image from 'next/image'

type TabType = 'profile' | 'security' | 'appearance' | 'notifications'

export default function SettingsPage() {
  const [activeTab, setActiveTab] = useState<TabType>('profile')
  const [loading, setLoading] = useState(false)
  const [user, setUser] = useState<any>(null)
  const [twoFactorStatus, setTwoFactorStatus] = useState<any>(null)
  const { theme, setTheme, resolvedTheme } = useTheme()
  const [mounted, setMounted] = useState(false)

  // Formulários
  const [profileForm, setProfileForm] = useState({
    email: '',
    username: '',
    full_name: '',
  })

  const [passwordForm, setPasswordForm] = useState({
    current_password: '',
    new_password: '',
    confirm_password: '',
  })

  const [twoFactorForm, setTwoFactorForm] = useState({
    code: '',
  })

  const [twoFactorData, setTwoFactorData] = useState<any>(null)
  const [qrCodeUrl, setQrCodeUrl] = useState<string | null>(null)

  useEffect(() => {
    loadUserData()
    load2FAStatus()
    setMounted(true)
  }, [])

  // Sincronizar tema quando montar e quando mudar
  useEffect(() => {
    if (!mounted) return
    
    // Determinar qual tema aplicar baseado no theme e resolvedTheme
    let shouldBeDark = true // default
    
    if (theme === 'light') {
      shouldBeDark = false
    } else if (theme === 'dark') {
      shouldBeDark = true
    } else if (theme === 'system' || !theme) {
      // Se for system ou undefined, usar resolvedTheme ou detectar preferência
      if (resolvedTheme === 'light') {
        shouldBeDark = false
      } else if (resolvedTheme === 'dark') {
        shouldBeDark = true
      } else {
        // Se não tem resolvedTheme, detectar preferência do sistema
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
        shouldBeDark = prefersDark
      }
    }
    
    // Aplicar tema na tag HTML
    if (shouldBeDark) {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  }, [mounted, theme, resolvedTheme])

  const loadUserData = async () => {
    try {
      const response = await apiClient.get('/users/me')
      setUser(response.data)
      setProfileForm({
        email: response.data.email || '',
        username: response.data.username || '',
        full_name: response.data.full_name || '',
      })
      
      // Carregar tema do backend se existir
      if (response.data.theme_preference) {
        setTheme(response.data.theme_preference as 'light' | 'dark' | 'system')
      }
    } catch (error: any) {
      console.error('Erro ao carregar dados do usuário:', error)
    }
  }

  const load2FAStatus = async () => {
    try {
      const response = await apiClient.get('/security/2fa/status')
      setTwoFactorStatus(response.data)
    } catch (error: any) {
      console.error('Erro ao carregar status do 2FA:', error)
    }
  }


  const handleUpdateProfile = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    try {
      await apiClient.put('/users/me', profileForm)
      toast.success('Perfil atualizado com sucesso!')
      loadUserData()
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Erro ao atualizar perfil')
    } finally {
      setLoading(false)
    }
  }

  const handleChangePassword = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (passwordForm.new_password !== passwordForm.confirm_password) {
      toast.error('As senhas não coincidem!')
      return
    }

    if (passwordForm.new_password.length < 8) {
      toast.error('A senha deve ter no mínimo 8 caracteres')
      return
    }

    setLoading(true)
    try {
      await apiClient.post('/users/me/change-password', {
        current_password: passwordForm.current_password,
        new_password: passwordForm.new_password,
      })
      toast.success('Senha alterada com sucesso!')
      setPasswordForm({
        current_password: '',
        new_password: '',
        confirm_password: '',
      })
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Erro ao alterar senha')
    } finally {
      setLoading(false)
    }
  }

  const handleEnable2FA = async () => {
    setLoading(true)
    try {
      const response = await apiClient.post('/security/2fa/enable', { method: 'totp' })
      setTwoFactorData(response.data)
      
      if (response.data.qr_code) {
        if (typeof response.data.qr_code === 'string') {
          setQrCodeUrl(`data:image/png;base64,${response.data.qr_code}`)
        } else if (response.data.qr_code instanceof ArrayBuffer) {
          const blob = new Blob([response.data.qr_code], { type: 'image/png' })
          const url = URL.createObjectURL(blob)
          setQrCodeUrl(url)
        }
      }
      
      toast.success('2FA habilitado! Escaneie o QR code')
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Erro ao habilitar 2FA')
    } finally {
      setLoading(false)
    }
  }

  const handleVerify2FA = async () => {
    if (!twoFactorForm.code) {
      toast.error('Digite o código do autenticador')
      return
    }

    setLoading(true)
    try {
      await apiClient.post('/security/2fa/verify', { code: twoFactorForm.code })
      toast.success('2FA configurado com sucesso!')
      setTwoFactorData(null)
      setQrCodeUrl(null)
      setTwoFactorForm({ code: '' })
      load2FAStatus()
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Código inválido')
    } finally {
      setLoading(false)
    }
  }

  const handleDisable2FA = async () => {
    if (!confirm('Tem certeza que deseja desabilitar o 2FA?')) {
      return
    }

    setLoading(true)
    try {
      await apiClient.post('/security/2fa/disable')
      toast.success('2FA desabilitado com sucesso!')
      load2FAStatus()
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Erro ao desabilitar 2FA')
    } finally {
      setLoading(false)
    }
  }

  const handleThemeChange = async (newTheme: 'light' | 'dark' | 'system') => {
    console.log('Mudando tema para:', newTheme)
    
    // Aplicar imediatamente na DOM para feedback visual instantâneo
    if (newTheme === 'system') {
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
      if (prefersDark) {
        document.documentElement.classList.add('dark')
      } else {
        document.documentElement.classList.remove('dark')
      }
    } else if (newTheme === 'dark') {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
    
    // Atualizar via next-themes (salva no localStorage)
    setTheme(newTheme)
    
    // Salvar no backend
    try {
      await apiClient.put('/users/me', {
        theme_preference: newTheme
      })
      toast.success(`Tema alterado para ${newTheme === 'light' ? 'Claro' : newTheme === 'dark' ? 'Escuro' : 'Sistema'}!`)
    } catch (error: any) {
      console.error('Erro ao salvar tema no backend:', error)
      toast.error('Tema aplicado, mas não foi possível salvar no servidor')
    }
  }

  // Evitar hidratação mismatch - mostrar loading até o tema estar pronto
  if (!mounted) {
    return (
      <div className="min-h-screen bg-background p-6">
        <div className="max-w-7xl mx-auto">
          <div className="mb-8">
            <h1 className="text-3xl font-bold mb-2">Configurações</h1>
            <p className="text-muted-foreground">Carregando...</p>
          </div>
        </div>
      </div>
    )
  }

  const tabs = [
    { id: 'profile' as TabType, name: 'Perfil', icon: '👤' },
    { id: 'security' as TabType, name: 'Segurança', icon: '🔒' },
    { id: 'appearance' as TabType, name: 'Aparência', icon: '🎨' },
    { id: 'notifications' as TabType, name: 'Notificações', icon: '🔔' },
  ]

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">Configurações</h1>
          <p className="text-muted-foreground">Configure sua conta e preferências</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Sidebar de Tabs */}
          <div className="lg:col-span-1">
            <div className="bg-card rounded-lg border border-border p-4 space-y-2">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                    activeTab === tab.id
                      ? 'bg-indigo-500/20 text-indigo-400 border border-indigo-500/30'
                      : 'text-muted-foreground hover:bg-background hover:text-foreground'
                  }`}
                >
                  <span className="text-lg">{tab.icon}</span>
                  <span className="font-medium">{tab.name}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Conteúdo */}
          <div className="lg:col-span-3">
            <div className="bg-card rounded-lg border border-border p-6">
              {/* Tab: Perfil */}
              {activeTab === 'profile' && (
                <div>
                  <h2 className="text-2xl font-bold mb-6">Perfil</h2>
                  <form onSubmit={handleUpdateProfile} className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium mb-2">Email</label>
                      <input
                        type="email"
                        value={profileForm.email}
                        onChange={(e) => setProfileForm({ ...profileForm, email: e.target.value })}
                        className="w-full px-4 py-3 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                        required
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium mb-2">Nome de usuário</label>
                      <input
                        type="text"
                        value={profileForm.username}
                        onChange={(e) => setProfileForm({ ...profileForm, username: e.target.value })}
                        className="w-full px-4 py-3 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                        required
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium mb-2">Nome completo</label>
                      <input
                        type="text"
                        value={profileForm.full_name}
                        onChange={(e) => setProfileForm({ ...profileForm, full_name: e.target.value })}
                        className="w-full px-4 py-3 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                      />
                    </div>

                    <button
                      type="submit"
                      disabled={loading}
                      className="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 transition-colors"
                    >
                      {loading ? 'Salvando...' : 'Salvar alterações'}
                    </button>
                  </form>
                </div>
              )}

              {/* Tab: Segurança */}
              {activeTab === 'security' && (
                <div className="space-y-8">
                  <div>
                    <h2 className="text-2xl font-bold mb-6">Segurança</h2>

                    {/* Alterar Senha */}
                    <div className="mb-8 p-6 bg-background rounded-lg border border-border">
                      <h3 className="text-xl font-semibold mb-4">Alterar Senha</h3>
                      <form onSubmit={handleChangePassword} className="space-y-4">
                        <div>
                          <label className="block text-sm font-medium mb-2">Senha atual</label>
                          <input
                            type="password"
                            value={passwordForm.current_password}
                            onChange={(e) => setPasswordForm({ ...passwordForm, current_password: e.target.value })}
                            className="w-full px-4 py-3 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                            required
                          />
                        </div>

                        <div>
                          <label className="block text-sm font-medium mb-2">Nova senha</label>
                          <input
                            type="password"
                            value={passwordForm.new_password}
                            onChange={(e) => setPasswordForm({ ...passwordForm, new_password: e.target.value })}
                            className="w-full px-4 py-3 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                            required
                            minLength={8}
                          />
                        </div>

                        <div>
                          <label className="block text-sm font-medium mb-2">Confirmar nova senha</label>
                          <input
                            type="password"
                            value={passwordForm.confirm_password}
                            onChange={(e) => setPasswordForm({ ...passwordForm, confirm_password: e.target.value })}
                            className="w-full px-4 py-3 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                            required
                            minLength={8}
                          />
                        </div>

                        <button
                          type="submit"
                          disabled={loading}
                          className="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 transition-colors"
                        >
                          {loading ? 'Alterando...' : 'Alterar senha'}
                        </button>
                      </form>
                    </div>

                    {/* 2FA */}
                    <div className="p-6 bg-background rounded-lg border border-border">
                      <h3 className="text-xl font-semibold mb-4">Autenticação de Dois Fatores (2FA)</h3>
                      
                      {twoFactorStatus?.is_enabled ? (
                        <div>
                          <div className="mb-4 p-4 bg-green-500/10 border border-green-500/20 rounded-lg">
                            <p className="text-green-400">✅ 2FA está habilitado</p>
                            <p className="text-sm text-muted-foreground mt-1">Método: {twoFactorStatus.method || 'TOTP'}</p>
                          </div>
                          <button
                            onClick={handleDisable2FA}
                            disabled={loading}
                            className="px-6 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50 transition-colors"
                          >
                            {loading ? 'Desabilitando...' : 'Desabilitar 2FA'}
                          </button>
                        </div>
                      ) : (
                        <div>
                          {twoFactorData ? (
                            <div className="space-y-4">
                              <p className="text-muted-foreground">Escaneie o QR code com seu app autenticador:</p>
                              
                              {qrCodeUrl && (
                                <div className="flex justify-center mb-4">
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

                              {twoFactorData.backup_codes && (
                                <div className="mb-4 p-3 bg-yellow-500/10 border border-yellow-500/20 rounded-lg">
                                  <p className="text-xs text-yellow-400 mb-2">
                                    <strong>Códigos de Backup:</strong> Guarde estes códigos em local seguro
                                  </p>
                                  <div className="grid grid-cols-2 gap-2">
                                    {twoFactorData.backup_codes.map((code: string, idx: number) => (
                                      <code key={idx} className="text-xs bg-background px-2 py-1 rounded">
                                        {code}
                                      </code>
                                    ))}
                                  </div>
                                </div>
                              )}

                              <div>
                                <label className="block text-sm font-medium mb-2">Código do Autenticador</label>
                                <input
                                  type="text"
                                  value={twoFactorForm.code}
                                  onChange={(e) => setTwoFactorForm({ code: e.target.value })}
                                  placeholder="000000"
                                  maxLength={6}
                                  className="w-full px-4 py-3 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                                />
                              </div>

                              <button
                                onClick={handleVerify2FA}
                                disabled={loading}
                                className="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 transition-colors"
                              >
                                {loading ? 'Verificando...' : 'Verificar e Ativar'}
                              </button>
                            </div>
                          ) : (
                            <div>
                              <p className="text-muted-foreground mb-4">
                                Adicione uma camada extra de segurança à sua conta
                              </p>
                              <button
                                onClick={handleEnable2FA}
                                disabled={loading}
                                className="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 transition-colors"
                              >
                                {loading ? 'Habilitando...' : 'Habilitar 2FA'}
                              </button>
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              )}

              {/* Tab: Aparência */}
              {activeTab === 'appearance' && (
                <div>
                  <h2 className="text-2xl font-bold mb-6">Aparência</h2>
                  
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium mb-4">Tema</label>
                      <div className="grid grid-cols-3 gap-4">
                        <button
                          onClick={() => handleThemeChange('light')}
                          className={`p-6 rounded-lg border-2 transition-all ${
                            theme === 'light'
                              ? 'border-indigo-500 bg-indigo-500/10'
                              : 'border-border hover:border-indigo-500/50'
                          }`}
                        >
                          <div className="text-4xl mb-2">☀️</div>
                          <div className="font-medium">Claro</div>
                          <div className="text-sm text-muted-foreground">Fundo branco</div>
                        </button>

                        <button
                          onClick={() => handleThemeChange('dark')}
                          className={`p-6 rounded-lg border-2 transition-all ${
                            theme === 'dark'
                              ? 'border-indigo-500 bg-indigo-500/10'
                              : 'border-border hover:border-indigo-500/50'
                          }`}
                        >
                          <div className="text-4xl mb-2">🌙</div>
                          <div className="font-medium">Escuro</div>
                          <div className="text-sm text-muted-foreground">Fundo escuro</div>
                        </button>

                        <button
                          onClick={() => handleThemeChange('system')}
                          className={`p-6 rounded-lg border-2 transition-all ${
                            theme === 'system' || (!theme && resolvedTheme)
                              ? 'border-indigo-500 bg-indigo-500/10'
                              : 'border-border hover:border-indigo-500/50'
                          }`}
                        >
                          <div className="text-4xl mb-2">💻</div>
                          <div className="font-medium">Sistema</div>
                          <div className="text-sm text-muted-foreground">Segue o sistema</div>
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Tab: Notificações */}
              {activeTab === 'notifications' && (
                <div>
                  <h2 className="text-2xl font-bold mb-6">Notificações</h2>
                  <p className="text-muted-foreground">Configurações de notificações em breve...</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
