from typing import List, Optional
from uuid import UUID
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from decimal import Decimal
from src.domain.repositories.transaction_repository import TransactionRepository
from src.infrastructure.database.models.transaction import Transaction, TransactionType
from src.infrastructure.database.models.bill import Bill, BillStatus


class SQLAlchemyTransactionRepository(TransactionRepository):
    """Implementação do repositório de transações com SQLAlchemy"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, transaction: Transaction) -> Transaction:
        self.session.add(transaction)
        await self.session.commit()
        await self.session.refresh(transaction)
        return transaction

    async def get_by_id(self, transaction_id: UUID) -> Optional[Transaction]:
        result = await self.session.execute(
            select(Transaction).where(Transaction.id == transaction_id)
        )
        return result.scalar_one_or_none()

    async def get_by_user_id(
        self,
        user_id: UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[Transaction]:
        from sqlalchemy.orm import joinedload
        
        # Subquery para obter transaction_ids de bills canceladas
        cancelled_bills_subquery = select(Bill.transaction_id).where(
            and_(
                Bill.status == BillStatus.CANCELLED,
                Bill.transaction_id.isnot(None)
            )
        )
        
        query = select(Transaction).options(
            joinedload(Transaction.category),
            joinedload(Transaction.account)
        ).where(
            and_(
                Transaction.user_id == user_id,
                ~Transaction.id.in_(cancelled_bills_subquery)
            )
        )
        
        if start_date:
            # Garantir que start_date seja timezone-aware
            import pytz
            if start_date.tzinfo is None:
                start_date = pytz.UTC.localize(start_date)
            else:
                start_date = start_date.astimezone(pytz.UTC)
            query = query.where(Transaction.transaction_date >= start_date)
        if end_date:
            # Garantir que end_date seja timezone-aware e inclua o final do dia
            import pytz
            if end_date.tzinfo is None:
                end_date = pytz.UTC.localize(end_date)
            else:
                end_date = end_date.astimezone(pytz.UTC)
            # Adicionar 23:59:59.999 para incluir todo o dia
            from datetime import timedelta
            end_date = end_date.replace(hour=23, minute=59, second=59, microsecond=999999)
            query = query.where(Transaction.transaction_date <= end_date)
        
        query = query.order_by(Transaction.transaction_date.desc())
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_account_id(
        self,
        account_id: UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[Transaction]:
        query = select(Transaction).where(Transaction.account_id == account_id)
        
        if start_date:
            query = query.where(Transaction.transaction_date >= start_date)
        if end_date:
            query = query.where(Transaction.transaction_date <= end_date)
        
        query = query.order_by(Transaction.transaction_date.desc())
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def update(self, transaction: Transaction) -> Transaction:
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

    async def get_sum_by_period(
        self,
        user_id: UUID,
        start_date: datetime,
        end_date: datetime,
        transaction_type: Optional[str] = None,
    ) -> float:
        query = select(
            func.sum(Transaction.amount)
        ).where(
            and_(
                Transaction.user_id == user_id,
                Transaction.transaction_date >= start_date,
                Transaction.transaction_date <= end_date,
                Transaction.status == "completed",
            )
        )
        
        if transaction_type:
            query = query.where(Transaction.transaction_type == transaction_type)
        
        result = await self.session.execute(query)
        total = result.scalar() or Decimal("0")
        return float(total)

    async def search(
        self,
        user_id: UUID,
        search_text: Optional[str] = None,
        transaction_type: Optional[str] = None,
        category_id: Optional[UUID] = None,
        account_id: Optional[UUID] = None,
        workspace_id: Optional[UUID] = None,
        min_amount: Optional[float] = None,
        max_amount: Optional[float] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
        order_by: Optional[str] = None,
        order_direction: str = "desc",
    ) -> tuple[List[Transaction], int]:
        """Busca avançada de transações com filtros múltiplos"""
        from sqlalchemy import or_, desc, asc
        
        # Subquery para obter transaction_ids de bills canceladas
        cancelled_bills_subquery = select(Bill.transaction_id).where(
            and_(
                Bill.status == BillStatus.CANCELLED,
                Bill.transaction_id.isnot(None)
            )
        )
        
        # Query base (excluindo transações de bills canceladas)
        query = select(Transaction).where(
            and_(
                Transaction.user_id == user_id,
                ~Transaction.id.in_(cancelled_bills_subquery)
            )
        )
        count_query = select(func.count(Transaction.id)).where(
            and_(
                Transaction.user_id == user_id,
                ~Transaction.id.in_(cancelled_bills_subquery)
            )
        )
        
        # Filtros
        conditions = []
        
        if search_text:
            search_pattern = f"%{search_text.lower()}%"
            conditions.append(
                or_(
                    Transaction.description.ilike(search_pattern),
                    Transaction.notes.ilike(search_pattern),
                )
            )
        
        if transaction_type:
            # Converter string para enum se necessário
            from src.infrastructure.database.models.transaction import TransactionType
            try:
                type_enum = TransactionType(transaction_type)
                conditions.append(Transaction.transaction_type == type_enum)
            except ValueError:
                # Se não for um valor válido do enum, tentar como string
                conditions.append(Transaction.transaction_type == transaction_type)
        
        if category_id:
            conditions.append(Transaction.category_id == category_id)
        
        if account_id:
            conditions.append(Transaction.account_id == account_id)
        
        if workspace_id:
            conditions.append(Transaction.workspace_id == workspace_id)
        
        if min_amount is not None:
            conditions.append(Transaction.amount >= Decimal(str(min_amount)))
        
        if max_amount is not None:
            conditions.append(Transaction.amount <= Decimal(str(max_amount)))
        
        if start_date:
            conditions.append(Transaction.transaction_date >= start_date)
        
        if end_date:
            conditions.append(Transaction.transaction_date <= end_date)
        
        if status:
            # Converter string para enum se necessário
            from src.infrastructure.database.models.transaction import TransactionStatus
            try:
                status_enum = TransactionStatus(status.lower())
                conditions.append(Transaction.status == status_enum)
                print(f"[DEBUG] Filtro de status aplicado: {status} -> {status_enum}")
            except (ValueError, AttributeError):
                # Se não for um valor válido do enum, tentar como string
                print(f"[DEBUG] Status não é um enum válido, tentando como string: {status}")
                conditions.append(Transaction.status == status)
        
        # Aplicar condições
        if conditions:
            query = query.where(and_(*conditions))
            count_query = count_query.where(and_(*conditions))
        
        # Ordenação
        if order_by:
            order_column = getattr(Transaction, order_by, Transaction.transaction_date)
            if order_direction.lower() == "asc":
                query = query.order_by(asc(order_column))
            else:
                query = query.order_by(desc(order_column))
        else:
            query = query.order_by(desc(Transaction.transaction_date))
        
        # Paginação
        query = query.limit(limit).offset(offset)
        
        # Executar queries
        result = await self.session.execute(query)
        transactions = list(result.scalars().all())
        
        count_result = await self.session.execute(count_query)
        total_count = count_result.scalar() or 0
        
        return transactions, total_count

