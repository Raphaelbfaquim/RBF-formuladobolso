from fastapi import APIRouter, Depends, status
from typing import List
from uuid import UUID
from decimal import Decimal
from src.presentation.schemas.planning import (
    PlanningCreate,
    PlanningUpdate,
    PlanningResponse,
    PlanningProgressResponse,
    QuarterlyGoalCreate,
    QuarterlyGoalResponse,
)
from src.presentation.api.dependencies import get_current_active_user
from src.infrastructure.database.models.user import User
from src.application.use_cases.planning_use_cases import PlanningUseCases

router = APIRouter()


# TODO: Implementar dependências completas
@router.get("/", response_model=List[PlanningResponse])
async def list_plannings(
    current_user: User = Depends(get_current_active_user),
):
    """Lista todos os planejamentos do usuário"""
    return {"message": "List plannings endpoint"}


@router.post("/", response_model=PlanningResponse, status_code=status.HTTP_201_CREATED)
async def create_planning(
    planning_data: PlanningCreate,
    current_user: User = Depends(get_current_active_user),
):
    """Cria um novo planejamento"""
    return {"message": "Create planning endpoint"}


@router.get("/{planning_id}", response_model=PlanningResponse)
async def get_planning(
    planning_id: UUID,
    current_user: User = Depends(get_current_active_user),
):
    """Obtém um planejamento específico"""
    return {"message": f"Get planning {planning_id}"}


@router.get("/{planning_id}/progress", response_model=PlanningProgressResponse)
async def get_planning_progress(
    planning_id: UUID,
    current_user: User = Depends(get_current_active_user),
):
    """Obtém o progresso de um planejamento"""
    return {"message": f"Get planning progress {planning_id}"}


@router.post("/annual/{planning_id}/quarterly-goals", response_model=QuarterlyGoalResponse, status_code=status.HTTP_201_CREATED)
async def create_quarterly_goal(
    planning_id: UUID,
    goal_data: QuarterlyGoalCreate,
    current_user: User = Depends(get_current_active_user),
):
    """Cria uma meta trimestral"""
    return {"message": f"Create quarterly goal for planning {planning_id}"}
