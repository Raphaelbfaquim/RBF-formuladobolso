from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from src.infrastructure.database.models.user import Family, FamilyMember


class FamilyRepository(ABC):
    """Interface do repositório de famílias"""

    @abstractmethod
    async def create(self, family: Family) -> Family:
        pass

    @abstractmethod
    async def get_by_id(self, family_id: UUID) -> Optional[Family]:
        pass

    @abstractmethod
    async def get_by_user_id(self, user_id: UUID) -> List[Family]:
        pass

    @abstractmethod
    async def update(self, family: Family) -> Family:
        pass

    @abstractmethod
    async def delete(self, family_id: UUID) -> bool:
        pass


class FamilyMemberRepository(ABC):
    """Interface do repositório de membros da família"""

    @abstractmethod
    async def create(self, member: FamilyMember) -> FamilyMember:
        pass

    @abstractmethod
    async def get_by_id(self, member_id: UUID) -> Optional[FamilyMember]:
        pass

    @abstractmethod
    async def get_by_family_id(self, family_id: UUID) -> List[FamilyMember]:
        pass

    @abstractmethod
    async def get_by_user_id(self, user_id: UUID) -> List[FamilyMember]:
        pass

    @abstractmethod
    async def get_member_in_family(self, user_id: UUID, family_id: UUID) -> Optional[FamilyMember]:
        pass

    @abstractmethod
    async def update(self, member: FamilyMember) -> FamilyMember:
        pass

    @abstractmethod
    async def delete(self, member_id: UUID) -> bool:
        pass


class FamilyChatRepository(ABC):
    """Interface do repositório de mensagens do chat familiar"""

    @abstractmethod
    async def create(self, message) -> any:
        pass

    @abstractmethod
    async def get_by_family_id(self, family_id: UUID, limit: int = 50) -> List:
        pass

