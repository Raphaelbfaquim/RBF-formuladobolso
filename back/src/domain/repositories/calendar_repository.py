from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from src.infrastructure.database.models.calendar_event import (
    CalendarEvent,
    CalendarEventComment,
    CalendarEventParticipant,
)


class CalendarEventRepository(ABC):
    """Interface para repositório de eventos do calendário"""

    @abstractmethod
    async def create(self, event: CalendarEvent) -> CalendarEvent:
        """Cria um novo evento"""
        pass

    @abstractmethod
    async def get_by_id(self, event_id: UUID) -> Optional[CalendarEvent]:
        """Obtém um evento por ID"""
        pass

    @abstractmethod
    async def get_by_user_id(
        self,
        user_id: UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[CalendarEvent]:
        """Obtém eventos de um usuário"""
        pass

    @abstractmethod
    async def get_by_workspace_id(
        self,
        workspace_id: UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[CalendarEvent]:
        """Obtém eventos de um workspace"""
        pass

    @abstractmethod
    async def get_by_family_id(
        self,
        family_id: UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[CalendarEvent]:
        """Obtém eventos de uma família"""
        pass

    @abstractmethod
    async def get_accessible_by_user(
        self,
        user_id: UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[CalendarEvent]:
        """Obtém todos os eventos acessíveis pelo usuário (próprios + compartilhados)"""
        pass

    @abstractmethod
    async def update(self, event: CalendarEvent) -> CalendarEvent:
        """Atualiza um evento"""
        pass

    @abstractmethod
    async def delete(self, event_id: UUID) -> bool:
        """Deleta um evento"""
        pass


class CalendarEventCommentRepository(ABC):
    """Interface para repositório de comentários"""

    @abstractmethod
    async def create(self, comment: CalendarEventComment) -> CalendarEventComment:
        """Cria um novo comentário"""
        pass

    @abstractmethod
    async def get_by_event_id(self, event_id: UUID) -> List[CalendarEventComment]:
        """Obtém comentários de um evento"""
        pass

    @abstractmethod
    async def delete(self, comment_id: UUID) -> bool:
        """Deleta um comentário"""
        pass


class CalendarEventParticipantRepository(ABC):
    """Interface para repositório de participantes"""

    @abstractmethod
    async def create(self, participant: CalendarEventParticipant) -> CalendarEventParticipant:
        """Cria um novo participante"""
        pass

    @abstractmethod
    async def get_by_event_id(self, event_id: UUID) -> List[CalendarEventParticipant]:
        """Obtém participantes de um evento"""
        pass

    @abstractmethod
    async def get_by_event_and_user(
        self, event_id: UUID, user_id: UUID
    ) -> Optional[CalendarEventParticipant]:
        """Obtém participação de um usuário em um evento"""
        pass

    @abstractmethod
    async def update(self, participant: CalendarEventParticipant) -> CalendarEventParticipant:
        """Atualiza um participante"""
        pass

    @abstractmethod
    async def delete(self, participant_id: UUID) -> bool:
        """Deleta um participante"""
        pass


