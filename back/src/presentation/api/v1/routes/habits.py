from fastapi import APIRouter, Depends, Query
from typing import Optional
from src.presentation.api.dependencies import get_current_active_user
from src.domain.repositories.transaction_repository import TransactionRepository
from src.infrastructure.repositories.transaction_repository import SQLAlchemyTransactionRepository
from src.application.services.habit_analysis_service import HabitAnalysisService
from src.infrastructure.database.base import get_db
from src.infrastructure.database.models.user import User
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


def get_habit_analysis_service(db: AsyncSession = Depends(get_db)) -> HabitAnalysisService:
    transaction_repo = SQLAlchemyTransactionRepository(db)
    return HabitAnalysisService(transaction_repo)


@router.get("/analysis")
async def analyze_habits(
    days: int = Query(90, ge=30, le=365),
    habit_service: HabitAnalysisService = Depends(get_habit_analysis_service),
    current_user: User = Depends(get_current_active_user),
):
    """Analisa hábitos de consumo"""
    analysis = await habit_service.analyze_consumption_habits(current_user.id, days)
    return analysis


@router.get("/compare")
async def compare_with_average(
    category: Optional[str] = Query(None),
    habit_service: HabitAnalysisService = Depends(get_habit_analysis_service),
    current_user: User = Depends(get_current_active_user),
):
    """Compara gastos com média do mercado"""
    comparison = await habit_service.compare_with_average(current_user.id, category)
    return comparison

