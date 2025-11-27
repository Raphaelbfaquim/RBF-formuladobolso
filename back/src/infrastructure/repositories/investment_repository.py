from typing import List, Optional
from uuid import UUID
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import joinedload
from src.domain.repositories.investment_repository import (
    InvestmentAccountRepository,
    InvestmentTransactionRepository,
)
from src.infrastructure.database.models.investment import InvestmentAccount, InvestmentTransaction


class SQLAlchemyInvestmentAccountRepository(InvestmentAccountRepository):
    """Implementação do repositório de contas de investimento com SQLAlchemy"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, account: InvestmentAccount) -> InvestmentAccount:
        self.session.add(account)
        await self.session.commit()
        await self.session.refresh(account)
        return account

    async def get_by_id(self, account_id: UUID) -> Optional[InvestmentAccount]:
        result = await self.session.execute(
            select(InvestmentAccount)
            .options(joinedload(InvestmentAccount.transactions))
            .where(InvestmentAccount.id == account_id)
        )
        return result.scalar_one_or_none()

    async def get_by_user_id(self, user_id: UUID) -> List[InvestmentAccount]:
        result = await self.session.execute(
            select(InvestmentAccount)
            .options(joinedload(InvestmentAccount.transactions))
            .where(InvestmentAccount.user_id == user_id)
            .order_by(InvestmentAccount.created_at.desc())
        )
        return list(result.scalars().all())

    async def update(self, account: InvestmentAccount) -> InvestmentAccount:
        await self.session.commit()
        await self.session.refresh(account)
        return account

    async def delete(self, account_id: UUID) -> bool:
        account = await self.get_by_id(account_id)
        if account:
            await self.session.delete(account)
            await self.session.commit()
            return True
        return False


class SQLAlchemyInvestmentTransactionRepository(InvestmentTransactionRepository):
    """Implementação do repositório de transações de investimento com SQLAlchemy"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, transaction: InvestmentTransaction) -> InvestmentTransaction:
        self.session.add(transaction)
        await self.session.commit()
        await self.session.refresh(transaction)
        return transaction

    async def get_by_id(self, transaction_id: UUID) -> Optional[InvestmentTransaction]:
        result = await self.session.execute(
            select(InvestmentTransaction)
            .options(joinedload(InvestmentTransaction.account))
            .where(InvestmentTransaction.id == transaction_id)
        )
        return result.scalar_one_or_none()

    async def get_by_account_id(
        self, account_id: UUID, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None
    ) -> List[InvestmentTransaction]:
        query = select(InvestmentTransaction).options(
            joinedload(InvestmentTransaction.account)
        ).where(InvestmentTransaction.account_id == account_id)

        if start_date:
            query = query.where(InvestmentTransaction.transaction_date >= start_date)
        if end_date:
            query = query.where(InvestmentTransaction.transaction_date <= end_date)

        query = query.order_by(InvestmentTransaction.transaction_date.desc())
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_user_id(
        self, user_id: UUID, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None
    ) -> List[InvestmentTransaction]:
        query = select(InvestmentTransaction).options(
            joinedload(InvestmentTransaction.account)
        ).join(InvestmentAccount).where(InvestmentAccount.user_id == user_id)

        if start_date:
            query = query.where(InvestmentTransaction.transaction_date >= start_date)
        if end_date:
            query = query.where(InvestmentTransaction.transaction_date <= end_date)

        query = query.order_by(InvestmentTransaction.transaction_date.desc())
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def update(self, transaction: InvestmentTransaction) -> InvestmentTransaction:
        await self.session.commit()
        await self.session.refresh(transaction)
        return transaction

    async def delete(self, transaction_id: UUID) -> bool:
        transaction = await self.get_by_id(transaction_id)
        if transaction:
            await self.session.delete(transaction)
            await self.session.commit()
            return True
        return False


