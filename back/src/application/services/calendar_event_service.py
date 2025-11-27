"""Serviço para criar eventos do calendário automaticamente"""
from typing import Optional
from uuid import UUID
from datetime import datetime
from decimal import Decimal

from src.domain.repositories.calendar_repository import CalendarEventRepository
from src.infrastructure.database.models.calendar_event import CalendarEvent, CalendarEventType


class CalendarEventService:
    """Serviço para criar eventos do calendário automaticamente"""

    def __init__(self, calendar_event_repository: CalendarEventRepository):
        self.calendar_event_repository = calendar_event_repository

    async def create_transaction_event(
        self,
        transaction_id: UUID,
        title: str,
        transaction_date: datetime,
        user_id: UUID,
        workspace_id: Optional[UUID] = None,
        amount: Optional[Decimal] = None,
        transaction_type: Optional[str] = None,
    ) -> Optional[CalendarEvent]:
        """Cria evento do calendário para uma transação"""
        try:
            # Determinar cor e ícone baseado no tipo
            if transaction_type == "income":
                color = "#10b981"  # Verde
                icon = "💰"
            else:
                color = "#ef4444"  # Vermelho
                icon = "💸"

            event = CalendarEvent(
                event_type=CalendarEventType.TRANSACTION.value,  # Usar o valor "transaction" como string
                title=title,
                description=f"Transação: {title}" + (f" - R$ {amount:.2f}" if amount else ""),
                start_date=transaction_date,
                end_date=None,
                all_day=True,
                user_id=user_id,
                created_by=user_id,
                workspace_id=workspace_id,
                related_transaction_id=transaction_id,
                color=color,
                icon=icon,
                is_shared=workspace_id is not None,
                is_public=False,
            )

            return await self.calendar_event_repository.create(event)
        except Exception as e:
            print(f"[DEBUG] Erro ao criar evento de transação: {e}")
            return None

    async def create_bill_event(
        self,
        bill_id: UUID,
        name: str,
        due_date: datetime,
        user_id: UUID,
        workspace_id: Optional[UUID] = None,
        amount: Optional[Decimal] = None,
        bill_type: Optional[str] = None,
    ) -> Optional[CalendarEvent]:
        """Cria evento do calendário para uma conta a pagar/receber"""
        try:
            # Determinar cor e ícone
            if bill_type == "income":
                color = "#10b981"  # Verde
                icon = "📥"
            else:
                color = "#f97316"  # Laranja
                icon = "📋"

            event = CalendarEvent(
                event_type=CalendarEventType.BILL.value,  # Usar o valor "bill" como string
                title=name,
                description=f"Conta a {'receber' if bill_type == 'income' else 'pagar'}: {name}" + (f" - R$ {amount:.2f}" if amount else ""),
                start_date=due_date,
                end_date=None,
                all_day=True,
                user_id=user_id,
                created_by=user_id,
                workspace_id=workspace_id,
                related_bill_id=bill_id,
                color=color,
                icon=icon,
                is_shared=workspace_id is not None,
                is_public=False,
            )

            return await self.calendar_event_repository.create(event)
        except Exception as e:
            print(f"[DEBUG] Erro ao criar evento de conta: {e}")
            return None

    async def create_goal_event(
        self,
        goal_id: UUID,
        name: str,
        target_date: datetime,
        user_id: UUID,
        workspace_id: Optional[UUID] = None,
    ) -> Optional[CalendarEvent]:
        """Cria evento do calendário para uma meta"""
        try:
            event = CalendarEvent(
                event_type=CalendarEventType.GOAL.value,  # Usar o valor "goal" como string
                title=f"Meta: {name}",
                description=f"Data objetivo da meta: {name}",
                start_date=target_date,
                end_date=None,
                all_day=True,
                user_id=user_id,
                created_by=user_id,
                workspace_id=workspace_id,
                related_goal_id=goal_id,
                color="#3b82f6",  # Azul
                icon="🎯",
                is_shared=workspace_id is not None,
                is_public=False,
            )

            return await self.calendar_event_repository.create(event)
        except Exception as e:
            print(f"[DEBUG] Erro ao criar evento de meta: {e}")
            return None

    async def create_goal_contribution_event(
        self,
        goal_id: UUID,
        goal_name: str,
        contribution_date: datetime,
        user_id: UUID,
        amount: Decimal,
        workspace_id: Optional[UUID] = None,
    ) -> Optional[CalendarEvent]:
        """Cria evento do calendário para uma contribuição de meta"""
        try:
            event = CalendarEvent(
                event_type=CalendarEventType.GOAL_CONTRIBUTION.value,  # Usar o valor "goal_contribution" como string
                title=f"Contribuição: {goal_name}",
                description=f"Contribuição de R$ {amount:.2f} para a meta: {goal_name}",
                start_date=contribution_date,
                end_date=None,
                all_day=True,
                user_id=user_id,
                created_by=user_id,
                workspace_id=workspace_id,
                related_goal_id=goal_id,
                color="#8b5cf6",  # Roxo
                icon="💵",
                is_shared=workspace_id is not None,
                is_public=False,
            )

            return await self.calendar_event_repository.create(event)
        except Exception as e:
            print(f"[DEBUG] Erro ao criar evento de contribuição: {e}")
            return None

