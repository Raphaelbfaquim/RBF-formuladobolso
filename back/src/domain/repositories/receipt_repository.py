from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from src.infrastructure.database.models.receipt import Receipt


class ReceiptRepository(ABC):
    """Interface do repositório de notas fiscais"""

    @abstractmethod
    async def create(self, receipt: Receipt) -> Receipt:
        """Cria uma nova nota fiscal"""
        pass

    @abstractmethod
    async def get_by_id(self, receipt_id: UUID) -> Optional[Receipt]:
        """Obtém nota fiscal por ID"""
        pass

    @abstractmethod
    async def get_by_access_key(self, access_key: str) -> Optional[Receipt]:
        """Obtém nota fiscal por chave de acesso"""
        pass

    @abstractmethod
    async def get_by_user_id(self, user_id: UUID) -> List[Receipt]:
        """Obtém notas fiscais de um usuário"""
        pass

    @abstractmethod
    async def update(self, receipt: Receipt) -> Receipt:
        """Atualiza uma nota fiscal"""
        pass

    @abstractmethod
    async def delete(self, receipt_id: UUID) -> bool:
        """Deleta uma nota fiscal"""
        pass

