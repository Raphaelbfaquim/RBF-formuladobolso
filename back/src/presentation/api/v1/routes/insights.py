from fastapi import APIRouter, Depends, Query
from typing import List
from uuid import UUID
from src.presentation.api.dependencies import get_current_active_user
from src.domain.repositories.transaction_repository import TransactionRepository
from src.domain.repositories.account_repository import AccountRepository
from src.domain.repositories.category_repository import CategoryRepository
from src.infrastructure.repositories.transaction_repository import SQLAlchemyTransactionRepository
from src.infrastructure.repositories.account_repository import SQLAlchemyAccountRepository
from src.infrastructure.repositories.category_repository import SQLAlchemyCategoryRepository
from src.application.services.insights_service import InsightsService
from src.infrastructure.database.base import get_db
from src.infrastructure.database.models.user import User
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


def get_insights_service(db: AsyncSession = Depends(get_db)) -> InsightsService:
    transaction_repo = SQLAlchemyTransactionRepository(db)
    account_repo = SQLAlchemyAccountRepository(db)
    category_repo = SQLAlchemyCategoryRepository(db)
    return InsightsService(transaction_repo, account_repo, category_repo)


@router.get("/")
async def get_insights(
    days: int = Query(30, ge=7, le=365),
    insights_service: InsightsService = Depends(get_insights_service),
    current_user: User = Depends(get_current_active_user),
):
    """Obtém insights automáticos"""
    insights = await insights_service.generate_insights(current_user.id, days)
    return {"insights": insights, "count": len(insights)}


@router.get("/trends")
async def get_spending_trends(
    months: int = Query(6, ge=2, le=12),
    insights_service: InsightsService = Depends(get_insights_service),
    current_user: User = Depends(get_current_active_user),
):
    """Obtém tendências de gastos"""
    trends = await insights_service.get_spending_trends(current_user.id, months)
    return trends


@router.get("/categories")
async def get_category_analysis(
    days: int = Query(30, ge=7, le=365),
    insights_service: InsightsService = Depends(get_insights_service),
    current_user: User = Depends(get_current_active_user),
):
    """Análise de gastos por categoria"""
    analysis = await insights_service.get_category_analysis(current_user.id, days)
    return analysis


@router.get("/patterns")
async def get_spending_patterns(
    days: int = Query(30, ge=7, le=365),
    insights_service: InsightsService = Depends(get_insights_service),
    current_user: User = Depends(get_current_active_user),
):
    """Padrões de gastos (dia da semana, horário)"""
    patterns = await insights_service.get_spending_patterns(current_user.id, days)
    return patterns


@router.get("/recommendations")
async def get_recommendations(
    days: int = Query(30, ge=7, le=365),
    insights_service: InsightsService = Depends(get_insights_service),
    current_user: User = Depends(get_current_active_user),
):
    """Recomendações personalizadas"""
    recommendations = await insights_service.get_recommendations(current_user.id, days)
    return {"recommendations": recommendations, "count": len(recommendations)}


@router.get("/summary")
async def get_insights_summary(
    days: int = Query(30, ge=7, le=365),
    insights_service: InsightsService = Depends(get_insights_service),
    current_user: User = Depends(get_current_active_user),
):
    """Resumo completo de insights"""
    summary = await insights_service.get_summary(current_user.id, days)
    return summary

