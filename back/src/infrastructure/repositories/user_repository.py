from typing import Optional
from uuid import UUID
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from src.domain.repositories.user_repository import UserRepository
from src.infrastructure.database.models.user import User


class SQLAlchemyUserRepository(UserRepository):
    """Implementação do repositório de usuários com SQLAlchemy"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user: User) -> User:
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        result = await self.session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self.session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> Optional[User]:
        result = await self.session.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()

    async def update(self, user: User) -> User:
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def delete(self, user_id: UUID) -> bool:
        user = await self.get_by_id(user_id)
        if user:
            await self.session.delete(user)
            await self.session.commit()
            return True
        return False

    async def get_by_reset_token(self, reset_token: str) -> Optional[User]:
        result = await self.session.execute(
            select(User).where(User.reset_token == reset_token)
        )
        return result.scalar_one_or_none()

    async def update_reset_token(self, user_id: UUID, reset_token: Optional[str], reset_token_expires: Optional[datetime]) -> bool:
        stmt = (
            update(User)
            .where(User.id == user_id)
            .values(reset_token=reset_token, reset_token_expires=reset_token_expires)
        )
        await self.session.execute(stmt)
        await self.session.commit()
        return True

    async def update_password(self, user_id: UUID, hashed_password: str) -> bool:
        stmt = (
            update(User)
            .where(User.id == user_id)
            .values(hashed_password=hashed_password)
        )
        await self.session.execute(stmt)
        await self.session.commit()
        return True

