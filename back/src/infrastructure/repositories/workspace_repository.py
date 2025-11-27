from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from src.domain.repositories.workspace_repository import (
    WorkspaceRepository,
    WorkspaceMemberRepository,
)
from src.infrastructure.database.models.workspace import Workspace, WorkspaceMember


class SQLAlchemyWorkspaceRepository(WorkspaceRepository):
    """Implementação do repositório de workspaces"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, workspace: Workspace) -> Workspace:
        self.session.add(workspace)
        await self.session.commit()
        await self.session.refresh(workspace)
        return workspace

    async def get_by_id(self, workspace_id: UUID) -> Optional[Workspace]:
        result = await self.session.execute(select(Workspace).where(Workspace.id == workspace_id))
        return result.scalar_one_or_none()

    async def get_by_owner_id(self, owner_id: UUID) -> List[Workspace]:
        result = await self.session.execute(
            select(Workspace).where(Workspace.owner_id == owner_id, Workspace.is_active == True)
        )
        return list(result.scalars().all())

    async def get_accessible_by_user(self, user_id: UUID) -> List[Workspace]:
        """Obtém todos os workspaces que o usuário pode acessar"""
        # Workspaces próprios
        owned = await self.get_by_owner_id(user_id)
        
        # Workspaces compartilhados (via membros)
        result = await self.session.execute(
            select(Workspace)
            .join(WorkspaceMember)
            .where(WorkspaceMember.user_id == user_id, Workspace.is_active == True)
        )
        shared = list(result.scalars().all())
        
        # Workspaces familiares (se o workspace está associado a uma família que o usuário pertence)
        # TODO: Implementar busca por família
        
        # Combinar e remover duplicatas
        all_workspaces = {w.id: w for w in owned + shared}
        return list(all_workspaces.values())

    async def update(self, workspace: Workspace) -> Workspace:
        await self.session.commit()
        await self.session.refresh(workspace)
        return workspace

    async def delete(self, workspace_id: UUID) -> bool:
        workspace = await self.get_by_id(workspace_id)
        if workspace:
            workspace.is_active = False  # Soft delete
            await self.session.commit()
            return True
        return False

    async def user_has_access(self, user_id: UUID, workspace_id: UUID) -> bool:
        """Verifica se usuário tem acesso ao workspace"""
        workspace = await self.get_by_id(workspace_id)
        if not workspace:
            return False
        
        # Se é o dono
        if workspace.owner_id == user_id:
            return True
        
        # Se é membro
        result = await self.session.execute(
            select(WorkspaceMember).where(
                WorkspaceMember.workspace_id == workspace_id,
                WorkspaceMember.user_id == user_id,
            )
        )
        member = result.scalar_one_or_none()
        if member:
            return True
        
        # Se é workspace familiar e usuário pertence à família
        if workspace.workspace_type.value == "family" and workspace.family_id:
            # TODO: Verificar se usuário pertence à família
            pass
        
        return False


class SQLAlchemyWorkspaceMemberRepository(WorkspaceMemberRepository):
    """Implementação do repositório de membros do workspace"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, member: WorkspaceMember) -> WorkspaceMember:
        self.session.add(member)
        await self.session.commit()
        await self.session.refresh(member)
        return member

    async def get_by_workspace_id(self, workspace_id: UUID) -> List[WorkspaceMember]:
        result = await self.session.execute(
            select(WorkspaceMember).where(WorkspaceMember.workspace_id == workspace_id)
        )
        return list(result.scalars().all())

    async def get_member(self, user_id: UUID, workspace_id: UUID) -> Optional[WorkspaceMember]:
        result = await self.session.execute(
            select(WorkspaceMember).where(
                WorkspaceMember.user_id == user_id,
                WorkspaceMember.workspace_id == workspace_id,
            )
        )
        return result.scalar_one_or_none()

    async def delete(self, member_id: UUID) -> bool:
        result = await self.session.execute(
            select(WorkspaceMember).where(WorkspaceMember.id == member_id)
        )
        member = result.scalar_one_or_none()
        if member:
            await self.session.delete(member)
            await self.session.commit()
            return True
        return False

