from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from src.infrastructure.database.models.investment import InvestmentAccount, InvestmentTransaction


class InvestmentAccountRepository(ABC):
    """Interface para repositório de contas de investimento"""

    @abstractmethod
    async def create(self, account: InvestmentAccount) -> InvestmentAccount:
        pass

    @abstractmethod
    async def get_by_id(self, account_id: UUID) -> Optional[InvestmentAccount]:
        pass

    @abstractmethod
    async def get_by_user_id(self, user_id: UUID) -> List[InvestmentAccount]:
        pass

    @abstractmethod
    async def update(self, account: InvestmentAccount) -> InvestmentAccount:
        pass

    @abstractmethod
    async def delete(self, account_id: UUID) -> bool:
        pass


class InvestmentTransactionRepository(ABC):
    """Interface para repositório de transações de investimento"""

    @abstractmethod
    async def create(self, transaction: InvestmentTransaction) -> InvestmentTransaction:
        pass

    @abstractmethod
    async def get_by_id(self, transaction_id: UUID) -> Optional[InvestmentTransaction]:
        pass

    @abstractmethod
    async def get_by_account_id(
        self, account_id: UUID, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None
    ) -> List[InvestmentTransaction]:
        pass

    @abstractmethod
    async def get_by_user_id(
        self, user_id: UUID, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None
    ) -> List[InvestmentTransaction]:
        pass

    @abstractmethod
    async def update(self, transaction: InvestmentTransaction) -> InvestmentTransaction:
        pass

    @abstractmethod
    async def delete(self, transaction_id: UUID) -> bool:
        pass


