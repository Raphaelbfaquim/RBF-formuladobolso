from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.domain.repositories.family_repository import (
    FamilyRepository,
    FamilyMemberRepository,
    FamilyChatRepository,
)
from src.infrastructure.database.models.user import Family, FamilyMember
from src.infrastructure.database.models.family_chat import FamilyChatMessage


class SQLAlchemyFamilyRepository(FamilyRepository):
    """Implementação do repositório de famílias com SQLAlchemy"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, family: Family) -> Family:
        self.session.add(family)
        await self.session.commit()
        await self.session.refresh(family)
        return family

    async def get_by_id(self, family_id: UUID) -> Optional[Family]:
        result = await self.session.execute(select(Family).where(Family.id == family_id))
        return result.scalar_one_or_none()

    async def get_by_user_id(self, user_id: UUID) -> List[Family]:
        result = await self.session.execute(
            select(Family)
            .join(FamilyMember)
            .where(FamilyMember.user_id == user_id)
        )
        return list(result.scalars().all())

    async def update(self, family: Family) -> Family:
        await self.session.commit()
        await self.session.refresh(family)
        return family

    async def delete(self, family_id: UUID) -> bool:
        family = await self.get_by_id(family_id)
        if family:
            await self.session.delete(family)
            await self.session.commit()
            return True
        return False


class SQLAlchemyFamilyMemberRepository(FamilyMemberRepository):
    """Implementação do repositório de membros da família"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, member: FamilyMember) -> FamilyMember:
        self.session.add(member)
        await self.session.commit()
        await self.session.refresh(member)
        return member

    async def get_by_id(self, member_id: UUID) -> Optional[FamilyMember]:
        result = await self.session.execute(
            select(FamilyMember).where(FamilyMember.id == member_id)
        )
        return result.scalar_one_or_none()

    async def get_by_family_id(self, family_id: UUID) -> List[FamilyMember]:
        result = await self.session.execute(
            select(FamilyMember).where(FamilyMember.family_id == family_id)
        )
        return list(result.scalars().all())

    async def get_by_user_id(self, user_id: UUID) -> List[FamilyMember]:
        result = await self.session.execute(
            select(FamilyMember).where(FamilyMember.user_id == user_id)
        )
        return list(result.scalars().all())

    async def get_member_in_family(self, user_id: UUID, family_id: UUID) -> Optional[FamilyMember]:
        result = await self.session.execute(
            select(FamilyMember).where(
                FamilyMember.user_id == user_id,
                FamilyMember.family_id == family_id,
            )
        )
        return result.scalar_one_or_none()

    async def update(self, member: FamilyMember) -> FamilyMember:
        await self.session.commit()
        await self.session.refresh(member)
        return member

    async def delete(self, member_id: UUID) -> bool:
        member = await self.get_by_id(member_id)
        if member:
            await self.session.delete(member)
            await self.session.commit()
            return True
        return False


class SQLAlchemyFamilyChatRepository(FamilyChatRepository):
    """Implementação do repositório de chat familiar"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, message: FamilyChatMessage) -> FamilyChatMessage:
        self.session.add(message)
        await self.session.commit()
        await self.session.refresh(message)
        return message

    async def get_by_family_id(self, family_id: UUID, limit: int = 50) -> List[FamilyChatMessage]:
        result = await self.session.execute(
            select(FamilyChatMessage)
            .where(FamilyChatMessage.family_id == family_id)
            .order_by(FamilyChatMessage.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

