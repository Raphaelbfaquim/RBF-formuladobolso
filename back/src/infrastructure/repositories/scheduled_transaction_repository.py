from typing import List, Optional
from uuid import UUID
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from src.domain.repositories.scheduled_transaction_repository import ScheduledTransactionRepository
from src.infrastructure.database.models.scheduled_transaction import (
    ScheduledTransaction,
    ScheduledTransactionStatus,
)


class SQLAlchemyScheduledTransactionRepository(ScheduledTransactionRepository):
    """Implementação do repositório de transações agendadas"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, scheduled: ScheduledTransaction) -> ScheduledTransaction:
        self.session.add(scheduled)
        await self.session.commit()
        await self.session.refresh(scheduled)
        return scheduled

    async def get_by_id(self, scheduled_id: UUID) -> Optional[ScheduledTransaction]:
        result = await self.session.execute(
            select(ScheduledTransaction).where(ScheduledTransaction.id == scheduled_id)
        )
        return result.scalar_one_or_none()

    async def get_by_user_id(self, user_id: UUID) -> List[ScheduledTransaction]:
        result = await self.session.execute(
            select(ScheduledTransaction).where(
                ScheduledTransaction.user_id == user_id,
                ScheduledTransaction.is_active == True,
            )
        )
        return list(result.scalars().all())

    async def get_pending_executions(self, before_date: datetime) -> List[ScheduledTransaction]:
        """Obtém transações agendadas que precisam ser executadas"""
        result = await self.session.execute(
            select(ScheduledTransaction).where(
                and_(
                    ScheduledTransaction.status == ScheduledTransactionStatus.ACTIVE,
                    ScheduledTransaction.is_active == True,
                    ScheduledTransaction.next_execution_date <= before_date,
                    ScheduledTransaction.auto_execute == True,
                )
            )
        )
        return list(result.scalars().all())

    async def update(self, scheduled: ScheduledTransaction) -> ScheduledTransaction:
        await self.session.commit()
        await self.session.refresh(scheduled)
        return scheduled

    async def delete(self, scheduled_id: UUID) -> bool:
        scheduled = await self.get_by_id(scheduled_id)
        if scheduled:
            scheduled.is_active = False
            scheduled.status = ScheduledTransactionStatus.CANCELLED
            await self.session.commit()
            return True
        return False

