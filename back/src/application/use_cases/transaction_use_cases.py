from typing import List, Optional
from uuid import UUID
from datetime import datetime
from decimal import Decimal
from src.domain.repositories.transaction_repository import TransactionRepository
from src.domain.repositories.account_repository import AccountRepository
from src.domain.repositories.bill_repository import BillRepository
from src.domain.repositories.goal_repository import GoalRepository, GoalContributionRepository
from src.domain.repositories.calendar_repository import CalendarEventRepository
from src.application.services.calendar_event_service import CalendarEventService
from src.application.services.gamification_service import GamificationService
from src.infrastructure.database.models.transaction import (
    Transaction,
    TransactionType,
    TransactionStatus,
)
from src.infrastructure.database.models.bill import Bill, BillType, BillStatus, RecurrenceType
from src.shared.exceptions import NotFoundException, ValidationException


class TransactionUseCases:
    """Casos de uso para gerenciamento de transações"""

    def __init__(
        self,
        transaction_repository: TransactionRepository,
        account_repository: AccountRepository,
        bill_repository: Optional[BillRepository] = None,
        goal_repository: Optional[GoalRepository] = None,
        goal_contribution_repository: Optional[GoalContributionRepository] = None,
        calendar_event_repository: Optional[CalendarEventRepository] = None,
        gamification_service: Optional[GamificationService] = None,
    ):
        self.transaction_repository = transaction_repository
        self.account_repository = account_repository
        self.bill_repository = bill_repository
        self.goal_repository = goal_repository
        self.goal_contribution_repository = goal_contribution_repository
        self.calendar_event_service = (
            CalendarEventService(calendar_event_repository) if calendar_event_repository else None
        )
        self.gamification_service = gamification_service

    async def create_transaction(
        self,
        description: str,
        amount: Decimal,
        transaction_type: str,
        transaction_date: datetime,
        user_id: UUID,
        account_id: UUID,
        category_id: Optional[UUID] = None,
        receipt_id: Optional[UUID] = None,
        status: str = "completed",
        notes: Optional[str] = None,
        workspace_id: Optional[UUID] = None,
    ) -> Transaction:
        """Cria uma nova transação"""
        # Validar tipo de transação
        try:
            TransactionType(transaction_type)
        except ValueError:
            raise ValidationException(f"Tipo de transação inválido: {transaction_type}")

        # Validar status
        try:
            TransactionStatus(status)
        except ValueError:
            raise ValidationException(f"Status inválido: {status}")

        # Verificar se conta existe
        account = await self.account_repository.get_by_id(account_id)
        if not account:
            raise NotFoundException("Conta", str(account_id))

        # Criar transação
        transaction = Transaction(
            description=description,
            amount=amount,
            transaction_type=TransactionType(transaction_type),
            status=TransactionStatus(status),
            transaction_date=transaction_date,
            notes=notes,
            user_id=user_id,
            account_id=account_id,
            category_id=category_id,
            receipt_id=receipt_id,
            workspace_id=workspace_id,
        )

        transaction = await self.transaction_repository.create(transaction)

        # Criar evento do calendário para transações concluídas
        if transaction.status == TransactionStatus.COMPLETED and self.calendar_event_service:
            try:
                await self.calendar_event_service.create_transaction_event(
                    transaction_id=transaction.id,
                    title=description,
                    transaction_date=transaction_date,
                    user_id=user_id,
                    workspace_id=workspace_id,
                    amount=amount,
                    transaction_type=transaction_type,
                )
            except Exception as e:
                print(f"[DEBUG] Erro ao criar evento de calendário para transação: {e}")

        # Se for uma transação de poupança (income ou expense na categoria de poupança), distribuir para metas
        # TODO: Implementar distribuição automática para metas quando necessário
        # if category_id and transaction.status == TransactionStatus.COMPLETED:
        #     await self._distribute_to_goals(transaction, category_id, user_id)

        # Se for uma despesa pendente, criar automaticamente uma bill (conta a pagar)
        if (transaction.transaction_type == TransactionType.EXPENSE and 
            transaction.status == TransactionStatus.PENDING and 
            self.bill_repository):
            try:
                bill = Bill(
                    name=description,
                    description=notes,
                    bill_type=BillType.EXPENSE,
                    amount=amount,
                    due_date=transaction_date,
                    status=BillStatus.PENDING,
                    is_recurring=False,
                    recurrence_type=RecurrenceType.NONE,
                    user_id=user_id,
                    account_id=account_id,
                    category_id=category_id,
                    transaction_id=transaction.id,  # Associar à transação
                )
                await self.bill_repository.create(bill)
                print(f"[DEBUG] Bill criada automaticamente para transação pendente: {transaction.id}")
            except Exception as e:
                print(f"[ERROR] Erro ao criar bill automaticamente: {e}")
                import traceback
                traceback.print_exc()
                # Não falhar a criação da transação se a bill falhar

        # Atualizar saldo da conta se a transação estiver completa
        if transaction.status == TransactionStatus.COMPLETED:
            if transaction.transaction_type == TransactionType.INCOME:
                account.balance += amount
            elif transaction.transaction_type == TransactionType.EXPENSE:
                account.balance -= amount
            # TRANSFER não altera saldo aqui (será tratado em outro lugar)
            await self.account_repository.update(account)

        # Gamificação: Adicionar XP e verificar badges
        if self.gamification_service:
            try:
                # Adicionar XP por criar transação
                await self.gamification_service.add_points(user_id, 10, "Registrar transação")
                
                # Verificar e conceder badges automaticamente
                await self.gamification_service.check_achievements(user_id)
                
                # Atualizar streak
                await self.gamification_service.update_streak(user_id)
            except Exception as e:
                print(f"[DEBUG] Erro ao processar gamificação: {e}")
                import traceback
                traceback.print_exc()
                # Não falhar a criação da transação se a gamificação falhar

        return transaction

    async def get_transaction(self, transaction_id: UUID) -> Transaction:
        """Obtém uma transação por ID"""
        transaction = await self.transaction_repository.get_by_id(transaction_id)
        if not transaction:
            raise NotFoundException("Transação", str(transaction_id))
        return transaction

    async def get_user_transactions(
        self,
        user_id: UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[Transaction]:
        """Obtém transações de um usuário"""
        return await self.transaction_repository.get_by_user_id(
            user_id, start_date, end_date
        )

    async def update_transaction(
        self,
        transaction_id: UUID,
        description: Optional[str] = None,
        amount: Optional[Decimal] = None,
        transaction_date: Optional[datetime] = None,
        status: Optional[str] = None,
        category_id: Optional[UUID] = None,
        notes: Optional[str] = None,
    ) -> Transaction:
        """Atualiza uma transação"""
        transaction = await self.get_transaction(transaction_id)
        old_amount = transaction.amount
        old_status = transaction.status
        account = await self.account_repository.get_by_id(transaction.account_id)

        if description:
            transaction.description = description
        if amount:
            transaction.amount = amount
        if transaction_date:
            transaction.transaction_date = transaction_date
        if status:
            try:
                transaction.status = TransactionStatus(status)
            except ValueError:
                raise ValidationException(f"Status inválido: {status}")
        if category_id is not None:
            transaction.category_id = category_id
        if notes is not None:
            transaction.notes = notes

        transaction = await self.transaction_repository.update(transaction)

        # Atualizar bill associada se for uma despesa
        if (transaction.transaction_type == TransactionType.EXPENSE and 
            self.bill_repository):
            try:
                # Buscar bill associada à transação
                bill = await self.bill_repository.get_by_transaction_id(transaction.id)
                
                # Verificar se houve mudanças relevantes
                bill_needs_update = False
                if bill:
                    # Normalizar datas para comparação (remover timezone se necessário)
                    bill_due_date = bill.due_date.replace(tzinfo=None) if bill.due_date and bill.due_date.tzinfo else bill.due_date
                    trans_date = transaction.transaction_date.replace(tzinfo=None) if transaction.transaction_date and transaction.transaction_date.tzinfo else transaction.transaction_date
                    
                    # Verificar se precisa atualizar campos da bill
                    if (bill.name != transaction.description or
                        (bill.description or '') != (transaction.notes or '') or
                        bill.amount != transaction.amount or
                        bill_due_date != trans_date or
                        bill.category_id != transaction.category_id or
                        bill.account_id != transaction.account_id):
                        bill_needs_update = True
                
                # Atualizar ou criar bill baseado no status da transação
                if transaction.status == TransactionStatus.COMPLETED:
                    # Transação foi concluída -> marcar bill como paga
                    if bill:
                        bill.status = BillStatus.PAID
                        bill.payment_date = transaction.transaction_date
                        # Sincronizar todos os campos
                        bill.name = transaction.description
                        bill.description = transaction.notes
                        bill.amount = transaction.amount
                        bill.due_date = transaction.transaction_date
                        bill.category_id = transaction.category_id
                        bill.account_id = transaction.account_id
                        await self.bill_repository.update(bill)
                        print(f"[DEBUG] Bill {bill.id} atualizada para PAID e sincronizada com transação {transaction.id}")
                    else:
                        # Se não existe bill, criar uma (caso raro)
                        bill = Bill(
                            name=transaction.description,
                            description=transaction.notes,
                            bill_type=BillType.EXPENSE,
                            amount=transaction.amount,
                            due_date=transaction.transaction_date,
                            status=BillStatus.PAID,
                            payment_date=transaction.transaction_date,
                            is_recurring=False,
                            recurrence_type=RecurrenceType.NONE,
                            user_id=transaction.user_id,
                            account_id=transaction.account_id,
                            category_id=transaction.category_id,
                            transaction_id=transaction.id,
                        )
                        await self.bill_repository.create(bill)
                        print(f"[DEBUG] Bill criada como paga para transação {transaction.id}")
                
                elif transaction.status == TransactionStatus.PENDING:
                    # Transação voltou para pendente -> marcar bill como pendente
                    if bill:
                        bill.status = BillStatus.PENDING
                        bill.payment_date = None
                        # Sincronizar todos os campos
                        bill.name = transaction.description
                        bill.description = transaction.notes
                        bill.amount = transaction.amount
                        bill.due_date = transaction.transaction_date
                        bill.category_id = transaction.category_id
                        bill.account_id = transaction.account_id
                        await self.bill_repository.update(bill)
                        print(f"[DEBUG] Bill {bill.id} atualizada para PENDING e sincronizada com transação {transaction.id}")
                    else:
                        # Se não existe bill, criar uma pendente
                        bill = Bill(
                            name=transaction.description,
                            description=transaction.notes,
                            bill_type=BillType.EXPENSE,
                            amount=transaction.amount,
                            due_date=transaction.transaction_date,
                            status=BillStatus.PENDING,
                            is_recurring=False,
                            recurrence_type=RecurrenceType.NONE,
                            user_id=transaction.user_id,
                            account_id=transaction.account_id,
                            category_id=transaction.category_id,
                            transaction_id=transaction.id,
                        )
                        await self.bill_repository.create(bill)
                        print(f"[DEBUG] Bill criada como pendente para transação {transaction.id}")
                
                elif transaction.status == TransactionStatus.CANCELLED:
                    # Transação foi cancelada -> cancelar bill
                    if bill:
                        bill.status = BillStatus.CANCELLED
                        # Ainda sincronizar campos mesmo quando cancelada
                        bill.name = transaction.description
                        bill.description = transaction.notes
                        bill.amount = transaction.amount
                        bill.due_date = transaction.transaction_date
                        bill.category_id = transaction.category_id
                        bill.account_id = transaction.account_id
                        await self.bill_repository.update(bill)
                        print(f"[DEBUG] Bill {bill.id} cancelada e sincronizada com transação {transaction.id}")
                
                # Se a bill existe e houve mudanças em campos (mas status não mudou), sincronizar
                elif bill and bill_needs_update:
                    # Sincronizar todos os campos mantendo o status atual
                    bill.name = transaction.description
                    bill.description = transaction.notes
                    bill.amount = transaction.amount
                    bill.due_date = transaction.transaction_date
                    bill.category_id = transaction.category_id
                    bill.account_id = transaction.account_id
                    await self.bill_repository.update(bill)
                    print(f"[DEBUG] Bill {bill.id} sincronizada com transação {transaction.id} (campos atualizados, status mantido: {bill.status})")
                    
            except Exception as e:
                print(f"[ERROR] Erro ao atualizar bill associada: {e}")
                import traceback
                traceback.print_exc()
                # Não falhar a atualização da transação se a bill falhar

        # Atualizar saldo da conta se necessário
        if old_status == TransactionStatus.COMPLETED:
            if transaction.transaction_type == TransactionType.INCOME:
                account.balance -= old_amount
            elif transaction.transaction_type == TransactionType.EXPENSE:
                account.balance += old_amount

        if transaction.status == TransactionStatus.COMPLETED:
            if transaction.transaction_type == TransactionType.INCOME:
                account.balance += transaction.amount
            elif transaction.transaction_type == TransactionType.EXPENSE:
                account.balance -= transaction.amount

        await self.account_repository.update(account)

        return transaction

    async def delete_transaction(self, transaction_id: UUID) -> bool:
        """Deleta uma transação"""
        transaction = await self.get_transaction(transaction_id)
        
        # Cancelar bill associada se for uma despesa
        if (transaction.transaction_type == TransactionType.EXPENSE and 
            self.bill_repository):
            try:
                bill = await self.bill_repository.get_by_transaction_id(transaction_id)
                if bill:
                    bill.status = BillStatus.CANCELLED
                    await self.bill_repository.update(bill)
                    print(f"[DEBUG] Bill {bill.id} cancelada (transação {transaction_id} deletada)")
            except Exception as e:
                print(f"[ERROR] Erro ao cancelar bill associada: {e}")
                import traceback
                traceback.print_exc()
        
        # Reverter saldo da conta se necessário
        if transaction.status == TransactionStatus.COMPLETED:
            account = await self.account_repository.get_by_id(transaction.account_id)
            if transaction.transaction_type == TransactionType.INCOME:
                account.balance -= transaction.amount
            elif transaction.transaction_type == TransactionType.EXPENSE:
                account.balance += transaction.amount
            await self.account_repository.update(account)

        return await self.transaction_repository.delete(transaction_id)

    async def search_transactions(
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
        """Busca avançada de transações"""
        return await self.transaction_repository.search(
            user_id=user_id,
            search_text=search_text,
            transaction_type=transaction_type,
            category_id=category_id,
            account_id=account_id,
            workspace_id=workspace_id,
            min_amount=min_amount,
            max_amount=max_amount,
            start_date=start_date,
            end_date=end_date,
            status=status,
            limit=limit,
            offset=offset,
            order_by=order_by,
            order_direction=order_direction,
        )

