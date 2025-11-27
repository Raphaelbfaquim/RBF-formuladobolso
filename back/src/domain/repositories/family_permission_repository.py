from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from src.infrastructure.database.models.family_permission import FamilyMemberPermission, ModulePermission


class FamilyPermissionRepository(ABC):
    """Interface do repositório de permissões de membros da família"""

    @abstractmethod
    async def create(self, permission: FamilyMemberPermission) -> FamilyMemberPermission:
        pass

    @abstractmethod
    async def get_by_id(self, permission_id: UUID) -> Optional[FamilyMemberPermission]:
        pass

    @abstractmethod
    async def get_by_family_member_id(self, family_member_id: UUID) -> List[FamilyMemberPermission]:
        pass

    @abstractmethod
    async def get_by_family_member_and_module(
        self, family_member_id: UUID, module: ModulePermission
    ) -> Optional[FamilyMemberPermission]:
        pass

    @abstractmethod
    async def update(self, permission: FamilyMemberPermission) -> FamilyMemberPermission:
        pass

    @abstractmethod
    async def delete(self, permission_id: UUID) -> bool:
        pass

    @abstractmethod
    async def delete_by_family_member_id(self, family_member_id: UUID) -> bool:
        pass

