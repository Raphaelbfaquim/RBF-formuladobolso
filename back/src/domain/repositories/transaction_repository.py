from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from src.infrastructure.database.models.transaction import Transaction


class TransactionRepository(ABC):
    """Interface do repositório de transações"""

    @abstractmethod
    async def create(self, transaction: Transaction) -> Transaction:
        """Cria uma nova transação"""
        pass

    @abstractmethod
    async def get_by_id(self, transaction_id: UUID) -> Optional[Transaction]:
        """Obtém transação por ID"""
        pass

    @abstractmethod
    async def get_by_user_id(
        self,
        user_id: UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[Transaction]:
        """Obtém transações de um usuário"""
        pass

    @abstractmethod
    async def get_by_account_id(
        self,
        account_id: UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[Transaction]:
        """Obtém transações de uma conta"""
        pass

    @abstractmethod
    async def update(self, transaction: Transaction) -> Transaction:
        """Atualiza uma transação"""
        pass

    @abstractmethod
    async def delete(self, transaction_id: UUID) -> bool:
        """Deleta uma transação"""
        pass

    @abstractmethod
    async def get_sum_by_period(
        self,
        user_id: UUID,
        start_date: datetime,
        end_date: datetime,
        transaction_type: Optional[str] = None,
    ) -> float:
        """Obtém soma de transações em um período"""
        pass

    @abstractmethod
    async def search(
        self,
        user_id: UUID,
        search_text: Optional[str] = None,
        transaction_type: Optional[str] = None,
        category_id: Optional[UUID] = None,
        account_id: Optional[UUID] = None,
        workspace_id: Optional[UUID] = None,
        min_amount: Optional[float] = None,
        max_amount: Optional[float] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
        order_by: Optional[str] = None,
        order_direction: str = "desc",
    ) -> tuple[List[Transaction], int]:
        """Busca avançada de transações com filtros múltiplos"""
        pass

