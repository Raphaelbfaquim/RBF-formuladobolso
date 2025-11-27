from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from src.infrastructure.database.models.transfer import Transfer


class TransferRepository(ABC):
    """Interface do repositório de transferências"""

    @abstractmethod
    async def create(self, transfer: Transfer) -> Transfer:
        pass

    @abstractmethod
    async def get_by_id(self, transfer_id: UUID) -> Optional[Transfer]:
        pass

    @abstractmethod
    async def get_by_user_id(
        self,
        user_id: UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[Transfer]:
        pass

    @abstractmethod
    async def update(self, transfer: Transfer) -> Transfer:
        pass

    @abstractmethod
    async def delete(self, transfer_id: UUID) -> bool:
        pass

