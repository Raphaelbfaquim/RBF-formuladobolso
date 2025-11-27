'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import apiClient from '@/lib/api/client'
import toast from 'react-hot-toast'

interface CalendarEvent {
  id: string
  event_type: string
  title: string
  description: string | null
  start_date: string
  end_date: string | null
  all_day: boolean
  user_id: string
  user_name: string | null
  workspace_id: string | null
  workspace_name: string | null
  family_id: string | null
  color: string | null
  icon: string | null
  location: string | null
  is_shared: boolean
  is_public: boolean
  created_by_name: string | null
  comments_count: number
  participants_count: number
  user_participation_status: string | null
  related_bill_id: string | null
  related_transaction_id: string | null
  related_goal_id: string | null
}

interface EventsByDate {
  date: string
  events: CalendarEvent[]
}

const EVENT_TYPE_COLORS: Record<string, string> = {
  transaction: 'bg-green-500/20 text-green-400 border-green-500/30',
  bill: 'bg-orange-500/20 text-orange-400 border-orange-500/30',
  goal: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
  goal_contribution: 'bg-indigo-500/20 text-indigo-400 border-indigo-500/30',
  travel: 'bg-purple-500/20 text-purple-400 border-purple-500/30',
  birthday: 'bg-pink-500/20 text-pink-400 border-pink-500/30',
  important_event: 'bg-red-500/20 text-red-400 border-red-500/30',
  reminder: 'bg-gray-500/20 text-gray-400 border-gray-500/30',
  custom: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
}

const EVENT_TYPE_ICONS: Record<string, string> = {
  transaction: '💰',
  bill: '📋',
  goal: '🎯',
  goal_contribution: '💵',
  travel: '✈️',
  birthday: '🎂',
  important_event: '⭐',
  reminder: '📝',
  custom: '📅',
}

const EVENT_TYPE_LABELS: Record<string, string> = {
  transaction: 'Transação',
  bill: 'Conta a Pagar/Receber',
  goal: 'Meta',
  goal_contribution: 'Contribuição para Meta',
  travel: 'Viagem',
  birthday: 'Aniversário',
  important_event: 'Evento Importante',
  reminder: 'Lembrete',
  custom: 'Personalizado',
}

export default function CalendarPage() {
  const router = useRouter()
  const [loading, setLoading] = useState(true)
  const [currentMonth, setCurrentMonth] = useState(new Date().getMonth() + 1)
  const [currentYear, setCurrentYear] = useState(new Date().getFullYear())
  const [eventsByDate, setEventsByDate] = useState<Record<string, CalendarEvent[]>>({})
  const [selectedDate, setSelectedDate] = useState<string | null>(null)
  const [showEventModal, setShowEventModal] = useState(false)
  const [showCreateModal, setShowCreateModal] = useState(false)

  useEffect(() => {
    loadEvents()
  }, [currentMonth, currentYear])

  const loadEvents = async () => {
    setLoading(true)
    try {
      const response = await apiClient.get(`/calendar/month?month=${currentMonth}&year=${currentYear}`)
      const data = response.data

      // Converter array de events_by_date para objeto
      const eventsMap: Record<string, CalendarEvent[]> = {}
      data.events_by_date.forEach((item: EventsByDate) => {
        eventsMap[item.date] = item.events
      })
      setEventsByDate(eventsMap)
    } catch (error: any) {
      if (error.response?.status === 401) {
        router.push('/login')
      } else {
        toast.error('Erro ao carregar eventos')
      }
    } finally {
      setLoading(false)
    }
  }

  const handleMonthChange = (direction: 'prev' | 'next') => {
    if (direction === 'prev') {
      if (currentMonth === 1) {
        setCurrentMonth(12)
        setCurrentYear(currentYear - 1)
      } else {
        setCurrentMonth(currentMonth - 1)
      }
    } else {
      if (currentMonth === 12) {
        setCurrentMonth(1)
        setCurrentYear(currentYear + 1)
      } else {
        setCurrentMonth(currentMonth + 1)
      }
    }
  }

  const handleSyncFinancialEvents = async () => {
    try {
      const response = await apiClient.post('/calendar/sync-financial-events')
      toast.success(`✅ ${response.data.created} eventos financeiros sincronizados!`)
      loadEvents() // Recarregar eventos
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Erro ao sincronizar eventos')
    }
  }

  const getDaysInMonth = (month: number, year: number) => {
    return new Date(year, month, 0).getDate()
  }

  const getFirstDayOfMonth = (month: number, year: number) => {
    return new Date(year, month - 1, 1).getDay()
  }

  const formatDate = (year: number, month: number, day: number) => {
    return `${year}-${String(month).padStart(2, '0')}-${String(day).padStart(2, '0')}`
  }

  const getEventsForDate = (date: string) => {
    return eventsByDate[date] || []
  }

  const monthNames = [
    'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
    'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
  ]

  const weekDays = ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb']

  const daysInMonth = getDaysInMonth(currentMonth, currentYear)
  const firstDay = getFirstDayOfMonth(currentMonth, currentYear)
  const days = Array.from({ length: daysInMonth }, (_, i) => i + 1)
  const emptyDays = Array.from({ length: firstDay }, (_, i) => i)

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-3xl font-bold mb-2">📅 Calendário</h1>
            <p className="text-muted-foreground">
              Visualize eventos financeiros e pessoais compartilhados
            </p>
          </div>
          <div className="flex gap-3">
            <button
              onClick={handleSyncFinancialEvents}
              className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 font-medium text-sm"
            >
              🔄 Sincronizar Eventos Financeiros
            </button>
            <button
              onClick={() => setShowCreateModal(true)}
              className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 font-medium"
            >
              + Novo Evento
            </button>
          </div>
        </div>

        {/* Navegação do Mês */}
        <div className="glass rounded-xl p-4 mb-6 flex items-center justify-between">
          <button
            onClick={() => handleMonthChange('prev')}
            className="p-2 hover:bg-background rounded-lg transition-colors"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </button>
          <h2 className="text-2xl font-bold">
            {monthNames[currentMonth - 1]} {currentYear}
          </h2>
          <button
            onClick={() => handleMonthChange('next')}
            className="p-2 hover:bg-background rounded-lg transition-colors"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </button>
        </div>

        {/* Calendário */}
        {loading ? (
          <div className="glass rounded-xl p-12 text-center">
            <p className="text-muted-foreground">Carregando eventos...</p>
          </div>
        ) : (
          <div className="glass rounded-xl p-6">
            {/* Dias da Semana */}
            <div className="grid grid-cols-7 gap-2 mb-4">
              {weekDays.map((day) => (
                <div key={day} className="text-center font-semibold text-muted-foreground py-2">
                  {day}
                </div>
              ))}
            </div>

            {/* Dias do Mês */}
            <div className="grid grid-cols-7 gap-2">
              {/* Dias vazios no início */}
              {emptyDays.map((_, index) => (
                <div key={`empty-${index}`} className="aspect-square"></div>
              ))}

              {/* Dias do mês */}
              {days.map((day) => {
                const date = formatDate(currentYear, currentMonth, day)
                const events = getEventsForDate(date)
                const isToday = date === new Date().toISOString().split('T')[0]

                return (
                  <div
                    key={day}
                    className={`aspect-square p-2 border-2 rounded-lg cursor-pointer transition-all hover:border-indigo-500 ${
                      isToday
                        ? 'border-indigo-500 bg-indigo-500/10'
                        : 'border-border hover:bg-background'
                    }`}
                    onClick={() => {
                      setSelectedDate(date)
                      setShowEventModal(true)
                    }}
                  >
                    <div className={`text-sm font-semibold mb-1 ${isToday ? 'text-indigo-400' : ''}`}>
                      {day}
                    </div>
                    <div className="space-y-1">
                      {events.slice(0, 3).map((event) => (
                        <div
                          key={event.id}
                          className={`text-xs px-1 py-0.5 rounded truncate ${
                            EVENT_TYPE_COLORS[event.event_type] || EVENT_TYPE_COLORS.custom
                          }`}
                          title={event.title}
                        >
                          {event.icon || EVENT_TYPE_ICONS[event.event_type] || '📅'} {event.title}
                        </div>
                      ))}
                      {events.length > 3 && (
                        <div className="text-xs text-muted-foreground">
                          +{events.length - 3} mais
                        </div>
                      )}
                    </div>
                  </div>
                )
              })}
            </div>
          </div>
        )}

        {/* Legenda */}
        <div className="mt-6 glass rounded-xl p-4">
          <h3 className="font-semibold mb-3">Legenda</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {Object.entries(EVENT_TYPE_ICONS).map(([type, icon]) => (
              <div key={type} className="flex items-center gap-2 text-sm">
                <span className={`px-2 py-1 rounded text-xs ${
                  EVENT_TYPE_COLORS[type] || EVENT_TYPE_COLORS.custom
                }`}>
                  {icon}
                </span>
                <span className="text-muted-foreground">
                  {EVENT_TYPE_LABELS[type] || type.replace('_', ' ')}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Modal de Eventos do Dia */}
      {showEventModal && selectedDate && (
        <EventDayModal
          date={selectedDate}
          events={getEventsForDate(selectedDate)}
          onClose={() => {
            setShowEventModal(false)
            setSelectedDate(null)
          }}
          onRefresh={loadEvents}
        />
      )}

      {/* Modal de Criar Evento */}
      {showCreateModal && (
        <CreateEventModal
          onClose={() => {
            setShowCreateModal(false)
          }}
          onRefresh={loadEvents}
        />
      )}
    </div>
  )
}

// Modal de Eventos do Dia
function EventDayModal({
  date,
  events,
  onClose,
  onRefresh,
}: {
  date: string
  events: CalendarEvent[]
  onClose: () => void
  onRefresh: () => void
}) {
  const [selectedEvent, setSelectedEvent] = useState<CalendarEvent | null>(null)

  const formatDateDisplay = (dateStr: string) => {
    const d = new Date(dateStr)
    return d.toLocaleDateString('pt-BR', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    })
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-background rounded-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-2xl font-bold">{formatDateDisplay(date)}</h2>
            <button
              onClick={onClose}
              className="p-2 hover:bg-muted rounded-lg transition-colors"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {events.length === 0 ? (
            <p className="text-muted-foreground text-center py-8">
              Nenhum evento neste dia
            </p>
          ) : (
            <div className="space-y-3">
              {events.map((event) => (
                <div
                  key={event.id}
                  className={`p-4 rounded-lg border-2 cursor-pointer transition-all hover:scale-[1.02] ${
                    EVENT_TYPE_COLORS[event.event_type] || EVENT_TYPE_COLORS.custom
                  }`}
                  onClick={() => setSelectedEvent(event)}
                >
                  <div className="flex items-start gap-3">
                    <span className="text-2xl">{event.icon || EVENT_TYPE_ICONS[event.event_type] || '📅'}</span>
                    <div className="flex-1">
                      <h3 className="font-semibold mb-1">{event.title}</h3>
                      {event.description && (
                        <p className="text-sm text-muted-foreground mb-2">{event.description}</p>
                      )}
                      <div className="flex items-center gap-4 text-xs text-muted-foreground">
                        {event.location && <span>📍 {event.location}</span>}
                        {event.created_by_name && <span>Por: {event.created_by_name}</span>}
                        {event.comments_count > 0 && <span>💬 {event.comments_count}</span>}
                        {event.participants_count > 0 && <span>👥 {event.participants_count}</span>}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Modal de Detalhes do Evento */}
      {selectedEvent && (
        <EventDetailModal
          event={selectedEvent}
          onClose={() => setSelectedEvent(null)}
          onRefresh={onRefresh}
        />
      )}
    </div>
  )
}

// Modal de Detalhes do Evento
function EventDetailModal({
  event,
  onClose,
  onRefresh,
}: {
  event: CalendarEvent
  onClose: () => void
  onRefresh: () => void
}) {
  const [comments, setComments] = useState<any[]>([])
  const [newComment, setNewComment] = useState('')
  const [participationStatus, setParticipationStatus] = useState(event.user_participation_status || 'not_responded')
  const [loading, setLoading] = useState(false)
  const [billStatus, setBillStatus] = useState<string | null>(null)

  useEffect(() => {
    loadComments()
    if (event.event_type === 'bill' && event.related_bill_id) {
      loadBillStatus()
    }
  }, [event.id, event.event_type, event.related_bill_id])

  const loadComments = async () => {
    try {
      const response = await apiClient.get(`/calendar/${event.id}/comments`)
      setComments(response.data)
    } catch (error: any) {
      toast.error('Erro ao carregar comentários')
    }
  }

  const loadBillStatus = async () => {
    if (!event.related_bill_id) return
    try {
      const response = await apiClient.get(`/bills/${event.related_bill_id}`)
      setBillStatus(response.data.status)
    } catch (error: any) {
      // Silenciosamente falha se não conseguir carregar
      console.error('Erro ao carregar status da conta:', error)
    }
  }

  const handleAddComment = async () => {
    if (!newComment.trim()) return

    setLoading(true)
    try {
      await apiClient.post(`/calendar/${event.id}/comments`, {
        comment: newComment,
      })
      toast.success('Comentário adicionado!')
      setNewComment('')
      loadComments()
      onRefresh()
    } catch (error: any) {
      toast.error('Erro ao adicionar comentário')
    } finally {
      setLoading(false)
    }
  }

  const handleUpdateParticipation = async (status: string) => {
    setLoading(true)
    try {
      await apiClient.put(`/calendar/${event.id}/participation`, { status })
      toast.success('Status atualizado!')
      setParticipationStatus(status)
      onRefresh()
    } catch (error: any) {
      toast.error('Erro ao atualizar status')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-background rounded-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <span className="text-3xl">{event.icon || EVENT_TYPE_ICONS[event.event_type] || '📅'}</span>
              <div>
                <h2 className="text-2xl font-bold">{event.title}</h2>
                <p className="text-sm text-muted-foreground">
                  {new Date(event.start_date).toLocaleDateString('pt-BR', {
                    day: '2-digit',
                    month: 'long',
                    year: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit',
                  })}
                </p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="p-2 hover:bg-muted rounded-lg transition-colors"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {event.description && (
            <p className="text-muted-foreground mb-4">{event.description}</p>
          )}

          {/* Status da conta (apenas para eventos de conta) */}
          {event.event_type === 'bill' && billStatus && (
            <div className="mb-4 p-3 bg-background/50 rounded-lg">
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium text-muted-foreground">Status:</span>
                <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                  billStatus === 'paid' 
                    ? 'bg-green-500/20 text-green-400' 
                    : billStatus === 'pending'
                    ? 'bg-yellow-500/20 text-yellow-400'
                    : billStatus === 'cancelled'
                    ? 'bg-gray-500/20 text-gray-400'
                    : 'bg-orange-500/20 text-orange-400'
                }`}>
                  {billStatus === 'paid' ? '✅ Paga' : 
                   billStatus === 'pending' ? '⏳ Pendente' : 
                   billStatus === 'cancelled' ? '❌ Cancelada' : 
                   '📋 ' + billStatus}
                </span>
              </div>
            </div>
          )}

          {event.location && (
            <div className="mb-4 flex items-center gap-2 text-muted-foreground">
              <span>📍</span>
              <span>{event.location}</span>
            </div>
          )}

          {/* Participação e Comentários - Apenas para eventos pessoais */}
          {['travel', 'birthday', 'important_event', 'reminder', 'custom'].includes(event.event_type) && (
            <>
              {/* Participação */}
              <div className="mb-6 p-4 bg-background/50 rounded-lg">
                <h3 className="font-semibold mb-3">Sua participação</h3>
                <div className="flex gap-2">
                  <button
                    onClick={() => handleUpdateParticipation('going')}
                    disabled={loading}
                    className={`px-4 py-2 rounded-lg transition-colors ${
                      participationStatus === 'going'
                        ? 'bg-green-600 text-white'
                        : 'bg-background hover:bg-muted'
                    }`}
                  >
                    ✅ Vou
                  </button>
                  <button
                    onClick={() => handleUpdateParticipation('maybe')}
                    disabled={loading}
                    className={`px-4 py-2 rounded-lg transition-colors ${
                      participationStatus === 'maybe'
                        ? 'bg-yellow-600 text-white'
                        : 'bg-background hover:bg-muted'
                    }`}
                  >
                    ⏳ Talvez
                  </button>
                  <button
                    onClick={() => handleUpdateParticipation('not_going')}
                    disabled={loading}
                    className={`px-4 py-2 rounded-lg transition-colors ${
                      participationStatus === 'not_going'
                        ? 'bg-red-600 text-white'
                        : 'bg-background hover:bg-muted'
                    }`}
                  >
                    ❌ Não vou
                  </button>
                </div>
              </div>

              {/* Comentários */}
              <div className="mb-4">
                <h3 className="font-semibold mb-3">Comentários ({comments.length})</h3>
                <div className="space-y-3 mb-4 max-h-60 overflow-y-auto">
                  {comments.map((comment) => (
                    <div key={comment.id} className="p-3 bg-background/50 rounded-lg">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="font-semibold text-sm">{comment.user_name || 'Usuário'}</span>
                        <span className="text-xs text-muted-foreground">
                          {new Date(comment.created_at).toLocaleDateString('pt-BR')}
                        </span>
                      </div>
                      <p className="text-sm">{comment.comment}</p>
                    </div>
                  ))}
                </div>
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={newComment}
                    onChange={(e) => setNewComment(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleAddComment()}
                    placeholder="Adicionar comentário..."
                    className="flex-1 px-4 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  />
                  <button
                    onClick={handleAddComment}
                    disabled={loading || !newComment.trim()}
                    className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50"
                  >
                    Enviar
                  </button>
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  )
}

// Modal de Criar Evento
function CreateEventModal({
  onClose,
  onRefresh,
}: {
  onClose: () => void
  onRefresh: () => void
}) {
  const [loading, setLoading] = useState(false)
  const [formData, setFormData] = useState({
    event_type: 'travel',
    title: '',
    description: '',
    start_date: new Date().toISOString().split('T')[0],
    start_time: '',
    end_date: '',
    end_time: '',
    all_day: true,
    location: '',
    icon: '✈️',
    color: '#8b5cf6',
    is_shared: false,
    is_public: false,
  })

  const eventTypes = [
    { value: 'travel', label: '✈️ Viagem', icon: '✈️' },
    { value: 'birthday', label: '🎂 Aniversário', icon: '🎂' },
    { value: 'important_event', label: '⭐ Evento Importante', icon: '⭐' },
    { value: 'reminder', label: '📝 Lembrete', icon: '📝' },
    { value: 'custom', label: '📅 Personalizado', icon: '📅' },
  ]

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    try {
      const startDateTime = formData.all_day
        ? new Date(`${formData.start_date}T00:00:00`).toISOString()
        : new Date(`${formData.start_date}T${formData.start_time}:00`).toISOString()

      const endDateTime = formData.end_date
        ? formData.all_day
          ? new Date(`${formData.end_date}T23:59:59`).toISOString()
          : new Date(`${formData.end_date}T${formData.end_time}:00`).toISOString()
        : null

      await apiClient.post('/calendar/', {
        event_type: formData.event_type,
        title: formData.title,
        description: formData.description || null,
        start_date: startDateTime,
        end_date: endDateTime,
        all_day: formData.all_day,
        location: formData.location || null,
        icon: formData.icon,
        color: formData.color,
        is_shared: formData.is_shared,
        is_public: formData.is_public,
      })

      toast.success('Evento criado com sucesso!')
      onRefresh()
      onClose()
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Erro ao criar evento')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-background rounded-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold">Novo Evento</h2>
            <button
              onClick={onClose}
              className="p-2 hover:bg-muted rounded-lg transition-colors"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">Tipo de Evento</label>
              <div className="grid grid-cols-2 md:grid-cols-5 gap-2">
                {eventTypes.map((type) => (
                  <button
                    key={type.value}
                    type="button"
                    onClick={() => {
                      setFormData({ ...formData, event_type: type.value, icon: type.icon })
                    }}
                    className={`p-3 rounded-lg border-2 transition-all ${
                      formData.event_type === type.value
                        ? 'border-indigo-500 bg-indigo-500/10'
                        : 'border-border hover:border-indigo-500/50'
                    }`}
                  >
                    <div className="text-2xl mb-1">{type.icon}</div>
                    <div className="text-xs">{type.label.split(' ')[1]}</div>
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Título *</label>
              <input
                type="text"
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                required
                className="w-full px-4 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Descrição</label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                rows={3}
                className="w-full px-4 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-2">Data Início *</label>
                <input
                  type="date"
                  value={formData.start_date}
                  onChange={(e) => setFormData({ ...formData, start_date: e.target.value })}
                  required
                  className="w-full px-4 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
              </div>
              {!formData.all_day && (
                <div>
                  <label className="block text-sm font-medium mb-2">Hora Início</label>
                  <input
                    type="time"
                    value={formData.start_time}
                    onChange={(e) => setFormData({ ...formData, start_time: e.target.value })}
                    className="w-full px-4 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  />
                </div>
              )}
            </div>

            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="all_day"
                checked={formData.all_day}
                onChange={(e) => setFormData({ ...formData, all_day: e.target.checked })}
                className="w-4 h-4"
              />
              <label htmlFor="all_day" className="text-sm">Dia inteiro</label>
            </div>

            {formData.end_date && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Data Fim</label>
                  <input
                    type="date"
                    value={formData.end_date}
                    onChange={(e) => setFormData({ ...formData, end_date: e.target.value })}
                    className="w-full px-4 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  />
                </div>
                {!formData.all_day && (
                  <div>
                    <label className="block text-sm font-medium mb-2">Hora Fim</label>
                    <input
                      type="time"
                      value={formData.end_time}
                      onChange={(e) => setFormData({ ...formData, end_time: e.target.value })}
                      className="w-full px-4 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    />
                  </div>
                )}
              </div>
            )}

            <div>
              <label className="block text-sm font-medium mb-2">Local</label>
              <input
                type="text"
                value={formData.location}
                onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                placeholder="Ex: Paris, França"
                className="w-full px-4 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>

            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="is_shared"
                  checked={formData.is_shared}
                  onChange={(e) => setFormData({ ...formData, is_shared: e.target.checked })}
                  className="w-4 h-4"
                />
                <label htmlFor="is_shared" className="text-sm">Compartilhar no workspace</label>
              </div>
              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="is_public"
                  checked={formData.is_public}
                  onChange={(e) => setFormData({ ...formData, is_public: e.target.checked })}
                  className="w-4 h-4"
                />
                <label htmlFor="is_public" className="text-sm">Público</label>
              </div>
            </div>

            <div className="flex gap-3 pt-4">
              <button
                type="button"
                onClick={onClose}
                className="flex-1 px-4 py-2 bg-background border border-border rounded-lg hover:bg-muted transition-colors"
              >
                Cancelar
              </button>
              <button
                type="submit"
                disabled={loading}
                className="flex-1 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50"
              >
                {loading ? 'Criando...' : 'Criar Evento'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}
