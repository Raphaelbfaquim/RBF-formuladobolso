from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.domain.repositories.family_permission_repository import FamilyPermissionRepository
from src.infrastructure.database.models.family_permission import (
    FamilyMemberPermission,
    ModulePermission,
)


class SQLAlchemyFamilyPermissionRepository(FamilyPermissionRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, permission: FamilyMemberPermission) -> FamilyMemberPermission:
        self.session.add(permission)
        await self.session.commit()
        await self.session.refresh(permission)
        return permission

    async def get_by_id(self, permission_id: UUID) -> Optional[FamilyMemberPermission]:
        result = await self.session.execute(
            select(FamilyMemberPermission).where(FamilyMemberPermission.id == permission_id)
        )
        return result.scalar_one_or_none()

    async def get_by_family_member_id(
        self, family_member_id: UUID
    ) -> List[FamilyMemberPermission]:
        result = await self.session.execute(
            select(FamilyMemberPermission).where(
                FamilyMemberPermission.family_member_id == family_member_id
            )
        )
        return list(result.scalars().all())

    async def get_by_family_member_and_module(
        self, family_member_id: UUID, module: ModulePermission
    ) -> Optional[FamilyMemberPermission]:
        # Garantir que module é um enum ModulePermission
        if isinstance(module, str):
            # Se for string, tentar converter para enum
            try:
                module = ModulePermission(module.lower())
            except ValueError:
                # Se não conseguir converter, tentar pelo nome do enum
                module_upper = module.upper()
                if hasattr(ModulePermission, module_upper):
                    module = getattr(ModulePermission, module_upper)
                else:
                    raise ValueError(f"Módulo inválido: {module}")
        
        # Garantir que estamos usando o enum, não uma string
        if not isinstance(module, ModulePermission):
            raise ValueError(f"Módulo deve ser um enum ModulePermission, recebido: {type(module)}")
        
        # O SQLAlchemy deve converter automaticamente o enum para o valor correto
        # Mas vamos garantir que estamos usando o enum, não o valor como string
        result = await self.session.execute(
            select(FamilyMemberPermission).where(
                FamilyMemberPermission.family_member_id == family_member_id,
                FamilyMemberPermission.module == module,  # SQLAlchemy converte automaticamente
            )
        )
        return result.scalar_one_or_none()

    async def update(
        self, permission: FamilyMemberPermission
    ) -> FamilyMemberPermission:
        await self.session.commit()
        await self.session.refresh(permission)
        return permission

    async def delete(self, permission_id: UUID) -> bool:
        permission = await self.get_by_id(permission_id)
        if permission:
            await self.session.delete(permission)
            await self.session.commit()
            return True
        return False

    async def delete_by_family_member_id(self, family_member_id: UUID) -> bool:
        permissions = await self.get_by_family_member_id(family_member_id)
        for permission in permissions:
            await self.session.delete(permission)
        await self.session.commit()
        return True

