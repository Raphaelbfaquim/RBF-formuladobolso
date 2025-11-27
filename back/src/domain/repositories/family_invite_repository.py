from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID
from src.infrastructure.database.models.family_invite import FamilyInvite


class FamilyInviteRepository(ABC):
    """Interface do repositório de convites de família"""

    @abstractmethod
    async def create(self, invite: FamilyInvite) -> FamilyInvite:
        pass

    @abstractmethod
    async def get_by_id(self, invite_id: UUID) -> Optional[FamilyInvite]:
        pass

    @abstractmethod
    async def get_by_token(self, token: str) -> Optional[FamilyInvite]:
        pass

    @abstractmethod
    async def get_by_email_and_family(self, email: str, family_id: UUID) -> Optional[FamilyInvite]:
        pass

    @abstractmethod
    async def update(self, invite: FamilyInvite) -> FamilyInvite:
        pass

    @abstractmethod
    async def delete(self, invite_id: UUID) -> bool:
        pass

