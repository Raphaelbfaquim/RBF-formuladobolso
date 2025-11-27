from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from src.infrastructure.database.models.account import Account


class AccountRepository(ABC):
    """Interface do repositório de contas"""

    @abstractmethod
    async def create(self, account: Account) -> Account:
        """Cria uma nova conta"""
        pass

    @abstractmethod
    async def get_by_id(self, account_id: UUID) -> Optional[Account]:
        """Obtém conta por ID"""
        pass

    @abstractmethod
    async def get_by_user_id(self, user_id: UUID) -> List[Account]:
        """Obtém todas as contas de um usuário"""
        pass

    @abstractmethod
    async def get_by_family_id(self, family_id: UUID) -> List[Account]:
        """Obtém todas as contas de uma família"""
        pass

    @abstractmethod
    async def update(self, account: Account) -> Account:
        """Atualiza uma conta"""
        pass

    @abstractmethod
    async def delete(self, account_id: UUID) -> bool:
        """Deleta uma conta"""
        pass

