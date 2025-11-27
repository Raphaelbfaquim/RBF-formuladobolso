'use client'

import { useEffect, useState } from 'react'
import { useRouter, useParams } from 'next/navigation'
import apiClient from '@/lib/api/client'
import toast from 'react-hot-toast'

export default function CoursePage() {
  const router = useRouter()
  const params = useParams()
  const courseId = params.id as string
  const [loading, setLoading] = useState(true)
  const [course, setCourse] = useState<any>(null)
  const [progress, setProgress] = useState(0)

  useEffect(() => {
    loadCourse()
  }, [courseId])

  const loadCourse = async () => {
    setLoading(true)
    try {
      const response = await apiClient.get(`/education/content/${courseId}`)
      setCourse(response.data)
      setProgress(response.data.progress?.progress_percentage || 0)
    } catch (error: any) {
      toast.error('Erro ao carregar curso')
      router.push('/education')
    } finally {
      setLoading(false)
    }
  }

  const updateProgress = async (newProgress: number) => {
    try {
      await apiClient.put(`/education/content/${courseId}/progress?progress_percentage=${newProgress}`)
      setProgress(newProgress)
      if (newProgress >= 100) {
        toast.success('🎉 Curso concluído! Parabéns!')
      }
    } catch (error: any) {
      toast.error('Erro ao atualizar progresso')
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-background p-6">
        <div className="max-w-4xl mx-auto">
          <div className="glass rounded-xl p-12 text-center">Carregando...</div>
        </div>
      </div>
    )
  }

  if (!course) {
    return null
  }

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-4xl mx-auto">
        <button
          onClick={() => router.back()}
          className="mb-4 flex items-center gap-2 px-4 py-2 bg-background border border-border rounded-lg hover:bg-muted transition-colors"
        >
          <span>←</span>
          <span>Voltar</span>
        </button>

        <div className="glass rounded-xl overflow-hidden">
          {/* Header */}
          {course.image_url && (
            <div className="relative h-64 bg-gradient-to-r from-indigo-500 to-purple-600">
              <img
                src={course.image_url}
                alt={course.title}
                className="w-full h-full object-cover opacity-50"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-background/90 to-transparent" />
            </div>
          )}

          <div className="p-6">
            <h1 className="text-3xl font-bold mb-2">{course.title}</h1>
            {course.description && (
              <p className="text-muted-foreground text-lg mb-4">{course.description}</p>
            )}

            {/* Progresso */}
            <div className="mb-6">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium">Progresso</span>
                <span className="text-sm text-muted-foreground">{progress}%</span>
              </div>
              <div className="w-full bg-background rounded-full h-3">
                <div
                  className="h-3 rounded-full bg-gradient-to-r from-indigo-500 to-purple-500"
                  style={{ width: `${progress}%` }}
                />
              </div>
              {progress < 100 && (
                <div className="flex gap-2 mt-4">
                  <button
                    onClick={() => updateProgress(Math.min(progress + 25, 100))}
                    className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 text-sm"
                  >
                    +25%
                  </button>
                  <button
                    onClick={() => updateProgress(100)}
                    className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 text-sm"
                  >
                    Marcar como Concluído
                  </button>
                </div>
              )}
            </div>

            {/* Informações */}
            <div className="grid grid-cols-3 gap-4 mb-6">
              <div className="p-4 bg-background/50 rounded-lg">
                <p className="text-sm text-muted-foreground mb-1">Duração</p>
                <p className="font-semibold">{course.duration_minutes || 'N/A'} min</p>
              </div>
              <div className="p-4 bg-background/50 rounded-lg">
                <p className="text-sm text-muted-foreground mb-1">Dificuldade</p>
                <p className="font-semibold">
                  {['Iniciante', 'Básico', 'Intermediário', 'Avançado', 'Expert'][course.difficulty_level - 1] || 'N/A'}
                </p>
              </div>
              <div className="p-4 bg-background/50 rounded-lg">
                <p className="text-sm text-muted-foreground mb-1">Visualizações</p>
                <p className="font-semibold">{course.views_count || 0}</p>
              </div>
            </div>

            {/* Conteúdo */}
            {course.content && (
              <div className="prose prose-invert max-w-none">
                <div
                  className="text-foreground leading-relaxed"
                  dangerouslySetInnerHTML={{ __html: course.content }}
                />
              </div>
            )}

            {/* Vídeo */}
            {course.video_url && (
              <div className="mt-6">
                <h2 className="text-xl font-bold mb-4">Vídeo</h2>
                <div className="aspect-video rounded-lg overflow-hidden">
                  <iframe
                    src={course.video_url}
                    className="w-full h-full"
                    allowFullScreen
                  />
                </div>
              </div>
            )}

            {/* Tags */}
            {course.tags && course.tags.length > 0 && (
              <div className="mt-6 flex flex-wrap gap-2">
                {course.tags.map((tag: string, index: number) => (
                  <span
                    key={index}
                    className="px-3 py-1 bg-indigo-500/20 text-indigo-400 rounded-full text-sm"
                  >
                    {tag}
                  </span>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

