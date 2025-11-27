from typing import List, Optional
from uuid import UUID
from datetime import datetime
from decimal import Decimal
from src.domain.repositories.transfer_repository import TransferRepository
from src.domain.repositories.account_repository import AccountRepository
from src.domain.repositories.transaction_repository import TransactionRepository
from src.infrastructure.database.models.transfer import Transfer, TransferStatus
from src.infrastructure.database.models.transaction import Transaction, TransactionType, TransactionStatus
from src.shared.exceptions import NotFoundException, ValidationException


class TransferUseCases:
    """Casos de uso para transferências entre contas"""

    def __init__(
        self,
        transfer_repository: TransferRepository,
        account_repository: AccountRepository,
        transaction_repository: TransactionRepository,
    ):
        self.transfer_repository = transfer_repository
        self.account_repository = account_repository
        self.transaction_repository = transaction_repository

    async def create_transfer(
        self,
        from_account_id: UUID,
        to_account_id: UUID,
        amount: Decimal,
        user_id: UUID,
        transfer_date: datetime,
        description: Optional[str] = None,
        workspace_id: Optional[UUID] = None,
        scheduled_date: Optional[datetime] = None,
        notes: Optional[str] = None,
    ) -> Transfer:
        """Cria uma transferência entre contas"""
        # Validar contas
        from_account = await self.account_repository.get_by_id(from_account_id)
        to_account = await self.account_repository.get_by_id(to_account_id)
        
        if not from_account:
            raise NotFoundException("Conta de origem", str(from_account_id))
        if not to_account:
            raise NotFoundException("Conta de destino", str(to_account_id))
        
        if from_account_id == to_account_id:
            raise ValidationException("Não é possível transferir para a mesma conta")
        
        # Verificar saldo se não for agendada
        if not scheduled_date and from_account.balance < amount:
            raise ValidationException("Saldo insuficiente na conta de origem")
        
        # Criar transferência
        transfer = Transfer(
            description=description or f"Transferência de {from_account.name} para {to_account.name}",
            amount=amount,
            status=TransferStatus.PENDING if scheduled_date else TransferStatus.COMPLETED,
            transfer_date=transfer_date,
            scheduled_date=scheduled_date,
            notes=notes,
            from_account_id=from_account_id,
            to_account_id=to_account_id,
            user_id=user_id,
            workspace_id=workspace_id,
        )
        
        transfer = await self.transfer_repository.create(transfer)
        
        # Se não for agendada, executar imediatamente
        if not scheduled_date:
            await self._execute_transfer(transfer, from_account, to_account)
        
        return transfer

    async def _execute_transfer(self, transfer: Transfer, from_account, to_account):
        """Executa a transferência criando as transações"""
        # Criar transação de saída
        from_transaction = Transaction(
            description=f"Transferência para {to_account.name}",
            amount=transfer.amount,
            transaction_type=TransactionType.EXPENSE,
            status=TransactionStatus.COMPLETED,
            transaction_date=transfer.transfer_date,
            user_id=transfer.user_id,
            account_id=transfer.from_account_id,
            workspace_id=transfer.workspace_id,
            notes=transfer.notes,
        )
        from_transaction = await self.transaction_repository.create(from_transaction)
        
        # Criar transação de entrada
        to_transaction = Transaction(
            description=f"Transferência de {from_account.name}",
            amount=transfer.amount,
            transaction_type=TransactionType.INCOME,
            status=TransactionStatus.COMPLETED,
            transaction_date=transfer.transfer_date,
            user_id=transfer.user_id,
            account_id=transfer.to_account_id,
            workspace_id=transfer.workspace_id,
            notes=transfer.notes,
        )
        to_transaction = await self.transaction_repository.create(to_transaction)
        
        # Atualizar saldos
        from_account.balance -= transfer.amount
        to_account.balance += transfer.amount
        
        await self.account_repository.update(from_account)
        await self.account_repository.update(to_account)
        
        # Atualizar transferência com IDs das transações
        transfer.from_transaction_id = from_transaction.id
        transfer.to_transaction_id = to_transaction.id
        transfer.status = TransferStatus.COMPLETED
        await self.transfer_repository.update(transfer)

    async def get_transfer(self, transfer_id: UUID) -> Transfer:
        """Obtém uma transferência por ID"""
        transfer = await self.transfer_repository.get_by_id(transfer_id)
        if not transfer:
            raise NotFoundException("Transferência", str(transfer_id))
        return transfer

    async def get_user_transfers(
        self,
        user_id: UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[Transfer]:
        """Obtém transferências de um usuário"""
        return await self.transfer_repository.get_by_user_id(user_id, start_date, end_date)

    async def cancel_transfer(self, transfer_id: UUID) -> Transfer:
        """Cancela uma transferência"""
        transfer = await self.get_transfer(transfer_id)
        
        if transfer.status == TransferStatus.COMPLETED:
            # Reverter transferência
            from_account = await self.account_repository.get_by_id(transfer.from_account_id)
            to_account = await self.account_repository.get_by_id(transfer.to_account_id)
            
            # Reverter saldos
            from_account.balance += transfer.amount
            to_account.balance -= transfer.amount
            
            await self.account_repository.update(from_account)
            await self.account_repository.update(to_account)
            
            # Cancelar transações
            if transfer.from_transaction_id:
                from_trans = await self.transaction_repository.get_by_id(transfer.from_transaction_id)
                if from_trans:
                    await self.transaction_repository.delete(from_trans.id)
            
            if transfer.to_transaction_id:
                to_trans = await self.transaction_repository.get_by_id(transfer.to_transaction_id)
                if to_trans:
                    await self.transaction_repository.delete(to_trans.id)
        
        transfer.status = TransferStatus.CANCELLED
        return await self.transfer_repository.update(transfer)

