from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from src.infrastructure.database.models.workspace import Workspace, WorkspaceMember


class WorkspaceRepository(ABC):
    """Interface do repositório de workspaces"""

    @abstractmethod
    async def create(self, workspace: Workspace) -> Workspace:
        pass

    @abstractmethod
    async def get_by_id(self, workspace_id: UUID) -> Optional[Workspace]:
        pass

    @abstractmethod
    async def get_by_owner_id(self, owner_id: UUID) -> List[Workspace]:
        pass

    @abstractmethod
    async def get_accessible_by_user(self, user_id: UUID) -> List[Workspace]:
        """Obtém todos os workspaces que o usuário pode acessar (próprios + compartilhados)"""
        pass

    @abstractmethod
    async def update(self, workspace: Workspace) -> Workspace:
        pass

    @abstractmethod
    async def delete(self, workspace_id: UUID) -> bool:
        pass

    @abstractmethod
    async def user_has_access(self, user_id: UUID, workspace_id: UUID) -> bool:
        """Verifica se usuário tem acesso ao workspace"""
        pass


class WorkspaceMemberRepository(ABC):
    """Interface do repositório de membros do workspace"""

    @abstractmethod
    async def create(self, member: WorkspaceMember) -> WorkspaceMember:
        pass

    @abstractmethod
    async def get_by_workspace_id(self, workspace_id: UUID) -> List[WorkspaceMember]:
        pass

    @abstractmethod
    async def get_member(self, user_id: UUID, workspace_id: UUID) -> Optional[WorkspaceMember]:
        pass

    @abstractmethod
    async def delete(self, member_id: UUID) -> bool:
        pass

