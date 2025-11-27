from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from src.infrastructure.database.models.bill import Bill


class BillRepository(ABC):
    """Interface do repositório de contas"""

    @abstractmethod
    async def create(self, bill: Bill) -> Bill:
        """Cria uma nova conta"""
        pass

    @abstractmethod
    async def get_by_id(self, bill_id: UUID) -> Optional[Bill]:
        """Obtém conta por ID"""
        pass

    @abstractmethod
    async def get_by_user_id(
        self,
        user_id: UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        bill_type: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[Bill]:
        """Obtém contas de um usuário"""
        pass

    @abstractmethod
    async def get_upcoming(self, user_id: UUID, days: int = 7) -> List[Bill]:
        """Obtém contas próximas do vencimento"""
        pass

    @abstractmethod
    async def get_overdue(self, user_id: UUID) -> List[Bill]:
        """Obtém contas vencidas"""
        pass

    @abstractmethod
    async def update(self, bill: Bill) -> Bill:
        """Atualiza uma conta"""
        pass

    @abstractmethod
    async def delete(self, bill_id: UUID) -> bool:
        """Deleta uma conta"""
        pass

    @abstractmethod
    async def get_by_transaction_id(self, transaction_id: UUID) -> Optional[Bill]:
        """Obtém conta por ID da transação relacionada"""
        pass

