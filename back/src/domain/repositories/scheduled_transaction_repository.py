from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from src.infrastructure.database.models.scheduled_transaction import ScheduledTransaction


class ScheduledTransactionRepository(ABC):
    """Interface do repositório de transações agendadas"""

    @abstractmethod
    async def create(self, scheduled: ScheduledTransaction) -> ScheduledTransaction:
        pass

    @abstractmethod
    async def get_by_id(self, scheduled_id: UUID) -> Optional[ScheduledTransaction]:
        pass

    @abstractmethod
    async def get_by_user_id(self, user_id: UUID) -> List[ScheduledTransaction]:
        pass

    @abstractmethod
    async def get_pending_executions(self, before_date: datetime) -> List[ScheduledTransaction]:
        """Obtém transações agendadas que precisam ser executadas"""
        pass

    @abstractmethod
    async def update(self, scheduled: ScheduledTransaction) -> ScheduledTransaction:
        pass

    @abstractmethod
    async def delete(self, scheduled_id: UUID) -> bool:
        pass

