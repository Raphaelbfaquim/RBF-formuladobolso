from typing import List, Optional
from uuid import UUID
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.domain.repositories.transfer_repository import TransferRepository
from src.infrastructure.database.models.transfer import Transfer


class SQLAlchemyTransferRepository(TransferRepository):
    """Implementação do repositório de transferências"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, transfer: Transfer) -> Transfer:
        self.session.add(transfer)
        await self.session.commit()
        await self.session.refresh(transfer)
        return transfer

    async def get_by_id(self, transfer_id: UUID) -> Optional[Transfer]:
        result = await self.session.execute(select(Transfer).where(Transfer.id == transfer_id))
        return result.scalar_one_or_none()

    async def get_by_user_id(
        self,
        user_id: UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[Transfer]:
        query = select(Transfer).where(Transfer.user_id == user_id)
        
        if start_date:
            query = query.where(Transfer.transaction_date >= start_date)
        if end_date:
            query = query.where(Transfer.transaction_date <= end_date)
        
        query = query.order_by(Transfer.transfer_date.desc())
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def update(self, transfer: Transfer) -> Transfer:
        await self.session.commit()
        await self.session.refresh(transfer)
        return transfer

    async def delete(self, transfer_id: UUID) -> bool:
        transfer = await self.get_by_id(transfer_id)
        if transfer:
            await self.session.delete(transfer)
            await self.session.commit()
            return True
        return False

