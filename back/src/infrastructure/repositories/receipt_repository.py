from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.domain.repositories.receipt_repository import ReceiptRepository
from src.infrastructure.database.models.receipt import Receipt


class SQLAlchemyReceiptRepository(ReceiptRepository):
    """Implementação do repositório de notas fiscais com SQLAlchemy"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, receipt: Receipt) -> Receipt:
        self.session.add(receipt)
        await self.session.commit()
        await self.session.refresh(receipt)
        return receipt

    async def get_by_id(self, receipt_id: UUID) -> Optional[Receipt]:
        result = await self.session.execute(select(Receipt).where(Receipt.id == receipt_id))
        return result.scalar_one_or_none()

    async def get_by_access_key(self, access_key: str) -> Optional[Receipt]:
        result = await self.session.execute(
            select(Receipt).where(Receipt.access_key == access_key)
        )
        return result.scalar_one_or_none()

    async def get_by_user_id(self, user_id: UUID) -> List[Receipt]:
        result = await self.session.execute(
            select(Receipt).where(Receipt.user_id == user_id).order_by(Receipt.created_at.desc())
        )
        return list(result.scalars().all())

    async def update(self, receipt: Receipt) -> Receipt:
        await self.session.commit()
        await self.session.refresh(receipt)
        return receipt

    async def delete(self, receipt_id: UUID) -> bool:
        receipt = await self.get_by_id(receipt_id)
        if receipt:
            await self.session.delete(receipt)
            await self.session.commit()
            return True
        return False

