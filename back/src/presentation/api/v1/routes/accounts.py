from fastapi import APIRouter, Depends, status
from typing import List
from uuid import UUID
from src.presentation.schemas.account import AccountCreate, AccountUpdate, AccountResponse
from src.presentation.api.dependencies import get_current_active_user
from src.domain.repositories.account_repository import AccountRepository
from src.infrastructure.repositories.account_repository import SQLAlchemyAccountRepository
from src.infrastructure.repositories.family_repository import SQLAlchemyFamilyRepository, SQLAlchemyFamilyMemberRepository
from src.infrastructure.repositories.family_permission_repository import SQLAlchemyFamilyPermissionRepository
from src.infrastructure.database.models.family_permission import ModulePermission
from src.application.use_cases.account_use_cases import AccountUseCases
from src.infrastructure.database.base import get_db
from src.infrastructure.database.models.user import User
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


def get_account_repository(db: AsyncSession = Depends(get_db)) -> AccountRepository:
    return SQLAlchemyAccountRepository(db)


def get_account_use_cases(
    account_repository: AccountRepository = Depends(get_account_repository),
) -> AccountUseCases:
    return AccountUseCases(account_repository)


@router.post("/", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
async def create_account(
    account_data: AccountCreate,
    use_cases: AccountUseCases = Depends(get_account_use_cases),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Cria uma nova conta"""
    from src.infrastructure.repositories.family_repository import SQLAlchemyFamilyRepository, SQLAlchemyFamilyMemberRepository
    
    # Se não foi especificado family_id, buscar a família do usuário
    family_id = getattr(account_data, 'family_id', None)
    if not family_id:
        try:
            family_repo = SQLAlchemyFamilyRepository(db)
            member_repo = SQLAlchemyFamilyMemberRepository(db)
            families = await family_repo.get_by_user_id(current_user.id)
            # Se o usuário está em uma família, usar a primeira (ou pode escolher qual usar)
            if families:
                family_id = families[0].id
        except Exception as e:
            print(f"⚠️ Erro ao buscar família do usuário: {e}")
    
    account = await use_cases.create_account(
        name=account_data.name,
        account_type=account_data.account_type,
        user_id=current_user.id,
        initial_balance=account_data.initial_balance,
        description=account_data.description,
        currency=account_data.currency,
        bank_name=account_data.bank_name,
        account_number=account_data.account_number,
        family_id=family_id,
        workspace_id=getattr(account_data, 'workspace_id', None),
    )
    return account


@router.get("/", response_model=List[AccountResponse])
async def list_accounts(
    use_cases: AccountUseCases = Depends(get_account_use_cases),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Lista todas as contas do usuário e da família (se aplicável)"""
    # Buscar contas do usuário
    user_accounts = await use_cases.get_user_accounts(current_user.id)
    all_accounts = list(user_accounts)  # Começar com contas do usuário
    
    # Verificar se usuário está em alguma família e tem permissão para ver contas
    family_repo = SQLAlchemyFamilyRepository(db)
    member_repo = SQLAlchemyFamilyMemberRepository(db)
    account_repo = SQLAlchemyAccountRepository(db)
    permission_repo = SQLAlchemyFamilyPermissionRepository(db)
    
    families = await family_repo.get_by_user_id(current_user.id)
    
    # Para cada família, buscar contas se tiver permissão
    for family in families:
        member = await member_repo.get_member_in_family(current_user.id, family.id)
        if member:
            # Verificar permissão para ver contas
            permission = await permission_repo.get_by_family_member_and_module(
                member.id, ModulePermission.ACCOUNTS
            )
            if permission and permission.can_view:
                # Buscar todas as contas da família (com family_id)
                family_accounts = await account_repo.get_by_family_id(family.id)
                existing_ids = {acc.id for acc in family_accounts}
                
                # Buscar user_ids dos membros da família usando SQL direto (evita greenlet error)
                from sqlalchemy import text
                result = await db.execute(
                    text("SELECT user_id FROM family_members WHERE family_id = :family_id"),
                    {"family_id": str(family.id)}
                )
                member_user_ids = [row[0] for row in result.fetchall()]
                
                # Buscar contas de cada membro
                for member_user_id in member_user_ids:
                    try:
                        member_accounts = await account_repo.get_by_user_id(member_user_id)
                        for acc in member_accounts:
                            if acc.id not in existing_ids:
                                family_accounts.append(acc)
                                existing_ids.add(acc.id)
                    except Exception as e:
                        print(f"⚠️ Erro ao buscar contas do membro {member_user_id}: {e}")
                        continue
                
                # Adicionar apenas contas que ainda não estão na lista
                for acc in family_accounts:
                    if acc.id not in {a.id for a in all_accounts}:
                        all_accounts.append(acc)
    
    return all_accounts


@router.get("/{account_id}", response_model=AccountResponse)
async def get_account(
    account_id: UUID,
    use_cases: AccountUseCases = Depends(get_account_use_cases),
    current_user: User = Depends(get_current_active_user),
):
    """Obtém uma conta específica"""
    account = await use_cases.get_account(account_id)
    return account


@router.put("/{account_id}", response_model=AccountResponse)
async def update_account(
    account_id: UUID,
    account_update: AccountUpdate,
    use_cases: AccountUseCases = Depends(get_account_use_cases),
    current_user: User = Depends(get_current_active_user),
):
    """Atualiza uma conta"""
    account = await use_cases.update_account(
        account_id=account_id,
        name=account_update.name,
        description=account_update.description,
        bank_name=account_update.bank_name,
        account_number=account_update.account_number,
        is_active=account_update.is_active,
    )
    return account


@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(
    account_id: UUID,
    use_cases: AccountUseCases = Depends(get_account_use_cases),
    current_user: User = Depends(get_current_active_user),
):
    """Deleta uma conta"""
    await use_cases.delete_account(account_id)
    return None
