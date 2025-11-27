from typing import List, Optional
from uuid import UUID
from decimal import Decimal
from src.domain.repositories.account_repository import AccountRepository
from src.infrastructure.database.models.account import Account, AccountType
from src.shared.exceptions import NotFoundException, ValidationException


class AccountUseCases:
    """Casos de uso para gerenciamento de contas"""

    def __init__(self, account_repository: AccountRepository):
        self.account_repository = account_repository

    async def create_account(
        self,
        name: str,
        account_type: str,
        user_id: UUID,
        initial_balance: Decimal = Decimal("0"),
        description: Optional[str] = None,
        currency: str = "BRL",
        bank_name: Optional[str] = None,
        account_number: Optional[str] = None,
        family_id: Optional[UUID] = None,
        workspace_id: Optional[UUID] = None,
    ) -> Account:
        """Cria uma nova conta"""
        # Validar tipo de conta
        try:
            AccountType(account_type)
        except ValueError:
            raise ValidationException(f"Tipo de conta inválido: {account_type}")

        account = Account(
            name=name,
            description=description,
            account_type=AccountType(account_type),
            balance=initial_balance,
            initial_balance=initial_balance,
            currency=currency,
            bank_name=bank_name,
            account_number=account_number,
            owner_id=user_id,
            family_id=family_id,
            workspace_id=workspace_id,
            is_active=True,
        )

        return await self.account_repository.create(account)

    async def get_account(self, account_id: UUID) -> Account:
        """Obtém uma conta por ID"""
        account = await self.account_repository.get_by_id(account_id)
        if not account:
            raise NotFoundException("Conta", str(account_id))
        return account

    async def get_user_accounts(self, user_id: UUID) -> List[Account]:
        """Obtém todas as contas de um usuário"""
        return await self.account_repository.get_by_user_id(user_id)

    async def update_account(
        self,
        account_id: UUID,
        name: Optional[str] = None,
        description: Optional[str] = None,
        bank_name: Optional[str] = None,
        account_number: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> Account:
        """Atualiza uma conta"""
        account = await self.get_account(account_id)

        if name:
            account.name = name
        if description is not None:
            account.description = description
        if bank_name is not None:
            account.bank_name = bank_name
        if account_number is not None:
            account.account_number = account_number
        if is_active is not None:
            account.is_active = is_active

        return await self.account_repository.update(account)

    async def delete_account(self, account_id: UUID) -> bool:
        """Deleta uma conta (soft delete)"""
        account = await self.get_account(account_id)
        return await self.account_repository.delete(account_id)

