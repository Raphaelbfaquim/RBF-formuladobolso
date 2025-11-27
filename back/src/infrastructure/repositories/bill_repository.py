from typing import List, Optional
from uuid import UUID
from datetime import datetime, timedelta
import pytz
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import joinedload
from src.domain.repositories.bill_repository import BillRepository
from src.infrastructure.database.models.bill import Bill, BillStatus


class SQLAlchemyBillRepository(BillRepository):
    """Implementação do repositório de contas com SQLAlchemy"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, bill: Bill) -> Bill:
        self.session.add(bill)
        await self.session.commit()
        await self.session.refresh(bill)
        return bill

    async def get_by_id(self, bill_id: UUID) -> Optional[Bill]:
        result = await self.session.execute(select(Bill).where(Bill.id == bill_id))
        return result.scalar_one_or_none()

    async def get_by_user_id(
        self,
        user_id: UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        bill_type: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[Bill]:
        query = select(Bill).options(joinedload(Bill.category)).where(Bill.user_id == user_id)

        if start_date:
            query = query.where(Bill.due_date >= start_date)
        if end_date:
            query = query.where(Bill.due_date <= end_date)
        if bill_type:
            # Converter string para enum se necessário
            try:
                from src.infrastructure.database.models.bill import BillType
                type_enum = BillType(bill_type.lower())
                query = query.where(Bill.bill_type == type_enum)
            except (ValueError, AttributeError):
                query = query.where(Bill.bill_type == bill_type)
        if status:
            # Converter string para enum se necessário
            try:
                status_enum = BillStatus(status.lower())
                query = query.where(Bill.status == status_enum)
            except (ValueError, AttributeError):
                query = query.where(Bill.status == status)

        query = query.order_by(Bill.due_date.asc())
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_upcoming(self, user_id: UUID, days: int = 7) -> List[Bill]:
        now = datetime.now(pytz.UTC)
        end_date = now + timedelta(days=days)

        result = await self.session.execute(
            select(Bill).where(
                Bill.user_id == user_id,
                Bill.due_date >= now,
                Bill.due_date <= end_date,
                Bill.status == BillStatus.PENDING,
            ).order_by(Bill.due_date.asc())
        )
        return list(result.scalars().all())

    async def get_overdue(self, user_id: UUID) -> List[Bill]:
        now = datetime.now(pytz.UTC)

        result = await self.session.execute(
            select(Bill).where(
                Bill.user_id == user_id,
                Bill.due_date < now,
                Bill.status == BillStatus.PENDING,
            ).order_by(Bill.due_date.asc())
        )
        return list(result.scalars().all())

    async def update(self, bill: Bill) -> Bill:
        await self.session.commit()
        await self.session.refresh(bill)
        return bill

    async def delete(self, bill_id: UUID) -> bool:
        bill = await self.get_by_id(bill_id)
        if bill:
            await self.session.delete(bill)
            await self.session.commit()
            return True
        return False

    async def get_by_transaction_id(self, transaction_id: UUID) -> Optional[Bill]:
        result = await self.session.execute(
            select(Bill).where(Bill.transaction_id == transaction_id)
        )
        return result.scalar_one_or_none()

