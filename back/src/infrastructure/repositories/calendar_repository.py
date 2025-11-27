from typing import List, Optional
from uuid import UUID
from datetime import datetime
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

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
from src.infrastructure.database.models.workspace import WorkspaceMember


class SQLAlchemyCalendarEventRepository(CalendarEventRepository):
    """Implementação do repositório de eventos com SQLAlchemy"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, event: CalendarEvent) -> CalendarEvent:
        self.session.add(event)
        await self.session.commit()
        await self.session.refresh(event)
        return event

    async def get_by_id(self, event_id: UUID) -> Optional[CalendarEvent]:
        result = await self.session.execute(
            select(CalendarEvent)
            .options(
                joinedload(CalendarEvent.user),
                joinedload(CalendarEvent.creator),
                joinedload(CalendarEvent.workspace),
                joinedload(CalendarEvent.family),
            )
            .where(CalendarEvent.id == event_id)
        )
        return result.scalar_one_or_none()

    async def get_by_user_id(
        self,
        user_id: UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[CalendarEvent]:
        query = select(CalendarEvent).where(CalendarEvent.user_id == user_id)

        if start_date:
            query = query.where(CalendarEvent.start_date >= start_date)
        if end_date:
            query = query.where(CalendarEvent.start_date <= end_date)

        query = query.order_by(CalendarEvent.start_date.asc())

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_workspace_id(
        self,
        workspace_id: UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[CalendarEvent]:
        query = select(CalendarEvent).where(CalendarEvent.workspace_id == workspace_id)

        if start_date:
            query = query.where(CalendarEvent.start_date >= start_date)
        if end_date:
            query = query.where(CalendarEvent.start_date <= end_date)

        query = query.order_by(CalendarEvent.start_date.asc())

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_family_id(
        self,
        family_id: UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[CalendarEvent]:
        query = select(CalendarEvent).where(CalendarEvent.family_id == family_id)

        if start_date:
            query = query.where(CalendarEvent.start_date >= start_date)
        if end_date:
            query = query.where(CalendarEvent.start_date <= end_date)

        query = query.order_by(CalendarEvent.start_date.asc())

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_accessible_by_user(
        self,
        user_id: UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[CalendarEvent]:
        """Obtém todos os eventos acessíveis: próprios + compartilhados + públicos"""
        # Buscar eventos próprios
        own_events = await self.get_by_user_id(user_id, start_date, end_date)

        # Buscar eventos compartilhados em workspaces
        # Primeiro buscar workspaces do usuário
        workspace_members_query = select(WorkspaceMember.workspace_id).where(
            WorkspaceMember.user_id == user_id
        )
        workspace_members_result = await self.session.execute(workspace_members_query)
        workspace_ids = [row[0] for row in workspace_members_result.all()]

        # Buscar eventos desses workspaces
        workspace_events = []
        if workspace_ids:
            workspace_query = select(CalendarEvent).where(
                and_(
                    CalendarEvent.workspace_id.in_(workspace_ids),
                    CalendarEvent.is_shared == True,
                )
            )
            if start_date:
                workspace_query = workspace_query.where(CalendarEvent.start_date >= start_date)
            if end_date:
                workspace_query = workspace_query.where(CalendarEvent.start_date <= end_date)
            workspace_query = workspace_query.order_by(CalendarEvent.start_date.asc())
            workspace_result = await self.session.execute(workspace_query)
            workspace_events = list(workspace_result.scalars().all())

        # Buscar eventos públicos
        public_query = select(CalendarEvent).where(CalendarEvent.is_public == True)
        if start_date:
            public_query = public_query.where(CalendarEvent.start_date >= start_date)
        if end_date:
            public_query = public_query.where(CalendarEvent.start_date <= end_date)
        public_query = public_query.order_by(CalendarEvent.start_date.asc())
        public_result = await self.session.execute(public_query)
        public_events = list(public_result.scalars().all())

        # Combinar e remover duplicatas
        all_events = {e.id: e for e in own_events + workspace_events + public_events}
        return list(all_events.values())

    async def update(self, event: CalendarEvent) -> CalendarEvent:
        await self.session.commit()
        await self.session.refresh(event)
        return event

    async def delete(self, event_id: UUID) -> bool:
        event = await self.get_by_id(event_id)
        if event:
            await self.session.delete(event)
            await self.session.commit()
            return True
        return False


class SQLAlchemyCalendarEventCommentRepository(CalendarEventCommentRepository):
    """Implementação do repositório de comentários com SQLAlchemy"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, comment: CalendarEventComment) -> CalendarEventComment:
        self.session.add(comment)
        await self.session.commit()
        await self.session.refresh(comment)
        return comment

    async def get_by_event_id(self, event_id: UUID) -> List[CalendarEventComment]:
        result = await self.session.execute(
            select(CalendarEventComment)
            .options(joinedload(CalendarEventComment.user))
            .where(CalendarEventComment.event_id == event_id)
            .order_by(CalendarEventComment.created_at.asc())
        )
        return list(result.scalars().all())

    async def delete(self, comment_id: UUID) -> bool:
        result = await self.session.execute(
            select(CalendarEventComment).where(CalendarEventComment.id == comment_id)
        )
        comment = result.scalar_one_or_none()
        if comment:
            await self.session.delete(comment)
            await self.session.commit()
            return True
        return False


class SQLAlchemyCalendarEventParticipantRepository(CalendarEventParticipantRepository):
    """Implementação do repositório de participantes com SQLAlchemy"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, participant: CalendarEventParticipant) -> CalendarEventParticipant:
        self.session.add(participant)
        await self.session.commit()
        await self.session.refresh(participant)
        return participant

    async def get_by_event_id(self, event_id: UUID) -> List[CalendarEventParticipant]:
        result = await self.session.execute(
            select(CalendarEventParticipant)
            .options(joinedload(CalendarEventParticipant.user))
            .where(CalendarEventParticipant.event_id == event_id)
        )
        return list(result.scalars().all())

    async def get_by_event_and_user(
        self, event_id: UUID, user_id: UUID
    ) -> Optional[CalendarEventParticipant]:
        result = await self.session.execute(
            select(CalendarEventParticipant).where(
                and_(
                    CalendarEventParticipant.event_id == event_id,
                    CalendarEventParticipant.user_id == user_id,
                )
            )
        )
        return result.scalar_one_or_none()

    async def update(self, participant: CalendarEventParticipant) -> CalendarEventParticipant:
        await self.session.commit()
        await self.session.refresh(participant)
        return participant

    async def delete(self, participant_id: UUID) -> bool:
        result = await self.session.execute(
            select(CalendarEventParticipant).where(CalendarEventParticipant.id == participant_id)
        )
        participant = result.scalar_one_or_none()
        if participant:
            await self.session.delete(participant)
            await self.session.commit()
            return True
        return False

