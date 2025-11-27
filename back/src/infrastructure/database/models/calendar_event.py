from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Enum as SQLEnum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
import pytz
import enum

from src.infrastructure.database.base import Base


class CalendarEventType(enum.Enum):
    """Tipos de eventos do calendário"""
    # Eventos financeiros (automáticos)
    TRANSACTION = "transaction"  # Transação financeira
    BILL = "bill"  # Conta a pagar/receber
    GOAL = "goal"  # Meta financeira
    GOAL_CONTRIBUTION = "goal_contribution"  # Contribuição para meta
    
    # Eventos pessoais (cadastrados)
    TRAVEL = "travel"  # Viagem
    BIRTHDAY = "birthday"  # Aniversário
    IMPORTANT_EVENT = "important_event"  # Evento importante
    REMINDER = "reminder"  # Lembrete
    CUSTOM = "custom"  # Evento personalizado
    
    def __str__(self):
        return self.value


class EventParticipationStatus(str, enum.Enum):
    """Status de participação em evento"""
    GOING = "going"  # Vou
    MAYBE = "maybe"  # Talvez
    NOT_GOING = "not_going"  # Não vou
    NOT_RESPONDED = "not_responded"  # Não respondeu


class CalendarEvent(Base):
    """Evento do calendário (financeiro ou pessoal)"""
    __tablename__ = "calendar_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_type = Column(String(50), nullable=False)  # Usar String em vez de Enum para evitar problemas
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=True)  # Para eventos com duração
    all_day = Column(Boolean, default=True, nullable=False)  # Evento de dia inteiro
    
    # Relacionamentos
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)  # Criador
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id"), nullable=True)  # Workspace compartilhado
    family_id = Column(UUID(as_uuid=True), ForeignKey("families.id"), nullable=True)  # Família compartilhada
    
    # Dados específicos por tipo (relacionamentos opcionais)
    related_transaction_id = Column(UUID(as_uuid=True), ForeignKey("transactions.id"), nullable=True)
    related_bill_id = Column(UUID(as_uuid=True), ForeignKey("bills.id"), nullable=True)
    related_goal_id = Column(UUID(as_uuid=True), ForeignKey("goals.id"), nullable=True)
    
    # Personalização visual
    color = Column(String(7), nullable=True)  # Cor em hex (ex: #FF5733)
    icon = Column(String(50), nullable=True)  # Emoji ou ícone
    location = Column(String(255), nullable=True)  # Local (para viagens, eventos)
    
    # Compartilhamento
    is_shared = Column(Boolean, default=False, nullable=False)  # Se é compartilhado no workspace/família
    is_public = Column(Boolean, default=False, nullable=False)  # Se todos podem ver (mesmo sem ser membro)
    
    # Metadados
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(pytz.UTC), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(pytz.UTC), onupdate=lambda: datetime.now(pytz.UTC), nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)  # Quem criou

    # Relacionamentos
    user = relationship("User", foreign_keys=[user_id], backref="calendar_events")
    creator = relationship("User", foreign_keys=[created_by])
    workspace = relationship("Workspace", backref="calendar_events")
    family = relationship("Family", backref="calendar_events")
    transaction = relationship("Transaction", backref="calendar_events")
    bill = relationship("Bill", backref="calendar_events")
    goal = relationship("Goal", backref="calendar_events")
    comments = relationship("CalendarEventComment", back_populates="event", cascade="all, delete-orphan")
    participants = relationship("CalendarEventParticipant", back_populates="event", cascade="all, delete-orphan")


class CalendarEventComment(Base):
    """Comentário em um evento do calendário"""
    __tablename__ = "calendar_event_comments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_id = Column(UUID(as_uuid=True), ForeignKey("calendar_events.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    comment = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(pytz.UTC), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(pytz.UTC), onupdate=lambda: datetime.now(pytz.UTC), nullable=False)

    # Relacionamentos
    event = relationship("CalendarEvent", back_populates="comments")
    user = relationship("User", backref="calendar_event_comments")


class CalendarEventParticipant(Base):
    """Participante de um evento (confirmação de presença)"""
    __tablename__ = "calendar_event_participants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_id = Column(UUID(as_uuid=True), ForeignKey("calendar_events.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    status = Column(SQLEnum(EventParticipationStatus), default=EventParticipationStatus.NOT_RESPONDED, nullable=False)
    responded_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(pytz.UTC), nullable=False)

    # Relacionamentos
    event = relationship("CalendarEvent", back_populates="participants")
    user = relationship("User", backref="calendar_event_participations")

