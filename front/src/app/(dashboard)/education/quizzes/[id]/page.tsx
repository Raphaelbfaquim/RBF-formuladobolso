'use client'

import { useEffect, useState } from 'react'
import { useRouter, useParams } from 'next/navigation'
import apiClient from '@/lib/api/client'
import toast from 'react-hot-toast'

export default function QuizPage() {
  const router = useRouter()
  const params = useParams()
  const quizId = params.id as string
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [quiz, setQuiz] = useState<any>(null)
  const [answers, setAnswers] = useState<Record<string, any>>({})
  const [result, setResult] = useState<any>(null)

  useEffect(() => {
    loadQuiz()
  }, [quizId])

  const loadQuiz = async () => {
    setLoading(true)
    try {
      const response = await apiClient.get(`/education/quizzes/${quizId}`)
      setQuiz(response.data)
    } catch (error: any) {
      toast.error('Erro ao carregar quiz')
      router.push('/education')
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async () => {
    if (Object.keys(answers).length < quiz.questions.length) {
      toast.error('Por favor, responda todas as perguntas')
      return
    }

    setSubmitting(true)
    try {
      const response = await apiClient.post(`/education/quizzes/${quizId}/attempt`, answers)
      setResult(response.data)
      toast.success(
        response.data.is_passed
          ? `🎉 Parabéns! Você passou com ${response.data.score}%!`
          : `Você obteve ${response.data.score}%. Tente novamente!`
      )
    } catch (error: any) {
      toast.error('Erro ao submeter quiz')
    } finally {
      setSubmitting(false)
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

  if (!quiz) {
    return null
  }

  if (result) {
    return (
      <div className="min-h-screen bg-background p-6">
        <div className="max-w-4xl mx-auto">
          <div className="glass rounded-xl p-8 text-center">
            <div className={`text-6xl mb-4 ${result.is_passed ? 'text-green-400' : 'text-red-400'}`}>
              {result.is_passed ? '🎉' : '😔'}
            </div>
            <h1 className="text-3xl font-bold mb-4">
              {result.is_passed ? 'Parabéns! Você passou!' : 'Tente novamente!'}
            </h1>
            <div className="space-y-4 mb-6">
              <div>
                <p className="text-muted-foreground mb-1">Sua Pontuação</p>
                <p className={`text-4xl font-bold ${result.is_passed ? 'text-green-400' : 'text-red-400'}`}>
                  {result.score}%
                </p>
              </div>
              <div>
                <p className="text-muted-foreground mb-1">Respostas Corretas</p>
                <p className="text-2xl font-bold">
                  {result.correct_answers} de {result.total_questions}
                </p>
              </div>
              <div>
                <p className="text-muted-foreground mb-1">Pontuação Mínima</p>
                <p className="text-xl font-bold">{result.passing_score}%</p>
              </div>
            </div>
            <div className="flex gap-4 justify-center">
              <button
                onClick={() => {
                  setResult(null)
                  setAnswers({})
                }}
                className="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 font-medium"
              >
                Tentar Novamente
              </button>
              <button
                onClick={() => router.push('/education')}
                className="px-6 py-3 bg-background border border-border rounded-lg hover:bg-muted font-medium"
              >
                Voltar para Educação
              </button>
            </div>
          </div>
        </div>
      </div>
    )
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

        <div className="glass rounded-xl p-6">
          <h1 className="text-3xl font-bold mb-2">{quiz.title}</h1>
          {quiz.description && (
            <p className="text-muted-foreground mb-6">{quiz.description}</p>
          )}

          <div className="space-y-6">
            {quiz.questions.map((question: any, index: number) => {
              const questionId = question.id || `q${index}`
              return (
                <div key={index} className="p-6 bg-background/50 rounded-lg">
                  <h3 className="font-semibold text-lg mb-4">
                    {index + 1}. {question.question || question.text}
                  </h3>
                  <div className="space-y-2">
                    {question.options && question.options.map((option: string, optIndex: number) => (
                      <label
                        key={optIndex}
                        className={`flex items-center gap-3 p-3 rounded-lg cursor-pointer transition-colors ${
                          answers[questionId] === option
                            ? 'bg-indigo-500/20 border-2 border-indigo-500'
                            : 'bg-background border-2 border-transparent hover:bg-background/80'
                        }`}
                      >
                        <input
                          type="radio"
                          name={questionId}
                          value={option}
                          checked={answers[questionId] === option}
                          onChange={(e) => setAnswers({ ...answers, [questionId]: e.target.value })}
                          className="w-4 h-4"
                        />
                        <span>{option}</span>
                      </label>
                    ))}
                  </div>
                </div>
              )
            })}
          </div>

          <div className="mt-6 flex items-center justify-between">
            <p className="text-sm text-muted-foreground">
              {Object.keys(answers).length} de {quiz.questions.length} perguntas respondidas
            </p>
            <button
              onClick={handleSubmit}
              disabled={submitting || Object.keys(answers).length < quiz.questions.length}
              className="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 font-medium disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {submitting ? 'Enviando...' : 'Enviar Respostas'}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

