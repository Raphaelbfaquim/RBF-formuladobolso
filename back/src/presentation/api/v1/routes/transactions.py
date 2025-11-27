from fastapi import APIRouter, Depends, Query, status
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from src.infrastructure.database.base import get_db
from src.presentation.schemas.transaction import (
    TransactionCreate,
    TransactionUpdate,
    TransactionResponse,
)
from src.presentation.schemas.transaction_filter import TransactionFilter
from src.presentation.api.dependencies import get_current_active_user
from src.domain.repositories.transaction_repository import TransactionRepository
from src.domain.repositories.account_repository import AccountRepository
from src.domain.repositories.bill_repository import BillRepository
from src.domain.repositories.goal_repository import GoalRepository, GoalContributionRepository
from src.domain.repositories.calendar_repository import CalendarEventRepository
from src.domain.repositories.gamification_repository import (
    BadgeRepository,
    UserBadgeRepository,
    UserLevelRepository,
    ChallengeRepository,
    UserChallengeRepository,
)
from src.infrastructure.repositories.transaction_repository import SQLAlchemyTransactionRepository
from src.infrastructure.repositories.account_repository import SQLAlchemyAccountRepository
from src.infrastructure.repositories.bill_repository import SQLAlchemyBillRepository
from src.infrastructure.repositories.goal_repository import SQLAlchemyGoalRepository, SQLAlchemyGoalContributionRepository
from src.infrastructure.repositories.calendar_repository import SQLAlchemyCalendarEventRepository
from src.infrastructure.repositories.gamification_repository import (
    SQLAlchemyBadgeRepository,
    SQLAlchemyUserBadgeRepository,
    SQLAlchemyUserLevelRepository,
    SQLAlchemyChallengeRepository,
    SQLAlchemyUserChallengeRepository,
)
from src.application.use_cases.transaction_use_cases import TransactionUseCases
from src.application.services.gamification_service import GamificationService
from src.infrastructure.database.base import get_db
from src.infrastructure.database.models.user import User
from src.infrastructure.database.models.bill import BillStatus
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


def get_transaction_repository(db: AsyncSession = Depends(get_db)) -> TransactionRepository:
    return SQLAlchemyTransactionRepository(db)


def get_account_repository(db: AsyncSession = Depends(get_db)) -> AccountRepository:
    return SQLAlchemyAccountRepository(db)


def get_bill_repository(db: AsyncSession = Depends(get_db)) -> BillRepository:
    return SQLAlchemyBillRepository(db)


def get_goal_repository(db: AsyncSession = Depends(get_db)) -> GoalRepository:
    return SQLAlchemyGoalRepository(db)


def get_goal_contribution_repository(db: AsyncSession = Depends(get_db)) -> GoalContributionRepository:
    return SQLAlchemyGoalContributionRepository(db)


def get_calendar_event_repository(db: AsyncSession = Depends(get_db)) -> CalendarEventRepository:
    return SQLAlchemyCalendarEventRepository(db)


def get_badge_repository(db: AsyncSession = Depends(get_db)) -> BadgeRepository:
    return SQLAlchemyBadgeRepository(db)


def get_user_badge_repository(db: AsyncSession = Depends(get_db)) -> UserBadgeRepository:
    return SQLAlchemyUserBadgeRepository(db)


def get_user_level_repository(db: AsyncSession = Depends(get_db)) -> UserLevelRepository:
    return SQLAlchemyUserLevelRepository(db)


def get_challenge_repository(db: AsyncSession = Depends(get_db)) -> ChallengeRepository:
    return SQLAlchemyChallengeRepository(db)


def get_user_challenge_repository(db: AsyncSession = Depends(get_db)) -> UserChallengeRepository:
    return SQLAlchemyUserChallengeRepository(db)


def get_gamification_service(
    badge_repo: BadgeRepository = Depends(get_badge_repository),
    user_badge_repo: UserBadgeRepository = Depends(get_user_badge_repository),
    user_level_repo: UserLevelRepository = Depends(get_user_level_repository),
    challenge_repo: ChallengeRepository = Depends(get_challenge_repository),
    user_challenge_repo: UserChallengeRepository = Depends(get_user_challenge_repository),
    transaction_repo: TransactionRepository = Depends(get_transaction_repository),
    goal_repo: GoalRepository = Depends(get_goal_repository),
) -> GamificationService:
    return GamificationService(
        badge_repo,
        user_badge_repo,
        user_level_repo,
        challenge_repo,
        user_challenge_repo,
        transaction_repo,
        goal_repo,
    )


def get_transaction_use_cases(
    transaction_repository: TransactionRepository = Depends(get_transaction_repository),
    account_repository: AccountRepository = Depends(get_account_repository),
    bill_repository: BillRepository = Depends(get_bill_repository),
    goal_repository: GoalRepository = Depends(get_goal_repository),
    goal_contribution_repository: GoalContributionRepository = Depends(get_goal_contribution_repository),
    calendar_event_repository: CalendarEventRepository = Depends(get_calendar_event_repository),
    gamification_service: GamificationService = Depends(get_gamification_service),
) -> TransactionUseCases:
    return TransactionUseCases(
        transaction_repository, 
        account_repository, 
        bill_repository,
        goal_repository,
        goal_contribution_repository,
        calendar_event_repository,
        gamification_service
    )


@router.post("/", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    transaction_data: TransactionCreate,
    use_cases: TransactionUseCases = Depends(get_transaction_use_cases),
    current_user: User = Depends(get_current_active_user),
):
    """Cria uma nova transação"""
    transaction = await use_cases.create_transaction(
        description=transaction_data.description,
        amount=transaction_data.amount,
        transaction_type=transaction_data.transaction_type,
        transaction_date=transaction_data.transaction_date,
        user_id=current_user.id,
        account_id=transaction_data.account_id,
        category_id=transaction_data.category_id,
        receipt_id=transaction_data.receipt_id,
        status=transaction_data.status,
        notes=transaction_data.notes,
        workspace_id=getattr(transaction_data, 'workspace_id', None),
    )
    return transaction


@router.get("/")
async def list_transactions(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    limit: int = Query(100, ge=1, le=500, description="Número máximo de transações a retornar"),
    offset: int = Query(0, ge=0, description="Offset para paginação"),
    use_cases: TransactionUseCases = Depends(get_transaction_use_cases),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Lista transações do usuário e da família (se aplicável) com paginação"""
    import pytz
    from src.infrastructure.repositories.family_repository import SQLAlchemyFamilyRepository, SQLAlchemyFamilyMemberRepository
    from src.infrastructure.repositories.account_repository import SQLAlchemyAccountRepository
    from src.infrastructure.repositories.family_permission_repository import SQLAlchemyFamilyPermissionRepository
    from src.infrastructure.database.models.family_permission import ModulePermission
    
    # Normalizar timezone das datas recebidas
    if start_date:
        if start_date.tzinfo is None:
            start_date = pytz.UTC.localize(start_date)
        else:
            start_date = start_date.astimezone(pytz.UTC)
    
    if end_date:
        if end_date.tzinfo is None:
            end_date = pytz.UTC.localize(end_date)
        else:
            end_date = end_date.astimezone(pytz.UTC)
        from datetime import timedelta
        end_date = end_date.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    # Buscar transações do usuário
    user_transactions = await use_cases.get_user_transactions(
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date,
    )
    
    # Verificar se usuário está em alguma família e tem permissão para ver transações
    try:
        from sqlalchemy import select, text
        family_repo = SQLAlchemyFamilyRepository(db)
        member_repo = SQLAlchemyFamilyMemberRepository(db)
        account_repo = SQLAlchemyAccountRepository(db)
        permission_repo = SQLAlchemyFamilyPermissionRepository(db)
        
        families = await family_repo.get_by_user_id(current_user.id)
        all_transactions = list(user_transactions)  # Começar com transações do usuário
        
        # Para cada família, buscar transações se tiver permissão
        for family in families:
            try:
                member = await member_repo.get_member_in_family(current_user.id, family.id)
                if member:
                    # Verificar permissão para ver transações
                    permission = await permission_repo.get_by_family_member_and_module(
                        member.id, ModulePermission.TRANSACTIONS
                    )
                    if permission and permission.can_view:
                        # Buscar todas as contas da família (com family_id)
                        family_accounts = await account_repo.get_by_family_id(family.id)
                        family_account_ids = {acc.id for acc in family_accounts}
                        
                        # Buscar user_ids dos membros da família usando SQL direto (evita greenlet error)
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
                                    family_account_ids.add(acc.id)
                            except Exception as e:
                                print(f"⚠️ Erro ao buscar contas do membro {member_user_id}: {e}")
                                continue
                        
                        # Buscar transações dessas contas
                        for account_id in family_account_ids:
                            try:
                                account_transactions = await use_cases.transaction_repository.get_by_account_id(
                                    account_id, start_date, end_date
                                )
                                # Adicionar apenas transações que ainda não estão na lista
                                existing_ids = {t.id for t in all_transactions}
                                for trans in account_transactions:
                                    if trans.id not in existing_ids:
                                        all_transactions.append(trans)
                                        existing_ids.add(trans.id)
                            except Exception as e:
                                print(f"⚠️ Erro ao buscar transações da conta {account_id}: {e}")
                                continue
            except Exception as e:
                print(f"⚠️ Erro ao processar família {family.id}: {e}")
                continue
    except Exception as e:
        print(f"⚠️ Erro ao buscar dados da família: {e}")
        import traceback
        traceback.print_exc()
    
    # Aplicar paginação antes de processar (otimização para grandes volumes)
    total_count = len(all_transactions)
    transactions = all_transactions[offset:offset + limit]
    
    # Buscar categorias de todas as transações usando SQL direto (evita lazy loading)
    category_ids = {t.category_id for t in transactions if t.category_id}
    categories_dict = {}
    if category_ids:
        try:
            from sqlalchemy import text
            category_result = await db.execute(
                text("SELECT id, name, category_type FROM categories WHERE id = ANY(:category_ids)"),
                {"category_ids": [str(cid) for cid in category_ids]}
            )
            for row in category_result.fetchall():
                categories_dict[row[0]] = {
                    "id": row[0],
                    "name": row[1],
                    "category_type": row[2],
                }
        except Exception as e:
            print(f"⚠️ Erro ao buscar categorias: {e}")
    
    # Incluir informações da categoria na resposta
    result = []
    for transaction in transactions:
        transaction_dict = {
            "id": transaction.id,
            "description": transaction.description,
            "amount": transaction.amount,
            "transaction_type": transaction.transaction_type.value,
            "transaction_date": transaction.transaction_date,
            "status": transaction.status.value,
            "notes": transaction.notes,
            "user_id": transaction.user_id,
            "account_id": transaction.account_id,
            "category_id": transaction.category_id,
            "receipt_id": transaction.receipt_id,
            "created_at": transaction.transaction_date,
            "updated_at": transaction.updated_at,
        }
        
        # Incluir nome da categoria se existir (usando o dicionário em vez de lazy loading)
        if transaction.category_id and transaction.category_id in categories_dict:
            transaction_dict["category"] = categories_dict[transaction.category_id]
        
        result.append(transaction_dict)
    
    # Retornar com metadados de paginação
    return {
        "transactions": result,
        "total": total_count,
        "limit": limit,
        "offset": offset,
        "has_more": (offset + limit) < total_count
    }


@router.post("/search")
async def search_transactions(
    filters: TransactionFilter,
    use_cases: TransactionUseCases = Depends(get_transaction_use_cases),
    current_user: User = Depends(get_current_active_user),
):
    """Busca avançada de transações com filtros múltiplos"""
    transactions, total = await use_cases.search_transactions(
        user_id=current_user.id,
        search_text=filters.search_text,
        transaction_type=filters.transaction_type,
        category_id=filters.category_id,
        account_id=filters.account_id,
        workspace_id=filters.workspace_id,
        min_amount=float(filters.min_amount) if filters.min_amount else None,
        max_amount=float(filters.max_amount) if filters.max_amount else None,
        start_date=filters.start_date,
        end_date=filters.end_date,
        status=filters.status,
        limit=filters.page_size,
        offset=(filters.page - 1) * filters.page_size,
        order_by=filters.order_by,
        order_direction=filters.order_direction,
    )
    
    total_pages = (total + filters.page_size - 1) // filters.page_size
    
    return {
        "transactions": transactions,
        "total": total,
        "page": filters.page,
        "page_size": filters.page_size,
        "total_pages": total_pages,
    }


@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(
    transaction_id: UUID,
    use_cases: TransactionUseCases = Depends(get_transaction_use_cases),
    current_user: User = Depends(get_current_active_user),
):
    """Obtém uma transação específica"""
    transaction = await use_cases.get_transaction(transaction_id)
    return transaction


@router.put("/{transaction_id}", response_model=TransactionResponse)
async def update_transaction(
    transaction_id: UUID,
    transaction_update: TransactionUpdate,
    use_cases: TransactionUseCases = Depends(get_transaction_use_cases),
    current_user: User = Depends(get_current_active_user),
):
    """Atualiza uma transação"""
    transaction = await use_cases.update_transaction(
        transaction_id=transaction_id,
        description=transaction_update.description,
        amount=transaction_update.amount,
        transaction_date=transaction_update.transaction_date,
        status=transaction_update.status,
        category_id=transaction_update.category_id,
        notes=transaction_update.notes,
    )
    return transaction


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction(
    transaction_id: UUID,
    use_cases: TransactionUseCases = Depends(get_transaction_use_cases),
    current_user: User = Depends(get_current_active_user),
):
    """Deleta uma transação"""
    await use_cases.delete_transaction(transaction_id)
    return None
