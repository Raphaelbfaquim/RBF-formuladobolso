from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.domain.repositories.account_repository import AccountRepository
from src.infrastructure.database.models.account import Account


class SQLAlchemyAccountRepository(AccountRepository):
    """Implementação do repositório de contas com SQLAlchemy"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, account: Account) -> Account:
        self.session.add(account)
        await self.session.commit()
        await self.session.refresh(account)
        return account

    async def get_by_id(self, account_id: UUID) -> Optional[Account]:
        result = await self.session.execute(select(Account).where(Account.id == account_id))
        return result.scalar_one_or_none()

    async def get_by_user_id(self, user_id: UUID) -> List[Account]:
        result = await self.session.execute(
            select(Account).where(Account.owner_id == user_id, Account.is_active == True)
        )
        return list(result.scalars().all())

    async def get_by_family_id(self, family_id: UUID) -> List[Account]:
        result = await self.session.execute(
            select(Account).where(Account.family_id == family_id, Account.is_active == True)
        )
        return list(result.scalars().all())

    async def update(self, account: Account) -> Account:
        await self.session.commit()
        await self.session.refresh(account)
        return account

    async def delete(self, account_id: UUID) -> bool:
        account = await self.get_by_id(account_id)
        if account:
            account.is_active = False
            await self.session.commit()
            return True
        return False

