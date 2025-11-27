from fastapi import APIRouter, Depends, status
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from src.presentation.api.dependencies import get_current_active_user
from src.infrastructure.database.base import get_db
from src.domain.repositories.planning_repository import PlanningRepository
from src.domain.repositories.transaction_repository import TransactionRepository
from src.domain.repositories.user_repository import UserRepository
from src.infrastructure.repositories.planning_repository import SQLAlchemyPlanningRepository
from src.infrastructure.repositories.transaction_repository import SQLAlchemyTransactionRepository
from src.infrastructure.repositories.user_repository import SQLAlchemyUserRepository
from src.application.notifications.notification_service import NotificationService
from src.application.use_cases.planning_use_cases import PlanningUseCases
from src.application.use_cases.notification_use_cases import NotificationUseCases
from src.infrastructure.database.models.user import User

router = APIRouter()


def get_planning_repository(db: AsyncSession = Depends(get_db)) -> PlanningRepository:
    return SQLAlchemyPlanningRepository(db)


def get_transaction_repository(db: AsyncSession = Depends(get_db)) -> TransactionRepository:
    from src.infrastructure.repositories.transaction_repository import SQLAlchemyTransactionRepository
    return SQLAlchemyTransactionRepository(db)


def get_user_repository(db: AsyncSession = Depends(get_db)) -> UserRepository:
    return SQLAlchemyUserRepository(db)


def get_notification_use_cases(
    planning_repo: PlanningRepository = Depends(get_planning_repository),
    transaction_repo: TransactionRepository = Depends(get_transaction_repository),
    user_repo: UserRepository = Depends(get_user_repository),
    db: AsyncSession = Depends(get_db),
) -> NotificationUseCases:
    notification_service = NotificationService()
    planning_use_cases = PlanningUseCases(
        planning_repository=planning_repo,
        monthly_repository=SQLAlchemyMonthlyPlanningRepository(db),
        weekly_repository=SQLAlchemyWeeklyPlanningRepository(db),
        daily_repository=SQLAlchemyDailyPlanningRepository(db),
        annual_repository=SQLAlchemyAnnualPlanningRepository(db),
        quarterly_repository=SQLAlchemyQuarterlyGoalRepository(db),
        transaction_repository=transaction_repo,
    )
    return NotificationUseCases(
        planning_repository=planning_repo,
        transaction_repository=transaction_repo,
        user_repository=user_repo,
        notification_service=notification_service,
        planning_use_cases=planning_use_cases,
    )


@router.post("/planning/{planning_id}/check", status_code=status.HTTP_200_OK)
async def check_planning_notification(
    planning_id: UUID,
    threshold: float = 10.0,
    force: bool = False,
    use_cases: NotificationUseCases = Depends(get_notification_use_cases),
    current_user: User = Depends(get_current_active_user),
):
    """Verifica planejamento e envia notificações se necessário"""
    result = await use_cases.check_and_notify_planning(
        planning_id=planning_id,
        threshold=threshold,
        force_notification=force,
    )
    return result


# Importar repositórios necessários
from src.infrastructure.repositories.planning_repository import (
    SQLAlchemyMonthlyPlanningRepository,
    SQLAlchemyWeeklyPlanningRepository,
    SQLAlchemyDailyPlanningRepository,
    SQLAlchemyAnnualPlanningRepository,
    SQLAlchemyQuarterlyGoalRepository,
)

