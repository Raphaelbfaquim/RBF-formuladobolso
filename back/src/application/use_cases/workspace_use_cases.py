from typing import List, Optional
from uuid import UUID
from src.domain.repositories.workspace_repository import (
    WorkspaceRepository,
    WorkspaceMemberRepository,
)
from src.domain.repositories.family_repository import FamilyMemberRepository
from src.infrastructure.database.models.workspace import Workspace, WorkspaceType, WorkspaceMember
from src.shared.exceptions import NotFoundException, UnauthorizedException

NotFoundError = NotFoundException
UnauthorizedError = UnauthorizedException


class WorkspaceUseCases:
    """Casos de uso para gerenciamento de workspaces"""

    def __init__(
        self,
        workspace_repository: WorkspaceRepository,
        workspace_member_repository: WorkspaceMemberRepository,
        family_member_repository: FamilyMemberRepository,
    ):
        self.workspace_repository = workspace_repository
        self.workspace_member_repository = workspace_member_repository
        self.family_member_repository = family_member_repository

    async def create_workspace(
        self,
        name: str,
        description: Optional[str],
        workspace_type: WorkspaceType,
        owner_id: UUID,
        family_id: Optional[UUID] = None,
        color: Optional[str] = None,
        icon: Optional[str] = None,
    ) -> Workspace:
        """Cria um novo workspace"""
        # Se for workspace familiar, verificar se usuário pertence à família
        if workspace_type == WorkspaceType.FAMILY and family_id:
            member = await self.family_member_repository.get_member_in_family(owner_id, family_id)
            if not member:
                raise UnauthorizedError("Você não pertence a esta família")

        workspace = Workspace(
            name=name,
            description=description,
            workspace_type=workspace_type,
            owner_id=owner_id,
            family_id=family_id,
            color=color,
            icon=icon,
        )
        return await self.workspace_repository.create(workspace)

    async def get_user_workspaces(self, user_id: UUID) -> List[Workspace]:
        """Obtém todos os workspaces acessíveis pelo usuário"""
        return await self.workspace_repository.get_accessible_by_user(user_id)

    async def get_workspace(self, workspace_id: UUID, user_id: UUID) -> Workspace:
        """Obtém um workspace específico"""
        workspace = await self.workspace_repository.get_by_id(workspace_id)
        if not workspace:
            raise NotFoundError("Workspace não encontrado")

        # Verificar acesso
        has_access = await self.workspace_repository.user_has_access(user_id, workspace_id)
        if not has_access:
            raise UnauthorizedError("Você não tem acesso a este workspace")

        return workspace

    async def update_workspace(
        self,
        workspace_id: UUID,
        user_id: UUID,
        name: Optional[str] = None,
        description: Optional[str] = None,
        color: Optional[str] = None,
        icon: Optional[str] = None,
    ) -> Workspace:
        """Atualiza um workspace"""
        workspace = await self.get_workspace(workspace_id, user_id)

        # Verificar se é o dono
        if workspace.owner_id != user_id:
            raise UnauthorizedError("Apenas o dono pode atualizar o workspace")

        if name:
            workspace.name = name
        if description is not None:
            workspace.description = description
        if color:
            workspace.color = color
        if icon:
            workspace.icon = icon

        return await self.workspace_repository.update(workspace)

    async def delete_workspace(self, workspace_id: UUID, user_id: UUID) -> bool:
        """Deleta um workspace (soft delete)"""
        workspace = await self.get_workspace(workspace_id, user_id)

        # Verificar se é o dono
        if workspace.owner_id != user_id:
            raise UnauthorizedError("Apenas o dono pode deletar o workspace")

        return await self.workspace_repository.delete(workspace_id)

    async def share_workspace(
        self, workspace_id: UUID, owner_id: UUID, user_id: UUID, can_edit: bool = True, can_delete: bool = False
    ) -> WorkspaceMember:
        """Compartilha workspace com outro usuário"""
        workspace = await self.get_workspace(workspace_id, owner_id)

        # Verificar se é o dono
        if workspace.owner_id != owner_id:
            raise UnauthorizedError("Apenas o dono pode compartilhar o workspace")

        # Verificar se já é membro
        existing = await self.workspace_member_repository.get_member(user_id, workspace_id)
        if existing:
            raise ValueError("Usuário já tem acesso a este workspace")

        member = WorkspaceMember(
            workspace_id=workspace_id,
            user_id=user_id,
            can_edit=can_edit,
            can_delete=can_delete,
        )
        return await self.workspace_member_repository.create(member)

