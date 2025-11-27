from fastapi import APIRouter, Depends, status
from typing import List
from uuid import UUID
from src.presentation.schemas.goal import (
    GoalCreate,
    GoalUpdate,
    GoalResponse,
    GoalContributionCreate,
    GoalContributionResponse,
    GoalProgressResponse,
)
from src.presentation.api.dependencies import get_current_active_user
from src.domain.repositories.goal_repository import GoalRepository, GoalContributionRepository
from src.domain.repositories.account_repository import AccountRepository
from src.infrastructure.repositories.goal_repository import (
    SQLAlchemyGoalRepository,
    SQLAlchemyGoalContributionRepository,
)
from src.infrastructure.repositories.account_repository import SQLAlchemyAccountRepository
from src.application.use_cases.goal_use_cases import GoalUseCases
from src.infrastructure.database.base import get_db
from src.infrastructure.database.models.user import User
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


def get_goal_repository(db: AsyncSession = Depends(get_db)) -> GoalRepository:
    return SQLAlchemyGoalRepository(db)


def get_contribution_repository(db: AsyncSession = Depends(get_db)) -> GoalContributionRepository:
    return SQLAlchemyGoalContributionRepository(db)


def get_account_repository(db: AsyncSession = Depends(get_db)) -> AccountRepository:
    return SQLAlchemyAccountRepository(db)


def get_calendar_event_repository(
    db: AsyncSession = Depends(get_db)
) -> "CalendarEventRepository":
    from src.domain.repositories.calendar_repository import CalendarEventRepository
    from src.infrastructure.repositories.calendar_repository import SQLAlchemyCalendarEventRepository
    return SQLAlchemyCalendarEventRepository(db)


def get_goal_use_cases(
    goal_repo: GoalRepository = Depends(get_goal_repository),
    contribution_repo: GoalContributionRepository = Depends(get_contribution_repository),
    account_repo: AccountRepository = Depends(get_account_repository),
    calendar_event_repo: "CalendarEventRepository" = Depends(get_calendar_event_repository),
) -> GoalUseCases:
    return GoalUseCases(goal_repo, contribution_repo, account_repo, calendar_event_repo)


@router.post("/", response_model=GoalResponse, status_code=status.HTTP_201_CREATED)
async def create_goal(
    goal_data: GoalCreate,
    use_cases: GoalUseCases = Depends(get_goal_use_cases),
    current_user: User = Depends(get_current_active_user),
):
    """Cria uma nova meta"""
    goal = await use_cases.create_goal(
        name=goal_data.name,
        goal_type=goal_data.goal_type,
        target_amount=goal_data.target_amount,
        user_id=current_user.id,
        description=goal_data.description,
        target_date=goal_data.target_date,
        icon=goal_data.icon,
        color=goal_data.color,
        savings_category_id=goal_data.savings_category_id,
        auto_contribution_percentage=goal_data.auto_contribution_percentage,
    )
    
    # Calcular progresso para resposta
    progress = await use_cases.calculate_goal_progress(goal.id)
    
    # Construir resposta manualmente para incluir campos calculados
    goal_dict = {
        "id": goal.id,
        "name": goal.name,
        "description": goal.description,
        "goal_type": goal.goal_type.value,
        "target_amount": goal.target_amount,
        "current_amount": goal.current_amount,
        "target_date": goal.target_date,
        "status": goal.status.value,
        "icon": goal.icon,
        "color": goal.color,
        "savings_category_id": goal.savings_category_id,
        "auto_contribution_percentage": goal.auto_contribution_percentage,
        "user_id": goal.user_id,
        "percentage": progress["percentage"],
        "remaining_amount": progress["remaining_amount"],
        "days_remaining": progress["days_remaining"],
        "estimated_completion_date": progress["estimated_completion_date"],
        "created_at": goal.created_at,
        "updated_at": goal.updated_at,
    }
    
    return goal_dict


@router.get("/", response_model=List[GoalResponse])
async def list_goals(
    use_cases: GoalUseCases = Depends(get_goal_use_cases),
    current_user: User = Depends(get_current_active_user),
):
    """Lista todas as metas do usuário"""
    goals = await use_cases.get_user_goals(current_user.id)
    
    # Adicionar progresso a cada meta
    result = []
    for goal in goals:
        progress = await use_cases.calculate_goal_progress(goal.id)
        
        # Construir resposta manualmente para incluir campos calculados
        goal_dict = {
            "id": goal.id,
            "name": goal.name,
            "description": goal.description,
            "goal_type": goal.goal_type.value,
            "target_amount": goal.target_amount,
            "current_amount": goal.current_amount,
            "target_date": goal.target_date,
            "status": goal.status.value,
            "icon": goal.icon,
            "color": goal.color,
            "savings_category_id": goal.savings_category_id,
            "auto_contribution_percentage": goal.auto_contribution_percentage,
            "user_id": goal.user_id,
            "percentage": progress["percentage"],
            "remaining_amount": progress["remaining_amount"],
            "days_remaining": progress["days_remaining"],
            "estimated_completion_date": progress["estimated_completion_date"],
            "created_at": goal.created_at,
            "updated_at": goal.updated_at,
        }
        result.append(goal_dict)
    
    return result


@router.get("/{goal_id}", response_model=GoalResponse)
async def get_goal(
    goal_id: UUID,
    use_cases: GoalUseCases = Depends(get_goal_use_cases),
    current_user: User = Depends(get_current_active_user),
):
    """Obtém uma meta específica"""
    goal = await use_cases.get_goal(goal_id)
    progress = await use_cases.calculate_goal_progress(goal_id)
    
    # Construir resposta manualmente para incluir campos calculados
    goal_dict = {
        "id": goal.id,
        "name": goal.name,
        "description": goal.description,
        "goal_type": goal.goal_type.value,
        "target_amount": goal.target_amount,
        "current_amount": goal.current_amount,
        "target_date": goal.target_date,
        "status": goal.status.value,
        "icon": goal.icon,
        "color": goal.color,
        "savings_category_id": goal.savings_category_id,
        "auto_contribution_percentage": goal.auto_contribution_percentage,
        "user_id": goal.user_id,
        "percentage": progress["percentage"],
        "remaining_amount": progress["remaining_amount"],
        "days_remaining": progress["days_remaining"],
        "estimated_completion_date": progress["estimated_completion_date"],
        "created_at": goal.created_at,
        "updated_at": goal.updated_at,
    }
    
    return goal_dict


@router.get("/{goal_id}/progress", response_model=GoalProgressResponse)
async def get_goal_progress(
    goal_id: UUID,
    use_cases: GoalUseCases = Depends(get_goal_use_cases),
    current_user: User = Depends(get_current_active_user),
):
    """Obtém o progresso detalhado de uma meta"""
    progress = await use_cases.calculate_goal_progress(goal_id)
    goal = await use_cases.get_goal(goal_id)
    
    return {
        **progress,
        "name": goal.name,
    }


@router.get("/{goal_id}/contributions", response_model=List[GoalContributionResponse])
async def list_contributions(
    goal_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Lista todas as contribuições de uma meta"""
    contribution_repo = SQLAlchemyGoalContributionRepository(db)
    contributions = await contribution_repo.get_by_goal_id(goal_id)
    
    return [GoalContributionResponse.model_validate(c) for c in contributions]


@router.post("/{goal_id}/contributions", response_model=GoalContributionResponse, status_code=status.HTTP_201_CREATED)
async def add_contribution(
    goal_id: UUID,
    contribution_data: GoalContributionCreate,
    use_cases: GoalUseCases = Depends(get_goal_use_cases),
    current_user: User = Depends(get_current_active_user),
):
    """Adiciona uma contribuição para a meta"""
    contribution = await use_cases.add_contribution(
        goal_id=goal_id,
        amount=contribution_data.amount,
        contribution_date=contribution_data.contribution_date,
        notes=contribution_data.notes,
        transaction_id=contribution_data.transaction_id,
    )
    return contribution


@router.put("/{goal_id}", response_model=GoalResponse)
async def update_goal(
    goal_id: UUID,
    goal_update: GoalUpdate,
    use_cases: GoalUseCases = Depends(get_goal_use_cases),
    current_user: User = Depends(get_current_active_user),
):
    """Atualiza uma meta"""
    goal = await use_cases.update_goal(
        goal_id=goal_id,
        name=goal_update.name,
        description=goal_update.description,
        target_amount=goal_update.target_amount,
        target_date=goal_update.target_date,
        status=goal_update.status,
        icon=goal_update.icon,
        color=goal_update.color,
        savings_category_id=goal_update.savings_category_id,
        auto_contribution_percentage=goal_update.auto_contribution_percentage,
    )
    
    progress = await use_cases.calculate_goal_progress(goal.id)
    
    # Construir resposta manualmente para incluir campos calculados
    goal_dict = {
        "id": goal.id,
        "name": goal.name,
        "description": goal.description,
        "goal_type": goal.goal_type.value,
        "target_amount": goal.target_amount,
        "current_amount": goal.current_amount,
        "target_date": goal.target_date,
        "status": goal.status.value,
        "icon": goal.icon,
        "color": goal.color,
        "savings_category_id": goal.savings_category_id,
        "auto_contribution_percentage": goal.auto_contribution_percentage,
        "user_id": goal.user_id,
        "percentage": progress["percentage"],
        "remaining_amount": progress["remaining_amount"],
        "days_remaining": progress["days_remaining"],
        "estimated_completion_date": progress["estimated_completion_date"],
        "created_at": goal.created_at,
        "updated_at": goal.updated_at,
    }
    
    return goal_dict


@router.delete("/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_goal(
    goal_id: UUID,
    use_cases: GoalUseCases = Depends(get_goal_use_cases),
    current_user: User = Depends(get_current_active_user),
):
    """Deleta uma meta"""
    await use_cases.delete_goal(goal_id)
    return None

