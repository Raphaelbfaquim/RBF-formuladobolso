from fastapi import APIRouter, Depends, Query
from typing import Optional
from uuid import UUID
from decimal import Decimal
from src.presentation.api.dependencies import get_current_active_user
from src.domain.repositories.transaction_repository import TransactionRepository
from src.domain.repositories.account_repository import AccountRepository
from src.infrastructure.repositories.transaction_repository import SQLAlchemyTransactionRepository
from src.infrastructure.repositories.account_repository import SQLAlchemyAccountRepository
from src.application.services.prediction_service import PredictionService
from src.infrastructure.database.base import get_db
from src.infrastructure.database.models.user import User
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


def get_prediction_service(db: AsyncSession = Depends(get_db)) -> PredictionService:
    transaction_repo = SQLAlchemyTransactionRepository(db)
    account_repo = SQLAlchemyAccountRepository(db)
    return PredictionService(transaction_repo, account_repo)


@router.get("/balance/{account_id}")
async def predict_balance(
    account_id: UUID,
    days: int = Query(30, ge=1, le=365),
    prediction_service: PredictionService = Depends(get_prediction_service),
    current_user: User = Depends(get_current_active_user),
):
    """Previsão de saldo futuro"""
    prediction = await prediction_service.predict_balance(current_user.id, account_id, days)
    return prediction


@router.post("/simulate-purchase")
async def simulate_purchase(
    account_id: UUID,
    amount: Decimal,
    description: str = "",
    prediction_service: PredictionService = Depends(get_prediction_service),
    current_user: User = Depends(get_current_active_user),
):
    """Simula uma compra e mostra impacto"""
    simulation = await prediction_service.simulate_purchase(
        current_user.id, account_id, amount, description
    )
    return simulation


@router.get("/savings-goal")
async def calculate_savings_goal(
    target_amount: Decimal,
    months: int = Query(..., ge=1, le=120),
    prediction_service: PredictionService = Depends(get_prediction_service),
    current_user: User = Depends(get_current_active_user),
):
    """Calcula quanto precisa economizar por mês para alcançar uma meta"""
    calculation = await prediction_service.calculate_savings_goal(
        current_user.id, target_amount, months
    )
    return calculation

