from typing import List, Optional
from uuid import UUID
from datetime import datetime
from decimal import Decimal

from src.domain.repositories.calendar_repository import (
    CalendarEventRepository,
    CalendarEventCommentRepository,
    CalendarEventParticipantRepository,
)
from src.infrastructure.database.models.calendar_event import (
    CalendarEvent,
    CalendarEventComment,
    CalendarEventParticipant,
    CalendarEventType,
    EventParticipationStatus,
)
from src.shared.exceptions import NotFoundException, ValidationException, UnauthorizedException

UnauthorizedError = UnauthorizedException


class CalendarUseCases:
    """Casos de uso para gerenciamento do calendário"""

    def __init__(
        self,
        event_repository: CalendarEventRepository,
        comment_repository: CalendarEventCommentRepository,
        participant_repository: CalendarEventParticipantRepository,
    ):
        self.event_repository = event_repository
        self.comment_repository = comment_repository
        self.participant_repository = participant_repository

    async def create_event(
        self,
        event_type: str,
        title: str,
        start_date: datetime,
        user_id: UUID,
        created_by: UUID,
        description: Optional[str] = None,
        end_date: Optional[datetime] = None,
        all_day: bool = True,
        workspace_id: Optional[UUID] = None,
        family_id: Optional[UUID] = None,
        related_transaction_id: Optional[UUID] = None,
        related_bill_id: Optional[UUID] = None,
        related_goal_id: Optional[UUID] = None,
        color: Optional[str] = None,
        icon: Optional[str] = None,
        location: Optional[str] = None,
        is_shared: bool = False,
        is_public: bool = False,
    ) -> CalendarEvent:
        """Cria um novo evento"""
        try:
            CalendarEventType(event_type)
        except ValueError:
            raise ValidationException(f"Tipo de evento inválido: {event_type}")

        event = CalendarEvent(
            event_type=event_type if isinstance(event_type, str) else CalendarEventType(event_type).value,
            title=title,
            description=description,
            start_date=start_date,
            end_date=end_date,
            all_day=all_day,
            user_id=user_id,
            created_by=created_by,
            workspace_id=workspace_id,
            family_id=family_id,
            related_transaction_id=related_transaction_id,
            related_bill_id=related_bill_id,
            related_goal_id=related_goal_id,
            color=color,
            icon=icon,
            location=location,
            is_shared=is_shared,
            is_public=is_public,
        )

        return await self.event_repository.create(event)

    async def get_event(self, event_id: UUID, user_id: UUID) -> CalendarEvent:
        """Obtém um evento por ID"""
        event = await self.event_repository.get_by_id(event_id)
        if not event:
            raise NotFoundException("Evento", str(event_id))

        # Verificar acesso
        if event.user_id != user_id and not event.is_public and not event.is_shared:
            raise UnauthorizedError("Você não tem acesso a este evento")

        return event

    async def get_user_events(
        self,
        user_id: UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[CalendarEvent]:
        """Obtém eventos acessíveis pelo usuário"""
        return await self.event_repository.get_accessible_by_user(user_id, start_date, end_date)

    async def update_event(
        self,
        event_id: UUID,
        user_id: UUID,
        title: Optional[str] = None,
        description: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        all_day: Optional[bool] = None,
        color: Optional[str] = None,
        icon: Optional[str] = None,
        location: Optional[str] = None,
        is_shared: Optional[bool] = None,
        is_public: Optional[bool] = None,
    ) -> CalendarEvent:
        """Atualiza um evento"""
        event = await self.get_event(event_id, user_id)

        # Verificar se é o dono ou criador
        if event.user_id != user_id and event.created_by != user_id:
            raise UnauthorizedError("Apenas o dono pode editar o evento")

        if title:
            event.title = title
        if description is not None:
            event.description = description
        if start_date:
            event.start_date = start_date
        if end_date is not None:
            event.end_date = end_date
        if all_day is not None:
            event.all_day = all_day
        if color is not None:
            event.color = color
        if icon is not None:
            event.icon = icon
        if location is not None:
            event.location = location
        if is_shared is not None:
            event.is_shared = is_shared
        if is_public is not None:
            event.is_public = is_public

        return await self.event_repository.update(event)

    async def delete_event(self, event_id: UUID, user_id: UUID) -> bool:
        """Deleta um evento"""
        event = await self.get_event(event_id, user_id)

        # Verificar se é o dono ou criador
        if event.user_id != user_id and event.created_by != user_id:
            raise UnauthorizedError("Apenas o dono pode deletar o evento")

        return await self.event_repository.delete(event_id)

    async def add_comment(
        self, event_id: UUID, user_id: UUID, comment: str
    ) -> CalendarEventComment:
        """Adiciona um comentário a um evento"""
        event = await self.get_event(event_id, user_id)

        comment_obj = CalendarEventComment(
            event_id=event_id, user_id=user_id, comment=comment
        )

        return await self.comment_repository.create(comment_obj)

    async def get_event_comments(self, event_id: UUID, user_id: UUID) -> List[CalendarEventComment]:
        """Obtém comentários de um evento"""
        event = await self.get_event(event_id, user_id)
        return await self.comment_repository.get_by_event_id(event_id)

    async def update_participation(
        self, event_id: UUID, user_id: UUID, status: str
    ) -> CalendarEventParticipant:
        """Atualiza status de participação em um evento"""
        try:
            EventParticipationStatus(status)
        except ValueError:
            raise ValidationException(f"Status de participação inválido: {status}")

        event = await self.get_event(event_id, user_id)

        # Buscar participação existente
        participant = await self.participant_repository.get_by_event_and_user(event_id, user_id)

        from datetime import datetime
        import pytz

        if participant:
            participant.status = EventParticipationStatus(status)
            participant.responded_at = datetime.now(pytz.UTC)
            return await self.participant_repository.update(participant)
        else:
            participant = CalendarEventParticipant(
                event_id=event_id,
                user_id=user_id,
                status=EventParticipationStatus(status),
                responded_at=datetime.now(pytz.UTC),
            )
            return await self.participant_repository.create(participant)

    async def get_event_participants(
        self, event_id: UUID, user_id: UUID
    ) -> List[CalendarEventParticipant]:
        """Obtém participantes de um evento"""
        event = await self.get_event(event_id, user_id)
        return await self.participant_repository.get_by_event_id(event_id)

