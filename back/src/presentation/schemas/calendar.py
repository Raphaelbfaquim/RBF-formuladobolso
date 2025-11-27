from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from decimal import Decimal


class CalendarEventBase(BaseModel):
    """Base para eventos do calendário"""
    event_type: str
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    start_date: datetime
    end_date: Optional[datetime] = None
    all_day: bool = True
    workspace_id: Optional[UUID] = None
    family_id: Optional[UUID] = None
    color: Optional[str] = None
    icon: Optional[str] = None
    location: Optional[str] = None
    is_shared: bool = False
    is_public: bool = False


class CalendarEventCreate(CalendarEventBase):
    """Criação de evento"""
    related_transaction_id: Optional[UUID] = None
    related_bill_id: Optional[UUID] = None
    related_goal_id: Optional[UUID] = None


class CalendarEventUpdate(BaseModel):
    """Atualização de evento"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    all_day: Optional[bool] = None
    color: Optional[str] = None
    icon: Optional[str] = None
    location: Optional[str] = None
    is_shared: Optional[bool] = None
    is_public: Optional[bool] = None


class CalendarEventCommentCreate(BaseModel):
    """Criação de comentário"""
    comment: str = Field(..., min_length=1)


class CalendarEventCommentResponse(BaseModel):
    """Resposta de comentário"""
    id: UUID
    event_id: UUID
    user_id: UUID
    user_name: Optional[str] = None
    comment: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CalendarEventParticipantResponse(BaseModel):
    """Resposta de participante"""
    id: UUID
    event_id: UUID
    user_id: UUID
    user_name: Optional[str] = None
    status: str
    responded_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class CalendarEventParticipantUpdate(BaseModel):
    """Atualização de status de participação"""
    status: str  # going, maybe, not_going


class CalendarEventResponse(BaseModel):
    """Resposta de evento"""
    id: UUID
    event_type: str
    title: str
    description: Optional[str] = None
    start_date: datetime
    end_date: Optional[datetime] = None
    all_day: bool
    user_id: UUID
    user_name: Optional[str] = None
    workspace_id: Optional[UUID] = None
    workspace_name: Optional[str] = None
    family_id: Optional[UUID] = None
    related_transaction_id: Optional[UUID] = None
    related_bill_id: Optional[UUID] = None
    related_goal_id: Optional[UUID] = None
    color: Optional[str] = None
    icon: Optional[str] = None
    location: Optional[str] = None
    is_shared: bool
    is_public: bool
    created_at: datetime
    updated_at: datetime
    created_by: UUID
    created_by_name: Optional[str] = None
    comments_count: int = 0
    participants_count: int = 0
    user_participation_status: Optional[str] = None

    class Config:
        from_attributes = True


class CalendarEventsByDateResponse(BaseModel):
    """Eventos agrupados por data"""
    date: str  # YYYY-MM-DD
    events: List[CalendarEventResponse]


class CalendarMonthResponse(BaseModel):
    """Resposta do mês do calendário"""
    month: int
    year: int
    events_by_date: List[CalendarEventsByDateResponse]
    total_events: int


