'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import apiClient from '@/lib/api/client'
import toast from 'react-hot-toast'

interface UserLevel {
  id: string
  level: number
  experience_points: number
  total_points: number
  streak_days: number
  last_activity_date: string | null
  next_level_points: number
  progress_to_next_level: number
}

interface Badge {
  id: string
  name: string
  description: string | null
  badge_type: string
  icon: string | null
  color: string | null
  points: number
  rarity: string
}

interface UserBadge {
  id: string
  badge: Badge
  earned_at: string
  progress: number
}

interface Challenge {
  id: string
  name: string
  description: string | null
  challenge_type: string
  target_value: number | null
  target_metric: string | null
  reward_points: number
  start_date: string
  end_date: string
  badge_id: string | null
}

interface UserChallenge {
  id: string
  challenge: Challenge
  current_value: number
  progress_percentage: number
  is_completed: boolean
  completed_at: string | null
}

interface LeaderboardEntry {
  user_id: string
  username: string
  level: number
  total_points: number
  rank: number
}

const RARITY_COLORS: Record<string, string> = {
  common: 'border-gray-500 bg-gray-500/10',
  rare: 'border-blue-500 bg-blue-500/10',
  epic: 'border-purple-500 bg-purple-500/10',
  legendary: 'border-yellow-500 bg-yellow-500/10',
}

const RARITY_LABELS: Record<string, string> = {
  common: 'Comum',
  rare: 'Raro',
  epic: 'Épico',
  legendary: 'Lendário',
}

const LEVEL_TITLES: Record<number, string> = {
  1: 'Iniciante',
  5: 'Organizado',
  10: 'Economista',
  25: 'Mestre',
  50: 'Lendário',
  100: 'Mito',
}

function getLevelTitle(level: number): string {
  const keys = Object.keys(LEVEL_TITLES).map(Number).sort((a, b) => b - a)
  for (const key of keys) {
    if (level >= key) {
      return LEVEL_TITLES[key]
    }
  }
  return 'Iniciante'
}

export default function GamificationPage() {
  const router = useRouter()
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState<'overview' | 'badges' | 'challenges' | 'leaderboard'>('overview')
  
  const [userLevel, setUserLevel] = useState<UserLevel | null>(null)
  const [userBadges, setUserBadges] = useState<UserBadge[]>([])
  const [availableBadges, setAvailableBadges] = useState<Badge[]>([])
  const [activeChallenges, setActiveChallenges] = useState<Challenge[]>([])
  const [myChallenges, setMyChallenges] = useState<UserChallenge[]>([])
  const [leaderboard, setLeaderboard] = useState<LeaderboardEntry[]>([])
  const [showSeedButton, setShowSeedButton] = useState(false)

  useEffect(() => {
    loadData()
  }, [])

  useEffect(() => {
    if (activeTab === 'badges') {
      loadBadges()
    } else if (activeTab === 'challenges') {
      loadChallenges()
    } else if (activeTab === 'leaderboard') {
      loadLeaderboard()
    }
  }, [activeTab])

  const loadData = async () => {
    setLoading(true)
    try {
      await Promise.all([
        loadUserLevel(),
        loadBadges(),
        loadChallenges(),
        loadLeaderboard(),
      ])
    } catch (error: any) {
      if (error.response?.status === 401) {
        router.push('/login')
      } else {
        toast.error('Erro ao carregar dados de gamificação')
      }
    } finally {
      setLoading(false)
    }
  }

  const loadUserLevel = async () => {
    try {
      const response = await apiClient.get('/gamification/level')
      setUserLevel(response.data)
    } catch (error: any) {
      console.error('Erro ao carregar nível:', error)
    }
  }

  const loadBadges = async () => {
    try {
      const [userBadgesRes, availableBadgesRes] = await Promise.all([
        apiClient.get('/gamification/badges'),
        apiClient.get('/gamification/badges/available'),
      ])
      setUserBadges(userBadgesRes.data || [])
      setAvailableBadges(availableBadgesRes.data || [])
      setShowSeedButton(availableBadgesRes.data?.length === 0)
    } catch (error: any) {
      console.error('Erro ao carregar badges:', error)
      setShowSeedButton(true)
    }
  }

  const loadChallenges = async () => {
    try {
      const [activeRes, myRes] = await Promise.all([
        apiClient.get('/gamification/challenges'),
        apiClient.get('/gamification/challenges/my'),
      ])
      setActiveChallenges(activeRes.data || [])
      setMyChallenges(myRes.data || [])
    } catch (error: any) {
      console.error('Erro ao carregar desafios:', error)
    }
  }

  const loadLeaderboard = async () => {
    try {
      const response = await apiClient.get('/gamification/leaderboard?limit=20')
      setLeaderboard(response.data || [])
    } catch (error: any) {
      console.error('Erro ao carregar ranking:', error)
    }
  }

  const handleSeedBadges = async () => {
    try {
      await apiClient.post('/gamification/seed-badges?force=false')
      toast.success('Badges criados com sucesso!')
      loadBadges()
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Erro ao criar badges')
    }
  }

  const handleJoinChallenge = async (challengeId: string) => {
    try {
      await apiClient.post(`/gamification/challenges/${challengeId}/join`)
      toast.success('Desafio aceito!')
      loadChallenges()
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Erro ao entrar no desafio')
    }
  }

  if (loading && !userLevel) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-500 mx-auto"></div>
          <p className="mt-4 text-muted-foreground">Carregando gamificação...</p>
        </div>
      </div>
    )
  }

  const earnedBadgeIds = new Set(userBadges.filter(ub => ub.progress >= 100).map(ub => ub.badge.id))
  const unearnedBadges = availableBadges.filter(b => !earnedBadgeIds.has(b.id))
  const inProgressBadges = userBadges.filter(ub => ub.progress < 100)

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-7xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-3xl font-bold mb-2">Gamificação</h1>
            <p className="text-muted-foreground">Conquiste badges, níveis e desafios</p>
          </div>
          {showSeedButton && (
            <button
              onClick={handleSeedBadges}
              className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors text-sm font-medium"
            >
              Criar Badges Padrão
            </button>
          )}
        </div>

        {/* Tabs */}
        <div className="flex gap-2 mb-6 border-b border-border">
          <button
            onClick={() => setActiveTab('overview')}
            className={`px-4 py-2 font-medium transition-colors ${
              activeTab === 'overview'
                ? 'border-b-2 border-indigo-500 text-indigo-400'
                : 'text-muted-foreground hover:text-foreground'
            }`}
          >
            Visão Geral
          </button>
          <button
            onClick={() => setActiveTab('badges')}
            className={`px-4 py-2 font-medium transition-colors ${
              activeTab === 'badges'
                ? 'border-b-2 border-indigo-500 text-indigo-400'
                : 'text-muted-foreground hover:text-foreground'
            }`}
          >
            Badges ({userBadges.filter(ub => ub.progress >= 100).length}/{availableBadges.length})
          </button>
          <button
            onClick={() => setActiveTab('challenges')}
            className={`px-4 py-2 font-medium transition-colors ${
              activeTab === 'challenges'
                ? 'border-b-2 border-indigo-500 text-indigo-400'
                : 'text-muted-foreground hover:text-foreground'
            }`}
          >
            Desafios ({myChallenges.length})
          </button>
          <button
            onClick={() => setActiveTab('leaderboard')}
            className={`px-4 py-2 font-medium transition-colors ${
              activeTab === 'leaderboard'
                ? 'border-b-2 border-indigo-500 text-indigo-400'
                : 'text-muted-foreground hover:text-foreground'
            }`}
          >
            Ranking
          </button>
        </div>

        {/* Overview Tab */}
        {activeTab === 'overview' && userLevel && (
          <div className="space-y-6">
            {/* Level Card */}
            <div className="glass rounded-xl p-6">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h2 className="text-2xl font-bold mb-1">
                    Nível {userLevel.level} - {getLevelTitle(userLevel.level)}
                  </h2>
                  <p className="text-muted-foreground">
                    {userLevel.experience_points.toLocaleString('pt-BR')} XP de {userLevel.next_level_points.toLocaleString('pt-BR')} XP
                  </p>
                </div>
                <div className="text-right">
                  <div className="text-3xl font-bold text-indigo-400">{userLevel.total_points.toLocaleString('pt-BR')}</div>
                  <div className="text-sm text-muted-foreground">Pontos Totais</div>
                </div>
              </div>
              
              {/* Progress Bar */}
              <div className="w-full bg-background rounded-full h-4 mb-4">
                <div
                  className="bg-gradient-to-r from-indigo-500 to-purple-500 h-4 rounded-full transition-all duration-500"
                  style={{ width: `${userLevel.progress_to_next_level}%` }}
                ></div>
              </div>
              
              <div className="flex items-center gap-6 text-sm">
                <div className="flex items-center gap-2">
                  <span className="text-muted-foreground">Streak:</span>
                  <span className="font-bold text-orange-400 flex items-center gap-1">
                    🔥 {userLevel.streak_days} dias
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-muted-foreground">Badges:</span>
                  <span className="font-bold text-indigo-400">
                    {userBadges.filter(ub => ub.progress >= 100).length}
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-muted-foreground">Desafios:</span>
                  <span className="font-bold text-green-400">
                    {myChallenges.filter(uc => uc.is_completed).length}/{myChallenges.length}
                  </span>
                </div>
              </div>
            </div>

            {/* Recent Badges */}
            <div className="glass rounded-xl p-6">
              <h3 className="text-xl font-bold mb-4">Badges Recentes</h3>
              {userBadges.filter(ub => ub.progress >= 100).length > 0 ? (
                <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
                  {userBadges
                    .filter(ub => ub.progress >= 100)
                    .slice(0, 6)
                    .map((userBadge) => (
                      <div
                        key={userBadge.id}
                        className={`p-4 rounded-lg border-2 ${RARITY_COLORS[userBadge.badge.rarity] || RARITY_COLORS.common} text-center`}
                      >
                        <div className="text-4xl mb-2">{userBadge.badge.icon || '🏆'}</div>
                        <div className="text-xs font-medium">{userBadge.badge.name}</div>
                      </div>
                    ))}
                </div>
              ) : (
                <p className="text-muted-foreground text-center py-8">
                  Ainda não há badges conquistados. Complete ações para ganhar badges!
                </p>
              )}
            </div>

            {/* Active Challenges */}
            <div className="glass rounded-xl p-6">
              <h3 className="text-xl font-bold mb-4">Desafios Ativos</h3>
              {myChallenges.filter(uc => !uc.is_completed).length > 0 ? (
                <div className="space-y-3">
                  {myChallenges
                    .filter(uc => !uc.is_completed)
                    .slice(0, 3)
                    .map((userChallenge) => (
                      <div key={userChallenge.id} className="p-4 bg-background/50 rounded-lg">
                        <div className="flex items-center justify-between mb-2">
                          <h4 className="font-medium">{userChallenge.challenge.name}</h4>
                          <span className="text-sm text-muted-foreground">
                            {userChallenge.progress_percentage}%
                          </span>
                        </div>
                        <div className="w-full bg-background rounded-full h-2">
                          <div
                            className="bg-green-500 h-2 rounded-full transition-all"
                            style={{ width: `${userChallenge.progress_percentage}%` }}
                          ></div>
                        </div>
                        {userChallenge.challenge.target_value && (
                          <p className="text-xs text-muted-foreground mt-2">
                            {userChallenge.current_value.toLocaleString('pt-BR', {
                              style: 'currency',
                              currency: 'BRL'
                            })} / {userChallenge.challenge.target_value.toLocaleString('pt-BR', {
                              style: 'currency',
                              currency: 'BRL'
                            })}
                          </p>
                        )}
                      </div>
                    ))}
                </div>
              ) : (
                <p className="text-muted-foreground text-center py-8">
                  Nenhum desafio ativo. Entre em um desafio para começar!
                </p>
              )}
            </div>
          </div>
        )}

        {/* Badges Tab */}
        {activeTab === 'badges' && (
          <div className="space-y-6">
            {/* Earned Badges */}
            {userBadges.filter(ub => ub.progress >= 100).length > 0 && (
              <div>
                <h3 className="text-xl font-bold mb-4">Badges Conquistados ({userBadges.filter(ub => ub.progress >= 100).length})</h3>
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                  {userBadges
                    .filter(ub => ub.progress >= 100)
                    .map((userBadge) => (
                      <div
                        key={userBadge.id}
                        className={`p-4 rounded-lg border-2 ${RARITY_COLORS[userBadge.badge.rarity] || RARITY_COLORS.common}`}
                      >
                        <div className="text-5xl mb-3 text-center">{userBadge.badge.icon || '🏆'}</div>
                        <h4 className="font-bold mb-1 text-center">{userBadge.badge.name}</h4>
                        <p className="text-xs text-muted-foreground text-center mb-2">
                          {userBadge.badge.description}
                        </p>
                        <div className="flex items-center justify-between text-xs">
                          <span className={`px-2 py-1 rounded ${RARITY_COLORS[userBadge.badge.rarity] || RARITY_COLORS.common}`}>
                            {RARITY_LABELS[userBadge.badge.rarity] || 'Comum'}
                          </span>
                          <span className="text-indigo-400 font-bold">+{userBadge.badge.points} XP</span>
                        </div>
                        <p className="text-xs text-muted-foreground text-center mt-2">
                          Conquistado em {new Date(userBadge.earned_at).toLocaleDateString('pt-BR')}
                        </p>
                      </div>
                    ))}
                </div>
              </div>
            )}

            {/* In Progress Badges */}
            {inProgressBadges.length > 0 && (
              <div>
                <h3 className="text-xl font-bold mb-4">Em Progresso ({inProgressBadges.length})</h3>
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                  {inProgressBadges.map((userBadge) => (
                    <div
                      key={userBadge.id}
                      className="p-4 rounded-lg border-2 border-gray-500/30 bg-gray-500/5 opacity-60"
                    >
                      <div className="text-5xl mb-3 text-center">{userBadge.badge.icon || '🏆'}</div>
                      <h4 className="font-bold mb-1 text-center">{userBadge.badge.name}</h4>
                      <p className="text-xs text-muted-foreground text-center mb-2">
                        {userBadge.badge.description}
                      </p>
                      <div className="w-full bg-background rounded-full h-2 mb-2">
                        <div
                          className="bg-indigo-500 h-2 rounded-full"
                          style={{ width: `${userBadge.progress}%` }}
                        ></div>
                      </div>
                      <p className="text-xs text-center text-muted-foreground">{userBadge.progress}%</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Available Badges */}
            {unearnedBadges.length > 0 && (
              <div>
                <h3 className="text-xl font-bold mb-4">Badges Disponíveis ({unearnedBadges.length})</h3>
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                  {unearnedBadges.map((badge) => (
                    <div
                      key={badge.id}
                      className="p-4 rounded-lg border-2 border-gray-500/20 bg-gray-500/5 opacity-50"
                    >
                      <div className="text-5xl mb-3 text-center grayscale">{badge.icon || '🏆'}</div>
                      <h4 className="font-bold mb-1 text-center">{badge.name}</h4>
                      <p className="text-xs text-muted-foreground text-center mb-2">
                        {badge.description}
                      </p>
                      <div className="flex items-center justify-between text-xs">
                        <span className={`px-2 py-1 rounded ${RARITY_COLORS[badge.rarity] || RARITY_COLORS.common}`}>
                          {RARITY_LABELS[badge.rarity] || 'Comum'}
                        </span>
                        <span className="text-muted-foreground">+{badge.points} XP</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Challenges Tab */}
        {activeTab === 'challenges' && (
          <div className="space-y-6">
            {/* My Challenges */}
            {myChallenges.length > 0 && (
              <div>
                <h3 className="text-xl font-bold mb-4">Meus Desafios ({myChallenges.length})</h3>
                <div className="space-y-4">
                  {myChallenges.map((userChallenge) => (
                    <div
                      key={userChallenge.id}
                      className={`glass rounded-xl p-6 ${userChallenge.is_completed ? 'border-2 border-green-500' : ''}`}
                    >
                      <div className="flex items-start justify-between mb-4">
                        <div className="flex-1">
                          <div className="flex items-center gap-3 mb-2">
                            <h4 className="text-lg font-bold">{userChallenge.challenge.name}</h4>
                            {userChallenge.is_completed && (
                              <span className="px-2 py-1 bg-green-500/20 text-green-400 rounded text-xs font-medium">
                                ✓ Completo
                              </span>
                            )}
                          </div>
                          <p className="text-muted-foreground mb-4">
                            {userChallenge.challenge.description}
                          </p>
                          <div className="w-full bg-background rounded-full h-3 mb-2">
                            <div
                              className={`h-3 rounded-full transition-all ${
                                userChallenge.is_completed ? 'bg-green-500' : 'bg-indigo-500'
                              }`}
                              style={{ width: `${userChallenge.progress_percentage}%` }}
                            ></div>
                          </div>
                          <div className="flex items-center justify-between text-sm">
                            <span className="text-muted-foreground">
                              {userChallenge.progress_percentage}% completo
                            </span>
                            {userChallenge.challenge.target_value && (
                              <span className="text-muted-foreground">
                                {userChallenge.current_value.toLocaleString('pt-BR', {
                                  style: 'currency',
                                  currency: 'BRL'
                                })} / {userChallenge.challenge.target_value.toLocaleString('pt-BR', {
                                  style: 'currency',
                                  currency: 'BRL'
                                })}
                              </span>
                            )}
                          </div>
                          {userChallenge.completed_at && (
                            <p className="text-xs text-muted-foreground mt-2">
                              Completado em {new Date(userChallenge.completed_at).toLocaleDateString('pt-BR')}
                            </p>
                          )}
                        </div>
                        <div className="text-right ml-4">
                          <div className="text-2xl font-bold text-indigo-400">
                            +{userChallenge.challenge.reward_points} XP
                          </div>
                          <div className="text-xs text-muted-foreground">Recompensa</div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Available Challenges */}
            {activeChallenges.length > 0 && (
              <div>
                <h3 className="text-xl font-bold mb-4">Desafios Disponíveis ({activeChallenges.length})</h3>
                <div className="space-y-4">
                  {activeChallenges
                    .filter(c => !myChallenges.some(uc => uc.challenge.id === c.id))
                    .map((challenge) => (
                      <div key={challenge.id} className="glass rounded-xl p-6">
                        <div className="flex items-start justify-between mb-4">
                          <div className="flex-1">
                            <h4 className="text-lg font-bold mb-2">{challenge.name}</h4>
                            <p className="text-muted-foreground mb-4">{challenge.description}</p>
                            <div className="flex items-center gap-4 text-sm">
                              <span className="text-muted-foreground">
                                Tipo: {challenge.challenge_type}
                              </span>
                              <span className="text-muted-foreground">
                                Até {new Date(challenge.end_date).toLocaleDateString('pt-BR')}
                              </span>
                            </div>
                          </div>
                          <div className="text-right ml-4">
                            <div className="text-2xl font-bold text-indigo-400">
                              +{challenge.reward_points} XP
                            </div>
                            <div className="text-xs text-muted-foreground">Recompensa</div>
                          </div>
                        </div>
                        <button
                          onClick={() => handleJoinChallenge(challenge.id)}
                          className="w-full px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors font-medium"
                        >
                          Aceitar Desafio
                        </button>
                      </div>
                    ))}
                </div>
              </div>
            )}

            {activeChallenges.length === 0 && myChallenges.length === 0 && (
              <div className="glass rounded-xl p-12 text-center">
                <p className="text-muted-foreground">Nenhum desafio disponível no momento.</p>
              </div>
            )}
          </div>
        )}

        {/* Leaderboard Tab */}
        {activeTab === 'leaderboard' && (
          <div className="space-y-6">
            <div className="glass rounded-xl p-6">
              <h3 className="text-xl font-bold mb-4">Ranking Global</h3>
              {leaderboard.length > 0 ? (
                <div className="space-y-2">
                  {leaderboard.map((entry, index) => (
                    <div
                      key={entry.user_id}
                      className={`p-4 rounded-lg flex items-center justify-between ${
                        index < 3 ? 'bg-indigo-500/10 border-2 border-indigo-500' : 'bg-background/50'
                      }`}
                    >
                      <div className="flex items-center gap-4">
                        <div className="text-2xl font-bold w-12 text-center">
                          {index === 0 ? '🥇' : index === 1 ? '🥈' : index === 2 ? '🥉' : `#${entry.rank}`}
                        </div>
                        <div>
                          <div className="font-bold">{entry.username}</div>
                          <div className="text-sm text-muted-foreground">
                            Nível {entry.level}
                          </div>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="font-bold text-indigo-400">
                          {entry.total_points.toLocaleString('pt-BR')} pontos
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-muted-foreground text-center py-8">
                  Nenhum usuário no ranking ainda.
                </p>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
