from typing import List, Optional, Dict
from uuid import UUID
from datetime import datetime, timedelta
from decimal import Decimal
import pytz
from src.domain.repositories.investment_repository import (
    InvestmentAccountRepository,
    InvestmentTransactionRepository,
)
from src.infrastructure.database.models.investment import (
    InvestmentAccount,
    InvestmentTransaction,
    InvestmentAccountType,
    InvestmentType,
    InvestmentTransactionType,
)
from src.shared.exceptions import NotFoundException, ValidationException


class InvestmentUseCases:
    """Casos de uso para investimentos"""

    def __init__(
        self,
        account_repository: InvestmentAccountRepository,
        transaction_repository: InvestmentTransactionRepository,
    ):
        self.account_repository = account_repository
        self.transaction_repository = transaction_repository

    # ========== Investment Account Use Cases ==========

    async def create_investment_account(
        self,
        user_id: UUID,
        name: str,
        account_type: str,
        description: Optional[str] = None,
        institution_name: Optional[str] = None,
        account_number: Optional[str] = None,
        initial_balance: Decimal = Decimal("0"),
        currency: str = "BRL",
    ) -> InvestmentAccount:
        """Cria uma nova conta de investimento"""
        try:
            account_type_enum = InvestmentAccountType(account_type)
        except ValueError:
            raise ValidationException(f"Tipo de conta inválido: {account_type}")

        account = InvestmentAccount(
            user_id=user_id,
            name=name,
            description=description,
            account_type=account_type_enum,
            institution_name=institution_name,
            account_number=account_number,
            initial_balance=initial_balance,
            current_balance=initial_balance,
            currency=currency,
            is_active=True,
        )

        return await self.account_repository.create(account)

    async def get_investment_account(
        self, account_id: UUID, user_id: UUID
    ) -> InvestmentAccount:
        """Obtém uma conta de investimento"""
        account = await self.account_repository.get_by_id(account_id)
        if not account or account.user_id != user_id:
            raise NotFoundException("Conta de investimento não encontrada")
        return account

    async def get_user_investment_accounts(self, user_id: UUID) -> List[InvestmentAccount]:
        """Lista todas as contas de investimento do usuário"""
        return await self.account_repository.get_by_user_id(user_id)

    async def update_investment_account(
        self,
        account_id: UUID,
        user_id: UUID,
        name: Optional[str] = None,
        description: Optional[str] = None,
        account_type: Optional[str] = None,
        institution_name: Optional[str] = None,
        account_number: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> InvestmentAccount:
        """Atualiza uma conta de investimento"""
        account = await self.get_investment_account(account_id, user_id)

        if name is not None:
            account.name = name
        if description is not None:
            account.description = description
        if account_type is not None:
            try:
                account.account_type = InvestmentAccountType(account_type)
            except ValueError:
                raise ValidationException(f"Tipo de conta inválido: {account_type}")
        if institution_name is not None:
            account.institution_name = institution_name
        if account_number is not None:
            account.account_number = account_number
        if is_active is not None:
            account.is_active = is_active

        return await self.account_repository.update(account)

    async def delete_investment_account(self, account_id: UUID, user_id: UUID) -> bool:
        """Deleta uma conta de investimento"""
        account = await self.get_investment_account(account_id, user_id)
        return await self.account_repository.delete(account_id)

    # ========== Investment Transaction Use Cases ==========

    async def create_investment_transaction(
        self,
        account_id: UUID,
        user_id: UUID,
        investment_type: str,
        transaction_type: str,
        quantity: Decimal,
        unit_price: Decimal,
        total_amount: Decimal,
        transaction_date: datetime,
        symbol: Optional[str] = None,
        fees: Decimal = Decimal("0"),
        notes: Optional[str] = None,
    ) -> InvestmentTransaction:
        """Cria uma nova transação de investimento"""
        # Verificar se a conta pertence ao usuário
        account = await self.get_investment_account(account_id, user_id)

        try:
            investment_type_enum = InvestmentType(investment_type)
            transaction_type_enum = InvestmentTransactionType(transaction_type)
        except ValueError as e:
            raise ValidationException(f"Tipo inválido: {e}")

        # Garantir timezone
        if transaction_date.tzinfo is None:
            transaction_date = pytz.UTC.localize(transaction_date)
        else:
            transaction_date = transaction_date.astimezone(pytz.UTC)

        transaction = InvestmentTransaction(
            account_id=account_id,
            investment_type=investment_type_enum,
            transaction_type=transaction_type_enum,
            symbol=symbol,
            quantity=quantity,
            unit_price=unit_price,
            total_amount=total_amount,
            fees=fees,
            transaction_date=transaction_date,
            notes=notes,
        )

        # Atualizar saldo da conta baseado no tipo de transação
        if transaction_type_enum == InvestmentTransactionType.BUY:
            account.current_balance -= (total_amount + fees)
        elif transaction_type_enum == InvestmentTransactionType.SELL:
            account.current_balance += (total_amount - fees)
        elif transaction_type_enum in [InvestmentTransactionType.DIVIDEND, InvestmentTransactionType.INTEREST]:
            account.current_balance += total_amount
        elif transaction_type_enum == InvestmentTransactionType.FEE:
            account.current_balance -= total_amount

        await self.account_repository.update(account)
        return await self.transaction_repository.create(transaction)

    async def get_investment_transaction(
        self, transaction_id: UUID, user_id: UUID
    ) -> InvestmentTransaction:
        """Obtém uma transação de investimento"""
        transaction = await self.transaction_repository.get_by_id(transaction_id)
        if not transaction:
            raise NotFoundException("Transação não encontrada")

        # Verificar se a conta pertence ao usuário
        if transaction.account.user_id != user_id:
            raise NotFoundException("Transação não encontrada")

        return transaction

    async def get_account_transactions(
        self,
        account_id: UUID,
        user_id: UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[InvestmentTransaction]:
        """Lista transações de uma conta"""
        await self.get_investment_account(account_id, user_id)  # Verifica permissão
        return await self.transaction_repository.get_by_account_id(
            account_id, start_date, end_date
        )

    async def get_user_transactions(
        self,
        user_id: UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[InvestmentTransaction]:
        """Lista todas as transações do usuário"""
        return await self.transaction_repository.get_by_user_id(
            user_id, start_date, end_date
        )

    async def update_investment_transaction(
        self,
        transaction_id: UUID,
        user_id: UUID,
        investment_type: Optional[str] = None,
        transaction_type: Optional[str] = None,
        symbol: Optional[str] = None,
        quantity: Optional[Decimal] = None,
        unit_price: Optional[Decimal] = None,
        total_amount: Optional[Decimal] = None,
        fees: Optional[Decimal] = None,
        transaction_date: Optional[datetime] = None,
        notes: Optional[str] = None,
    ) -> InvestmentTransaction:
        """Atualiza uma transação de investimento"""
        transaction = await self.get_investment_transaction(transaction_id, user_id)

        if investment_type is not None:
            try:
                transaction.investment_type = InvestmentType(investment_type)
            except ValueError:
                raise ValidationException(f"Tipo de investimento inválido: {investment_type}")
        if transaction_type is not None:
            try:
                transaction.transaction_type = InvestmentTransactionType(transaction_type)
            except ValueError:
                raise ValidationException(f"Tipo de transação inválido: {transaction_type}")
        if symbol is not None:
            transaction.symbol = symbol
        if quantity is not None:
            transaction.quantity = quantity
        if unit_price is not None:
            transaction.unit_price = unit_price
        if total_amount is not None:
            transaction.total_amount = total_amount
        if fees is not None:
            transaction.fees = fees
        if transaction_date is not None:
            if transaction_date.tzinfo is None:
                transaction_date = pytz.UTC.localize(transaction_date)
            else:
                transaction_date = transaction_date.astimezone(pytz.UTC)
            transaction.transaction_date = transaction_date
        if notes is not None:
            transaction.notes = notes

        return await self.transaction_repository.update(transaction)

    async def delete_investment_transaction(
        self, transaction_id: UUID, user_id: UUID
    ) -> bool:
        """Deleta uma transação de investimento"""
        await self.get_investment_transaction(transaction_id, user_id)  # Verifica permissão
        return await self.transaction_repository.delete(transaction_id)


