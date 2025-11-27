from typing import List, Optional
from uuid import UUID
from datetime import datetime, timedelta
import pytz
from decimal import Decimal
from src.domain.repositories.bill_repository import BillRepository
from src.domain.repositories.account_repository import AccountRepository
from src.domain.repositories.transaction_repository import TransactionRepository
from src.domain.repositories.calendar_repository import CalendarEventRepository
from src.application.services.calendar_event_service import CalendarEventService
from src.infrastructure.database.models.bill import Bill, BillType, BillStatus, RecurrenceType
from src.infrastructure.database.models.transaction import Transaction, TransactionType, TransactionStatus
from src.shared.exceptions import NotFoundException, ValidationException


class BillUseCases:
    """Casos de uso para gerenciamento de contas a pagar/receber"""

    def __init__(
        self,
        bill_repository: BillRepository,
        account_repository: AccountRepository,
        transaction_repository: TransactionRepository,
        calendar_event_repository: Optional[CalendarEventRepository] = None,
    ):
        self.bill_repository = bill_repository
        self.account_repository = account_repository
        self.transaction_repository = transaction_repository
        self.calendar_event_service = (
            CalendarEventService(calendar_event_repository) if calendar_event_repository else None
        )

    async def create_bill(
        self,
        name: str,
        bill_type: str,
        amount: Decimal,
        due_date: datetime,
        user_id: UUID,
        description: Optional[str] = None,
        account_id: Optional[UUID] = None,
        category_id: Optional[UUID] = None,
        is_recurring: bool = False,
        recurrence_type: str = "none",
        recurrence_day: Optional[int] = None,
        recurrence_end_date: Optional[datetime] = None,
    ) -> Bill:
        """Cria uma nova conta"""
        try:
            BillType(bill_type)
        except ValueError:
            raise ValidationException(f"Tipo de conta inválido: {bill_type}")

        if is_recurring:
            try:
                RecurrenceType(recurrence_type)
            except ValueError:
                raise ValidationException(f"Tipo de recorrência inválido: {recurrence_type}")

        bill = Bill(
            name=name,
            description=description,
            bill_type=BillType(bill_type),
            amount=amount,
            due_date=due_date,
            status=BillStatus.PENDING,
            is_recurring=is_recurring,
            recurrence_type=RecurrenceType(recurrence_type) if is_recurring else RecurrenceType.NONE,
            recurrence_day=recurrence_day,
            recurrence_end_date=recurrence_end_date,
            user_id=user_id,
            account_id=account_id,
            category_id=category_id,
        )

        bill = await self.bill_repository.create(bill)

        # Criar evento do calendário para conta a pagar/receber
        if self.calendar_event_service:
            try:
                # Buscar workspace_id da conta se existir
                workspace_id = None
                if account_id:
                    account = await self.account_repository.get_by_id(account_id)
                    if account:
                        workspace_id = account.workspace_id

                await self.calendar_event_service.create_bill_event(
                    bill_id=bill.id,
                    name=name,
                    due_date=due_date,
                    user_id=user_id,
                    workspace_id=workspace_id,
                    amount=amount,
                    bill_type=bill_type,
                )
            except Exception as e:
                print(f"[DEBUG] Erro ao criar evento de calendário para conta: {e}")

        return bill

    async def get_bill(self, bill_id: UUID) -> Bill:
        """Obtém uma conta por ID"""
        bill = await self.bill_repository.get_by_id(bill_id)
        if not bill:
            raise NotFoundException("Conta", str(bill_id))
        return bill

    async def get_user_bills(
        self,
        user_id: UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        bill_type: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[Bill]:
        """Obtém contas de um usuário"""
        return await self.bill_repository.get_by_user_id(
            user_id, start_date, end_date, bill_type, status
        )

    async def get_upcoming_bills(self, user_id: UUID, days: int = 7) -> List[Bill]:
        """Obtém contas próximas do vencimento"""
        return await self.bill_repository.get_upcoming(user_id, days)

    async def get_overdue_bills(self, user_id: UUID) -> List[Bill]:
        """Obtém contas vencidas"""
        return await self.bill_repository.get_overdue(user_id)

    async def pay_bill(
        self,
        bill_id: UUID,
        payment_date: Optional[datetime] = None,
        account_id: Optional[UUID] = None,
        create_transaction: bool = True,
    ) -> Bill:
        """Marca conta como paga e cria transação se solicitado"""
        bill = await self.get_bill(bill_id)

        if bill.status == BillStatus.PAID:
            raise ValidationException("Conta já está paga")

        now = datetime.now(pytz.UTC)
        bill.payment_date = payment_date or now
        bill.status = BillStatus.PAID

        # Criar transação se solicitado
        if create_transaction:
            account_id = account_id or bill.account_id
            if account_id:
                account = await self.account_repository.get_by_id(account_id)
                if not account:
                    raise NotFoundException("Conta", str(account_id))

                transaction = Transaction(
                    description=f"Pagamento: {bill.name}",
                    amount=bill.amount,
                    transaction_type=TransactionType.EXPENSE if bill.bill_type == BillType.EXPENSE else TransactionType.INCOME,
                    status=TransactionStatus.COMPLETED,
                    transaction_date=bill.payment_date,
                    user_id=bill.user_id,
                    account_id=account_id,
                    category_id=bill.category_id,
                )

                transaction = await self.transaction_repository.create(transaction)
                bill.transaction_id = transaction.id

                # Atualizar saldo da conta
                if bill.bill_type == BillType.EXPENSE:
                    account.balance -= bill.amount
                else:
                    account.balance += bill.amount
                await self.account_repository.update(account)

        bill = await self.bill_repository.update(bill)

        # Criar próxima recorrência se necessário
        if bill.is_recurring and bill.recurrence_type != RecurrenceType.NONE:
            await self._create_next_recurrence(bill)

        return bill

    async def _create_next_recurrence(self, bill: Bill):
        """Cria próxima ocorrência de conta recorrente"""
        if not bill.recurrence_end_date:
            return

        now = datetime.now(pytz.UTC)
        if now > bill.recurrence_end_date:
            return  # Fim da recorrência

        next_due_date = None
        if bill.recurrence_type == RecurrenceType.MONTHLY:
            if bill.recurrence_day:
                # Próximo mês no mesmo dia
                if bill.due_date.month == 12:
                    next_due_date = bill.due_date.replace(year=bill.due_date.year + 1, month=1)
                else:
                    next_due_date = bill.due_date.replace(month=bill.due_date.month + 1)
            else:
                next_due_date = bill.due_date + timedelta(days=30)
        elif bill.recurrence_type == RecurrenceType.WEEKLY:
            next_due_date = bill.due_date + timedelta(weeks=1)
        elif bill.recurrence_type == RecurrenceType.DAILY:
            next_due_date = bill.due_date + timedelta(days=1)
        elif bill.recurrence_type == RecurrenceType.YEARLY:
            next_due_date = bill.due_date.replace(year=bill.due_date.year + 1)

        if next_due_date and next_due_date <= bill.recurrence_end_date:
            new_bill = Bill(
                name=bill.name,
                description=bill.description,
                bill_type=bill.bill_type,
                amount=bill.amount,
                due_date=next_due_date,
                status=BillStatus.PENDING,
                is_recurring=True,
                recurrence_type=bill.recurrence_type,
                recurrence_day=bill.recurrence_day,
                recurrence_end_date=bill.recurrence_end_date,
                user_id=bill.user_id,
                account_id=bill.account_id,
                category_id=bill.category_id,
            )
            await self.bill_repository.create(new_bill)

    async def update_bill(
        self,
        bill_id: UUID,
        name: Optional[str] = None,
        description: Optional[str] = None,
        amount: Optional[Decimal] = None,
        due_date: Optional[datetime] = None,
        status: Optional[str] = None,
        payment_date: Optional[datetime] = None,
        account_id: Optional[UUID] = None,
        category_id: Optional[UUID] = None,
    ) -> Bill:
        """Atualiza uma conta"""
        bill = await self.get_bill(bill_id)

        if name:
            bill.name = name
        if description is not None:
            bill.description = description
        if amount:
            bill.amount = amount
        if due_date:
            bill.due_date = due_date
        if status:
            try:
                bill.status = BillStatus(status)
            except ValueError:
                raise ValidationException(f"Status inválido: {status}")
        if payment_date is not None:
            bill.payment_date = payment_date
        if account_id is not None:
            bill.account_id = account_id
        if category_id is not None:
            bill.category_id = category_id

        return await self.bill_repository.update(bill)

    async def delete_bill(self, bill_id: UUID) -> bool:
        """Deleta uma conta"""
        bill = await self.get_bill(bill_id)
        return await self.bill_repository.delete(bill_id)

