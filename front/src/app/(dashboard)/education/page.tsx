'use client'

import { useEffect, useState, Suspense } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import apiClient from '@/lib/api/client'
import toast from 'react-hot-toast'

type TabType = 'help' | 'courses' | 'finance' | 'investment' | 'progress'

const HELP_TOPICS = [
  { id: 'dashboard', name: 'Dashboard', icon: '📊', description: 'Visão geral das suas finanças' },
  { id: 'transactions', name: 'Transações', icon: '💸', description: 'Como registrar e gerenciar transações' },
  { id: 'accounts', name: 'Contas', icon: '🏦', description: 'Gerenciamento de contas bancárias' },
  { id: 'categories', name: 'Categorias', icon: '📁', description: 'Organize seus gastos por categorias' },
  { id: 'planning', name: 'Planejamento', icon: '📅', description: 'Planeje suas finanças' },
  { id: 'goals', name: 'Metas', icon: '🎯', description: 'Defina e acompanhe suas metas' },
  { id: 'investments', name: 'Investimentos', icon: '📈', description: 'Gerencie seus investimentos' },
  { id: 'reports', name: 'Relatórios', icon: '📊', description: 'Gere relatórios detalhados' },
  { id: 'workspaces', name: 'Workspaces', icon: '💼', description: 'Organize por contextos' },
  { id: 'insights', name: 'Insights', icon: '💡', description: 'Análises inteligentes' },
]

const COURSE_CATEGORIES = [
  { id: 'finance', name: 'Finanças Pessoais', icon: '💰', color: 'from-blue-500 to-cyan-500' },
  { id: 'investment', name: 'Investimentos', icon: '📈', color: 'from-green-500 to-emerald-500' },
]

const FINANCE_COURSES = [
  {
    id: '1',
    title: 'Fundamentos de Finanças Pessoais',
    description: 'Aprenda os conceitos básicos para gerenciar seu dinheiro',
    duration: 60,
    difficulty: 1,
    modules: 4,
    image: '💰',
  },
  {
    id: '2',
    title: 'Orçamento Pessoal',
    description: 'Como criar e manter um orçamento eficiente',
    duration: 45,
    difficulty: 1,
    modules: 3,
    image: '📊',
  },
  {
    id: '3',
    title: 'Como Sair das Dívidas',
    description: 'Estratégias práticas para eliminar dívidas',
    duration: 90,
    difficulty: 2,
    modules: 5,
    image: '💳',
  },
  {
    id: '4',
    title: 'Reserva de Emergência',
    description: 'Como construir e manter sua reserva de emergência',
    duration: 30,
    difficulty: 1,
    modules: 2,
    image: '🏦',
  },
  {
    id: '5',
    title: 'Planejamento para Aposentadoria',
    description: 'Prepare-se financeiramente para o futuro',
    duration: 120,
    difficulty: 3,
    modules: 6,
    image: '👴',
  },
]

const INVESTMENT_COURSES = [
  {
    id: '1',
    title: 'Introdução aos Investimentos',
    description: 'Conceitos básicos para começar a investir',
    duration: 60,
    difficulty: 1,
    modules: 4,
    image: '📈',
  },
  {
    id: '2',
    title: 'Renda Fixa para Iniciantes',
    description: 'Aprenda sobre CDB, LCI, LCA e Tesouro Direto',
    duration: 90,
    difficulty: 1,
    modules: 5,
    image: '🏛️',
  },
  {
    id: '3',
    title: 'Ações e Bolsa de Valores',
    description: 'Como investir em ações de forma inteligente',
    duration: 120,
    difficulty: 2,
    modules: 6,
    image: '📊',
  },
  {
    id: '4',
    title: 'Fundos de Investimento',
    description: 'Entenda como funcionam os fundos',
    duration: 75,
    difficulty: 2,
    modules: 4,
    image: '💼',
  },
  {
    id: '5',
    title: 'Análise Técnica',
    description: 'Técnicas avançadas de análise de gráficos',
    duration: 150,
    difficulty: 4,
    modules: 8,
    image: '📉',
  },
  {
    id: '6',
    title: 'Diversificação de Carteira',
    description: 'Como montar uma carteira diversificada',
    duration: 90,
    difficulty: 3,
    modules: 5,
    image: '🎯',
  },
]

function EducationPageContent() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const [activeTab, setActiveTab] = useState<TabType>('help')
  const [selectedTopic, setSelectedTopic] = useState<string | null>(null)
  const [helpContent, setHelpContent] = useState<any>(null)
  const [loading, setLoading] = useState(false)

  // Ler parâmetro 'tab' da URL
  useEffect(() => {
    const tabParam = searchParams.get('tab')
    if (tabParam && ['help', 'courses', 'finance', 'investment', 'progress'].includes(tabParam)) {
      setActiveTab(tabParam as TabType)
    }
  }, [searchParams])

  // Função para mudar de aba e atualizar URL
  const handleTabChange = (tab: TabType) => {
    setActiveTab(tab)
    router.push(`/education?tab=${tab}`, { scroll: false })
  }

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-3xl font-bold mb-2">📚 Educação Financeira</h1>
          <p className="text-muted-foreground">Aprenda sobre finanças pessoais e investimentos</p>
        </div>

        {/* Tabs */}
        <div className="flex gap-2 mb-6 overflow-x-auto">
          <button
            onClick={() => handleTabChange('help')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors whitespace-nowrap ${
              activeTab === 'help'
                ? 'bg-indigo-600 text-white'
                : 'bg-background hover:bg-muted'
            }`}
          >
            ❓ Ajuda da Aplicação
          </button>
          <button
            onClick={() => handleTabChange('courses')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors whitespace-nowrap ${
              activeTab === 'courses'
                ? 'bg-indigo-600 text-white'
                : 'bg-background hover:bg-muted'
            }`}
          >
            🎓 Centro de Cursos
          </button>
          <button
            onClick={() => handleTabChange('finance')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors whitespace-nowrap ${
              activeTab === 'finance'
                ? 'bg-indigo-600 text-white'
                : 'bg-background hover:bg-muted'
            }`}
          >
            💰 Finanças Pessoais
          </button>
          <button
            onClick={() => handleTabChange('investment')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors whitespace-nowrap ${
              activeTab === 'investment'
                ? 'bg-indigo-600 text-white'
                : 'bg-background hover:bg-muted'
            }`}
          >
            📈 Investimentos
          </button>
          <button
            onClick={() => handleTabChange('progress')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors whitespace-nowrap ${
              activeTab === 'progress'
                ? 'bg-indigo-600 text-white'
                : 'bg-background hover:bg-muted'
            }`}
          >
            📊 Meu Progresso
          </button>
        </div>

        {/* Content */}
        {activeTab === 'help' && (
          <HelpTab
            selectedTopic={selectedTopic}
            setSelectedTopic={setSelectedTopic}
            helpContent={helpContent}
            setHelpContent={setHelpContent}
            loading={loading}
            setLoading={setLoading}
          />
        )}
        {activeTab === 'courses' && <CoursesTab />}
        {activeTab === 'finance' && <FinanceCoursesTab />}
        {activeTab === 'investment' && <InvestmentCoursesTab />}
        {activeTab === 'progress' && <ProgressTab />}
      </div>
    </div>
  )
}

export default function EducationPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-background p-6">
        <div className="max-w-7xl mx-auto">
          <div className="glass rounded-xl p-12 text-center">Carregando...</div>
        </div>
      </div>
    }>
      <EducationPageContent />
    </Suspense>
  )
}

// ========== Help Tab ==========
function HelpTab({ selectedTopic, setSelectedTopic, helpContent, setHelpContent, loading, setLoading }: any) {
  const loadHelpContent = async (topic: string) => {
    setLoading(true)
    try {
      const response = await apiClient.get(`/education/help?topic=${topic}`)
      console.log('Resposta da API:', response.data)
      
      if (response.data) {
        // Verificar se a resposta tem a estrutura esperada
        if (response.data.title || response.data.content) {
          setHelpContent(response.data)
          setSelectedTopic(topic)
        } else {
          console.error('Estrutura de resposta inválida:', response.data)
          throw new Error('Estrutura de resposta inválida do servidor')
        }
      } else {
        throw new Error('Resposta vazia do servidor')
      }
    } catch (error: any) {
      console.error('Erro ao carregar ajuda:', error)
      console.error('Detalhes do erro:', {
        message: error.message,
        response: error.response?.data,
        status: error.response?.status,
        statusText: error.response?.statusText
      })
      
      let errorMessage = 'Erro ao carregar conteúdo de ajuda'
      if (error.response?.data?.detail) {
        errorMessage = error.response.data.detail
      } else if (error.response?.data?.message) {
        errorMessage = error.response.data.message
      } else if (error.message) {
        errorMessage = error.message
      }
      
      toast.error(errorMessage)
      setHelpContent(null)
      setSelectedTopic(null)
    } finally {
      setLoading(false)
    }
  }

  if (selectedTopic && helpContent) {
    // Converter markdown simples para HTML com melhor formatação
    const formatContent = (content: string) => {
      if (!content) return ''
      
      // Processar linha por linha para melhor controle
      const lines = content.split('\n')
      let html = ''
      let inList = false
      let inParagraph = false
      
      for (let i = 0; i < lines.length; i++) {
        const line = lines[i]
        const trimmed = line.trim()
        
        if (!trimmed) {
          if (inList) {
            html += '</ul>'
            inList = false
          }
          if (inParagraph) {
            html += '</p>'
            inParagraph = false
          }
          continue
        }
        
        // Headers
        if (trimmed.startsWith('#### ')) {
          if (inParagraph) { html += '</p>'; inParagraph = false }
          if (inList) { html += '</ul>'; inList = false }
          html += `<h4 class="text-lg font-bold mt-6 mb-3 text-indigo-400">${trimmed.substring(5)}</h4>`
        } else if (trimmed.startsWith('### ')) {
          if (inParagraph) { html += '</p>'; inParagraph = false }
          if (inList) { html += '</ul>'; inList = false }
          html += `<h3 class="text-xl font-bold mt-6 mb-3">${trimmed.substring(4)}</h3>`
        } else if (trimmed.startsWith('## ')) {
          if (inParagraph) { html += '</p>'; inParagraph = false }
          if (inList) { html += '</ul>'; inList = false }
          html += `<h2 class="text-2xl font-bold mt-8 mb-4">${trimmed.substring(3)}</h2>`
        } else if (trimmed.startsWith('# ')) {
          if (inParagraph) { html += '</p>'; inParagraph = false }
          if (inList) { html += '</ul>'; inList = false }
          html += `<h1 class="text-3xl font-bold mt-8 mb-4">${trimmed.substring(2)}</h1>`
        }
        // Blockquotes
        else if (trimmed.startsWith('> ')) {
          if (inParagraph) { html += '</p>'; inParagraph = false }
          if (inList) { html += '</ul>'; inList = false }
          const quoteText = trimmed.substring(2)
            .replace(/\*\*(.*?)\*\*/g, '<strong class="font-bold">$1</strong>')
          html += `<blockquote class="border-l-4 border-indigo-500 pl-4 py-3 my-4 bg-indigo-500/10 rounded-r-lg">${quoteText}</blockquote>`
        }
        // Lists
        else if (trimmed.startsWith('- ')) {
          if (inParagraph) { html += '</p>'; inParagraph = false }
          if (!inList) {
            html += '<ul class="list-disc list-inside space-y-2 my-4 ml-4">'
            inList = true
          }
          const listItem = trimmed.substring(2)
            .replace(/\*\*(.*?)\*\*/g, '<strong class="font-bold text-foreground">$1</strong>')
            .replace(/`(.*?)`/g, '<code class="bg-background px-2 py-1 rounded text-sm font-mono text-indigo-400">$1</code>')
          html += `<li class="mb-2">${listItem}</li>`
        }
        // Regular paragraph
        else {
          if (inList) {
            html += '</ul>'
            inList = false
          }
          if (!inParagraph) {
            html += '<p class="mb-4 leading-relaxed">'
            inParagraph = true
          } else {
            html += '<br />'
          }
          
          let paraText = trimmed
            .replace(/\*\*(.*?)\*\*/g, '<strong class="font-bold text-foreground">$1</strong>')
            .replace(/\*(.*?)\*/g, '<em class="italic">$1</em>')
            .replace(/`(.*?)`/g, '<code class="bg-background px-2 py-1 rounded text-sm font-mono text-indigo-400">$1</code>')
          
          html += paraText
        }
      }
      
      // Fechar tags abertas
      if (inList) html += '</ul>'
      if (inParagraph) html += '</p>'
      
      return html
    }

    return (
      <div className="space-y-6">
        <button
          onClick={() => {
            setSelectedTopic(null)
            setHelpContent(null)
          }}
          className="flex items-center gap-2 px-4 py-2 bg-background border border-border rounded-lg hover:bg-muted transition-colors"
        >
          <span>←</span>
          <span>Voltar para lista de tópicos</span>
        </button>

        <div className="glass rounded-xl overflow-hidden">
          {/* Header com imagem */}
          {helpContent.image && (
            <div className="relative h-48 bg-gradient-to-r from-indigo-500 to-purple-600">
              <img
                src={helpContent.image}
                alt={helpContent.title}
                className="w-full h-full object-cover opacity-50"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-background/90 to-transparent" />
              <div className="absolute bottom-0 left-0 right-0 p-6">
                <div className="text-5xl mb-2">{helpContent.icon || '📚'}</div>
                <h1 className="text-3xl font-bold mb-2">{helpContent.title}</h1>
                <p className="text-muted-foreground text-lg">{helpContent.description}</p>
              </div>
            </div>
          )}

          {!helpContent.image && (
            <div className="p-6 border-b border-border">
              <div className="flex items-center gap-4">
                <div className="text-5xl">{helpContent.icon || '📚'}</div>
                <div>
                  <h1 className="text-3xl font-bold mb-2">{helpContent.title}</h1>
                  <p className="text-muted-foreground text-lg">{helpContent.description}</p>
                </div>
              </div>
            </div>
          )}

          {/* Conteúdo */}
          <div className="p-6">
            <div
              className="help-content text-foreground leading-relaxed"
              dangerouslySetInnerHTML={{ __html: formatContent(helpContent.content || '') }}
            />

            {/* Dicas */}
            {helpContent.tips && helpContent.tips.length > 0 && (
              <div className="mt-8 p-6 bg-gradient-to-r from-indigo-500/10 to-purple-500/10 rounded-xl border border-indigo-500/20">
                <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
                  <span>💡</span>
                  <span>Dicas Pro</span>
                </h3>
                <ul className="space-y-3">
                  {helpContent.tips.map((tip: string, index: number) => (
                    <li key={index} className="flex items-start gap-3">
                      <span className="text-indigo-400 mt-1">✓</span>
                      <span>{tip}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      </div>
    )
  }

  return (
    <div>
      <h2 className="text-xl font-bold mb-4">Tópicos de Ajuda</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {HELP_TOPICS.map((topic) => (
          <button
            key={topic.id}
            onClick={() => loadHelpContent(topic.id)}
            className="glass rounded-xl p-6 text-left hover:bg-background/50 transition-colors"
          >
            <div className="text-4xl mb-3">{topic.icon}</div>
            <h3 className="font-bold text-lg mb-2">{topic.name}</h3>
            <p className="text-sm text-muted-foreground">{topic.description}</p>
          </button>
        ))}
      </div>
    </div>
  )
}

// ========== Courses Tab ==========
function CoursesTab() {
  const router = useRouter()
  const [loading, setLoading] = useState(true)
  const [seeding, setSeeding] = useState(false)
  const [courses, setCourses] = useState<any[]>([])

  useEffect(() => {
    loadCourses()
  }, [])

  const loadCourses = async () => {
    setLoading(true)
    try {
      const response = await apiClient.get('/education/content?content_type=course')
      setCourses(response.data || [])
    } catch (error: any) {
      // Se não houver cursos no banco, usar os cursos mockados
      setCourses([])
    } finally {
      setLoading(false)
    }
  }

  const seedCourses = async () => {
    if (!confirm('Deseja criar todos os cursos padrão no banco de dados?')) return

    setSeeding(true)
    try {
      const response = await apiClient.post('/education/seed-courses?force=false')
      if (response.data.total > 0) {
        toast.success(`${response.data.total} cursos criados com sucesso!`)
      } else {
        toast.info(response.data.message || 'Todos os cursos já existem')
      }
      loadCourses()
    } catch (error: any) {
      if (error.response?.data?.hint) {
        toast.error(`${error.response.data.message}. ${error.response.data.hint}`)
      } else {
        toast.error(error.response?.data?.detail || 'Erro ao criar cursos')
      }
    } finally {
      setSeeding(false)
    }
  }

  if (loading) {
    return <div className="glass rounded-xl p-12 text-center">Carregando...</div>
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold">Categorias de Cursos</h2>
        {courses.length === 0 && (
          <button
            onClick={seedCourses}
            disabled={seeding}
            className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 font-medium disabled:opacity-50"
          >
            {seeding ? 'Criando cursos...' : '📚 Criar Todos os Cursos'}
          </button>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        {COURSE_CATEGORIES.map((category) => (
          <div
            key={category.id}
            onClick={() => {
              if (category.id === 'finance') {
                router.push('/education?tab=finance')
              } else if (category.id === 'investment') {
                router.push('/education?tab=investment')
              }
            }}
            className={`glass rounded-xl p-8 bg-gradient-to-br ${category.color} cursor-pointer hover:scale-105 transition-transform`}
          >
            <div className="text-6xl mb-4">{category.icon}</div>
            <h3 className="text-2xl font-bold mb-2">{category.name}</h3>
            <p className="text-muted-foreground">Explore nossos cursos de {category.name.toLowerCase()}</p>
          </div>
        ))}
      </div>

      {courses.length > 0 ? (
        <>
          <h3 className="text-lg font-bold mb-4">Cursos Disponíveis ({courses.length})</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {courses.map((course) => (
              <div
                key={course.id}
                onClick={() => router.push(`/education/courses/${course.id}`)}
                className="glass rounded-xl p-6 hover:bg-background/50 transition-colors cursor-pointer"
              >
                {course.image_url && (
                  <img
                    src={course.image_url}
                    alt={course.title}
                    className="w-full h-32 object-cover rounded-lg mb-4"
                  />
                )}
                <h3 className="font-bold text-lg mb-2">{course.title}</h3>
                <p className="text-sm text-muted-foreground mb-4 line-clamp-2">{course.description}</p>
                <div className="flex items-center gap-4 text-xs text-muted-foreground">
                  {course.duration_minutes && <span>⏱️ {course.duration_minutes} min</span>}
                  <span>
                    {['Iniciante', 'Básico', 'Intermediário', 'Avançado', 'Expert'][course.difficulty_level - 1]}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </>
      ) : (
        <div className="glass rounded-xl p-12 text-center">
          <p className="text-muted-foreground mb-4">Nenhum curso disponível ainda</p>
          <button
            onClick={seedCourses}
            disabled={seeding}
            className="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 font-medium disabled:opacity-50"
          >
            {seeding ? 'Criando cursos...' : '📚 Criar Todos os Cursos'}
          </button>
        </div>
      )}
    </div>
  )
}

// ========== Finance Courses Tab ==========
function FinanceCoursesTab() {
  const router = useRouter()
  const [loading, setLoading] = useState(true)
  const [seeding, setSeeding] = useState(false)
  const [courses, setCourses] = useState<any[]>([])

  useEffect(() => {
    loadCourses()
  }, [])

  const loadCourses = async () => {
    setLoading(true)
    try {
      const response = await apiClient.get('/education/content?content_type=course')
      const allCourses = response.data || []
      // Filtrar cursos de finanças pessoais (por tags ou título)
      const financeCourses = allCourses.filter((c: any) => {
        const tags = c.tags || []
        const title = (c.title || '').toLowerCase()
        const description = (c.description || '').toLowerCase()
        return (
          tags.some((tag: string) => 
            tag.toLowerCase().includes('finança') || 
            tag.toLowerCase().includes('pessoal') ||
            tag.toLowerCase().includes('orçamento') ||
            tag.toLowerCase().includes('dívida') ||
            tag.toLowerCase().includes('reserva') ||
            tag.toLowerCase().includes('aposentadoria')
          ) ||
          title.includes('finança') ||
          title.includes('orçamento') ||
          title.includes('dívida') ||
          title.includes('reserva') ||
          title.includes('aposentadoria') ||
          description.includes('finança pessoal')
        )
      })
      setCourses(financeCourses)
    } catch (error: any) {
      setCourses([])
    } finally {
      setLoading(false)
    }
  }

  const seedCourses = async () => {
    if (!confirm('Deseja criar todos os cursos padrão no banco de dados?')) return

    setSeeding(true)
    try {
      const response = await apiClient.post('/education/seed-courses?force=false')
      if (response.data.total > 0) {
        toast.success(`${response.data.total} cursos criados com sucesso!`)
      } else {
        toast.info(response.data.message || 'Todos os cursos já existem')
      }
      loadCourses()
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Erro ao criar cursos')
    } finally {
      setSeeding(false)
    }
  }

  if (loading) {
    return <div className="glass rounded-xl p-12 text-center">Carregando...</div>
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold">Cursos de Finanças Pessoais</h2>
        <div className="flex items-center gap-4">
          <div className="text-sm text-muted-foreground">{courses.length} cursos disponíveis</div>
          {courses.length === 0 && (
            <button
              onClick={seedCourses}
              disabled={seeding}
              className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 font-medium disabled:opacity-50 text-sm"
            >
              {seeding ? 'Criando...' : '📚 Criar Cursos'}
            </button>
          )}
        </div>
      </div>
      {courses.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {courses.map((course) => (
            <CourseCard key={course.id} course={course} />
          ))}
        </div>
      ) : (
        <div className="glass rounded-xl p-12 text-center">
          <p className="text-muted-foreground mb-4">Nenhum curso de finanças pessoais disponível</p>
          <button
            onClick={seedCourses}
            disabled={seeding}
            className="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 font-medium disabled:opacity-50"
          >
            {seeding ? 'Criando cursos...' : '📚 Criar Todos os Cursos'}
          </button>
        </div>
      )}
    </div>
  )
}

// ========== Investment Courses Tab ==========
function InvestmentCoursesTab() {
  const router = useRouter()
  const [loading, setLoading] = useState(true)
  const [seeding, setSeeding] = useState(false)
  const [courses, setCourses] = useState<any[]>([])

  useEffect(() => {
    loadCourses()
  }, [])

  const loadCourses = async () => {
    setLoading(true)
    try {
      const response = await apiClient.get('/education/content?content_type=course')
      const allCourses = response.data || []
      // Filtrar cursos de investimentos (por tags ou título)
      const investmentCourses = allCourses.filter((c: any) => {
        const tags = c.tags || []
        const title = (c.title || '').toLowerCase()
        const description = (c.description || '').toLowerCase()
        return (
          tags.some((tag: string) => 
            tag.toLowerCase().includes('investimento') ||
            tag.toLowerCase().includes('ação') ||
            tag.toLowerCase().includes('renda fixa') ||
            tag.toLowerCase().includes('fundos') ||
            tag.toLowerCase().includes('análise técnica') ||
            tag.toLowerCase().includes('diversificação')
          ) ||
          title.includes('investimento') ||
          title.includes('ação') ||
          title.includes('renda fixa') ||
          title.includes('fundos') ||
          title.includes('análise técnica') ||
          title.includes('diversificação') ||
          description.includes('investir')
        )
      })
      setCourses(investmentCourses)
    } catch (error: any) {
      setCourses([])
    } finally {
      setLoading(false)
    }
  }

  const seedCourses = async () => {
    if (!confirm('Deseja criar todos os cursos padrão no banco de dados?')) return

    setSeeding(true)
    try {
      const response = await apiClient.post('/education/seed-courses?force=false')
      if (response.data.total > 0) {
        toast.success(`${response.data.total} cursos criados com sucesso!`)
      } else {
        toast.info(response.data.message || 'Todos os cursos já existem')
      }
      loadCourses()
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Erro ao criar cursos')
    } finally {
      setSeeding(false)
    }
  }

  if (loading) {
    return <div className="glass rounded-xl p-12 text-center">Carregando...</div>
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold">Cursos de Investimentos</h2>
        <div className="flex items-center gap-4">
          <div className="text-sm text-muted-foreground">{courses.length} cursos disponíveis</div>
          {courses.length === 0 && (
            <button
              onClick={seedCourses}
              disabled={seeding}
              className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 font-medium disabled:opacity-50 text-sm"
            >
              {seeding ? 'Criando...' : '📚 Criar Cursos'}
            </button>
          )}
        </div>
      </div>
      {courses.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {courses.map((course) => (
            <CourseCard key={course.id} course={course} />
          ))}
        </div>
      ) : (
        <div className="glass rounded-xl p-12 text-center">
          <p className="text-muted-foreground mb-4">Nenhum curso de investimentos disponível</p>
          <button
            onClick={seedCourses}
            disabled={seeding}
            className="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 font-medium disabled:opacity-50"
          >
            {seeding ? 'Criando cursos...' : '📚 Criar Todos os Cursos'}
          </button>
        </div>
      )}
    </div>
  )
}

// ========== Course Card ==========
function CourseCard({ course }: { course: any }) {
  const router = useRouter()
  const difficultyColors = ['bg-green-500/20 text-green-400', 'bg-blue-500/20 text-blue-400', 'bg-yellow-500/20 text-yellow-400', 'bg-orange-500/20 text-orange-400', 'bg-red-500/20 text-red-400']
  const difficultyLabels = ['Iniciante', 'Básico', 'Intermediário', 'Avançado', 'Expert']
  
  const difficulty = course.difficulty || course.difficulty_level || 1
  const duration = course.duration || course.duration_minutes
  const image = course.image || course.image_url

  const handleStart = () => {
    if (course.id && course.id.length > 10) {
      // ID válido do banco
      router.push(`/education/courses/${course.id}`)
    } else {
      // Curso mockado - mostrar mensagem
      toast.error('Este curso ainda não está disponível. Em breve!')
    }
  }

  return (
    <div className="glass rounded-xl p-6 hover:bg-background/50 transition-colors">
      {image && (
        <div className="mb-4">
          {image.startsWith('http') ? (
            <img src={image} alt={course.title} className="w-full h-32 object-cover rounded-lg" />
          ) : (
            <div className="text-5xl">{image}</div>
          )}
        </div>
      )}
      <h3 className="font-bold text-lg mb-2">{course.title}</h3>
      <p className="text-sm text-muted-foreground mb-4 line-clamp-2">{course.description}</p>
      <div className="flex items-center gap-4 text-xs text-muted-foreground mb-4">
        {duration && <span>⏱️ {duration} min</span>}
        {course.modules && <span>📚 {course.modules} módulos</span>}
      </div>
      <div className="flex items-center justify-between">
        <span className={`px-2 py-1 rounded text-xs font-semibold ${difficultyColors[difficulty - 1] || difficultyColors[0]}`}>
          {difficultyLabels[difficulty - 1] || difficultyLabels[0]}
        </span>
        <button
          onClick={handleStart}
          className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 text-sm font-medium"
        >
          Começar
        </button>
      </div>
    </div>
  )
}

// ========== Progress Tab ==========
function ProgressTab() {
  const router = useRouter()
  const [progress, setProgress] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadProgress()
  }, [])

  const loadProgress = async () => {
    setLoading(true)
    try {
      const response = await apiClient.get('/education/progress')
      setProgress(response.data)
    } catch (error: any) {
      toast.error('Erro ao carregar progresso')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="glass rounded-xl p-12 text-center">Carregando...</div>
  }

  if (!progress) {
    return <div className="glass rounded-xl p-12 text-center">Nenhum progresso registrado</div>
  }

  return (
    <div className="space-y-6">
      <h2 className="text-xl font-bold mb-4">Meu Progresso</h2>
      
      {/* Estatísticas Gerais */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="glass rounded-xl p-4">
          <p className="text-sm text-muted-foreground mb-1">Total de Conteúdo</p>
          <p className="text-2xl font-bold">{progress.total_content || 0}</p>
        </div>
        <div className="glass rounded-xl p-4">
          <p className="text-sm text-muted-foreground mb-1">Concluídos</p>
          <p className="text-2xl font-bold text-green-400">{progress.completed_content || 0}</p>
        </div>
        <div className="glass rounded-xl p-4">
          <p className="text-sm text-muted-foreground mb-1">Em Progresso</p>
          <p className="text-2xl font-bold text-yellow-400">{progress.in_progress_content || 0}</p>
        </div>
        <div className="glass rounded-xl p-4">
          <p className="text-sm text-muted-foreground mb-1">Taxa de Conclusão</p>
          <p className="text-2xl font-bold">{progress.completion_rate || 0}%</p>
        </div>
      </div>

      {/* Barra de Progresso Geral */}
      <div className="glass rounded-xl p-6">
        <h3 className="font-bold mb-4">Progresso Geral</h3>
        <div className="w-full bg-background rounded-full h-4 mb-2">
          <div
            className="h-4 rounded-full bg-gradient-to-r from-indigo-500 to-purple-500"
            style={{ width: `${progress.completion_rate || 0}%` }}
          />
        </div>
        <p className="text-sm text-muted-foreground">
          {progress.completed_content || 0} de {progress.total_content || 0} conteúdos concluídos
        </p>
      </div>

      {/* Detalhes do Progresso */}
      {progress.progress_details && progress.progress_details.length > 0 && (
        <div className="glass rounded-xl p-6">
          <h3 className="font-bold mb-4">Detalhes do Progresso</h3>
          <div className="space-y-4">
            {progress.progress_details.map((detail: any, index: number) => (
              <div
                key={index}
                className="p-4 bg-background/50 rounded-lg cursor-pointer hover:bg-background/80 transition-colors"
                onClick={() => router.push(`/education/courses/${detail.content_id}`)}
              >
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-semibold">{detail.content_title}</h4>
                  <span className={`px-2 py-1 rounded text-xs font-semibold ${
                    detail.is_completed
                      ? 'bg-green-500/20 text-green-400'
                      : 'bg-yellow-500/20 text-yellow-400'
                  }`}>
                    {detail.is_completed ? 'Concluído' : 'Em Progresso'}
                  </span>
                </div>
                <div className="w-full bg-background rounded-full h-2 mb-2">
                  <div
                    className="h-2 rounded-full bg-gradient-to-r from-indigo-500 to-purple-500"
                    style={{ width: `${detail.progress_percentage}%` }}
                  />
                </div>
                <div className="flex items-center justify-between text-xs text-muted-foreground">
                  <span>{detail.progress_percentage}% completo</span>
                  {detail.last_accessed_at && (
                    <span>
                      Último acesso: {new Date(detail.last_accessed_at).toLocaleDateString('pt-BR')}
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
