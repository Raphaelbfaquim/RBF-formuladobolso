from typing import Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, cast, String, text
from src.domain.repositories.family_invite_repository import FamilyInviteRepository
from src.infrastructure.database.models.family_invite import FamilyInvite


class SQLAlchemyFamilyInviteRepository(FamilyInviteRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, invite: FamilyInvite) -> FamilyInvite:
        self.session.add(invite)
        await self.session.commit()
        await self.session.refresh(invite)
        return invite

    async def get_by_id(self, invite_id: UUID) -> Optional[FamilyInvite]:
        result = await self.session.execute(
            select(FamilyInvite).where(FamilyInvite.id == invite_id)
        )
        return result.scalar_one_or_none()

    async def get_by_token(self, token: str) -> Optional[FamilyInvite]:
        result = await self.session.execute(
            select(FamilyInvite).where(FamilyInvite.token == token)
        )
        return result.scalar_one_or_none()

    async def get_by_email_and_family(self, email: str, family_id: UUID) -> Optional[FamilyInvite]:
        from src.infrastructure.database.models.family_invite import FamilyInviteStatus
        # Fazer cast da coluna enum para text para comparar com string
        # PostgreSQL não permite comparar enum nativo diretamente com VARCHAR
        result = await self.session.execute(
            select(FamilyInvite).where(
                FamilyInvite.email == email,
                FamilyInvite.family_id == family_id,
                cast(FamilyInvite.status, String) == FamilyInviteStatus.PENDING.value
            )
        )
        return result.scalar_one_or_none()

    async def update(self, invite: FamilyInvite) -> FamilyInvite:
        await self.session.commit()
        await self.session.refresh(invite)
        return invite

    async def delete(self, invite_id: UUID) -> bool:
        invite = await self.get_by_id(invite_id)
        if invite:
            await self.session.delete(invite)
            await self.session.commit()
            return True
        return False

