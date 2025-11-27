from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID
from datetime import datetime
from src.infrastructure.database.models.user import User


class UserRepository(ABC):
    """Interface do repositório de usuários"""

    @abstractmethod
    async def create(self, user: User) -> User:
        """Cria um novo usuário"""
        pass

    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Obtém usuário por ID"""
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        """Obtém usuário por email"""
        pass

    @abstractmethod
    async def get_by_username(self, username: str) -> Optional[User]:
        """Obtém usuário por username"""
        pass

    @abstractmethod
    async def update(self, user: User) -> User:
        """Atualiza um usuário"""
        pass

    @abstractmethod
    async def delete(self, user_id: UUID) -> bool:
        """Deleta um usuário"""
        pass

    @abstractmethod
    async def get_by_reset_token(self, reset_token: str) -> Optional[User]:
        """Obtém usuário por token de reset"""
        pass

    @abstractmethod
    async def update_reset_token(self, user_id: UUID, reset_token: Optional[str], reset_token_expires: Optional[datetime]) -> bool:
        """Atualiza token de reset do usuário"""
        pass

    @abstractmethod
    async def update_password(self, user_id: UUID, hashed_password: str) -> bool:
        """Atualiza senha do usuário"""
        pass

