from typing import List, Optional
from uuid import UUID
from datetime import datetime, timedelta
from decimal import Decimal
from src.domain.repositories.scheduled_transaction_repository import ScheduledTransactionRepository
from src.domain.repositories.transaction_repository import TransactionRepository
from src.domain.repositories.account_repository import AccountRepository
from src.infrastructure.database.models.scheduled_transaction import (
    ScheduledTransaction,
    ScheduledTransactionStatus,
    RecurrenceType,
    TransactionExecution,
)
from src.infrastructure.database.models.transaction import Transaction, TransactionType, TransactionStatus
from src.shared.exceptions import NotFoundException, ValidationException


class ScheduledTransactionUseCases:
    """Casos de uso para transações agendadas"""

    def __init__(
        self,
        scheduled_repository: ScheduledTransactionRepository,
        transaction_repository: TransactionRepository,
        account_repository: AccountRepository,
    ):
        self.scheduled_repository = scheduled_repository
        self.transaction_repository = transaction_repository
        self.account_repository = account_repository

    async def create_scheduled_transaction(
        self,
        description: str,
        amount: Decimal,
        transaction_type: str,
        account_id: UUID,
        user_id: UUID,
        start_date: datetime,
        recurrence_type: str = "none",
        end_date: Optional[datetime] = None,
        max_executions: Optional[int] = None,
        auto_execute: bool = False,
        category_id: Optional[UUID] = None,
        workspace_id: Optional[UUID] = None,
        notes: Optional[str] = None,
        recurrence_day: Optional[int] = None,
        recurrence_weekday: Optional[int] = None,
    ) -> ScheduledTransaction:
        """Cria uma transação agendada"""
        # Validar tipo
        try:
            TransactionType(transaction_type)
        except ValueError:
            raise ValidationException(f"Tipo de transação inválido: {transaction_type}")

        # Validar recorrência
        try:
            RecurrenceType(recurrence_type)
        except ValueError:
            raise ValidationException(f"Tipo de recorrência inválido: {recurrence_type}")

        # Verificar conta
        account = await self.account_repository.get_by_id(account_id)
        if not account:
            raise NotFoundException("Conta", str(account_id))

        scheduled = ScheduledTransaction(
            description=description,
            amount=amount,
            transaction_type=transaction_type,
            status=ScheduledTransactionStatus.ACTIVE,
            start_date=start_date,
            end_date=end_date,
            next_execution_date=start_date,
            recurrence_type=RecurrenceType(recurrence_type),
            recurrence_day=recurrence_day,
            recurrence_weekday=recurrence_weekday,
            max_executions=max_executions,
            auto_execute=auto_execute,
            user_id=user_id,
            account_id=account_id,
            category_id=category_id,
            workspace_id=workspace_id,
            notes=notes,
        )

        return await self.scheduled_repository.create(scheduled)

    async def get_scheduled_transactions(self, user_id: UUID) -> List[ScheduledTransaction]:
        """Obtém transações agendadas do usuário"""
        return await self.scheduled_repository.get_by_user_id(user_id)

    async def execute_scheduled_transaction(self, scheduled_id: UUID) -> Transaction:
        """Executa uma transação agendada"""
        scheduled = await self.scheduled_repository.get_by_id(scheduled_id)
        if not scheduled:
            raise NotFoundException("Transação agendada", str(scheduled_id))

        if scheduled.status != ScheduledTransactionStatus.ACTIVE:
            raise ValidationException("Transação agendada não está ativa")

        # Criar transação
        transaction = Transaction(
            description=scheduled.description,
            amount=scheduled.amount,
            transaction_type=TransactionType(scheduled.transaction_type),
            status=TransactionStatus.COMPLETED,
            transaction_date=scheduled.next_execution_date,
            user_id=scheduled.user_id,
            account_id=scheduled.account_id,
            category_id=scheduled.category_id,
            workspace_id=scheduled.workspace_id,
            notes=scheduled.notes,
        )
        transaction = await self.transaction_repository.create(transaction)

        # Atualizar saldo da conta
        account = await self.account_repository.get_by_id(scheduled.account_id)
        if scheduled.transaction_type == "income":
            account.balance += scheduled.amount
        elif scheduled.transaction_type == "expense":
            account.balance -= scheduled.amount
        await self.account_repository.update(account)

        # Registrar execução
        execution = TransactionExecution(
            scheduled_transaction_id=scheduled.id,
            transaction_id=transaction.id,
            execution_date=scheduled.next_execution_date,
            status="success",
        )
        # TODO: Adicionar ao repositório de execuções

        # Atualizar próxima execução
        scheduled.execution_count += 1
        scheduled.last_execution_date = scheduled.next_execution_date

        # Calcular próxima execução
        if scheduled.recurrence_type != RecurrenceType.NONE:
            scheduled.next_execution_date = self._calculate_next_execution(scheduled)
        else:
            scheduled.status = ScheduledTransactionStatus.COMPLETED

        # Verificar limites
        if scheduled.max_executions and scheduled.execution_count >= scheduled.max_executions:
            scheduled.status = ScheduledTransactionStatus.COMPLETED

        if scheduled.end_date and scheduled.next_execution_date > scheduled.end_date:
            scheduled.status = ScheduledTransactionStatus.COMPLETED

        await self.scheduled_repository.update(scheduled)

        return transaction

    def _calculate_next_execution(self, scheduled: ScheduledTransaction) -> datetime:
        """Calcula próxima data de execução"""
        current = scheduled.next_execution_date

        if scheduled.recurrence_type == RecurrenceType.DAILY:
            return current + timedelta(days=1)
        elif scheduled.recurrence_type == RecurrenceType.WEEKLY:
            return current + timedelta(weeks=1)
        elif scheduled.recurrence_type == RecurrenceType.MONTHLY:
            # Próximo mês, mesmo dia
            if current.month == 12:
                return current.replace(year=current.year + 1, month=1)
            else:
                return current.replace(month=current.month + 1)
        elif scheduled.recurrence_type == RecurrenceType.YEARLY:
            return current.replace(year=current.year + 1)

        return current

    async def pause_scheduled_transaction(self, scheduled_id: UUID) -> ScheduledTransaction:
        """Pausa uma transação agendada"""
        scheduled = await self.scheduled_repository.get_by_id(scheduled_id)
        if not scheduled:
            raise NotFoundException("Transação agendada", str(scheduled_id))

        scheduled.status = ScheduledTransactionStatus.PAUSED
        return await self.scheduled_repository.update(scheduled)

    async def resume_scheduled_transaction(self, scheduled_id: UUID) -> ScheduledTransaction:
        """Retoma uma transação agendada"""
        scheduled = await self.scheduled_repository.get_by_id(scheduled_id)
        if not scheduled:
            raise NotFoundException("Transação agendada", str(scheduled_id))

        scheduled.status = ScheduledTransactionStatus.ACTIVE
        return await self.scheduled_repository.update(scheduled)

    async def cancel_scheduled_transaction(self, scheduled_id: UUID) -> ScheduledTransaction:
        """Cancela uma transação agendada"""
        scheduled = await self.scheduled_repository.get_by_id(scheduled_id)
        if not scheduled:
            raise NotFoundException("Transação agendada", str(scheduled_id))

        scheduled.status = ScheduledTransactionStatus.CANCELLED
        return await self.scheduled_repository.update(scheduled)

