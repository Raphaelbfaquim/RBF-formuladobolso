from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from uuid import UUID
from src.presentation.schemas.scheduled_transaction import (
    ScheduledTransactionCreate,
    ScheduledTransactionResponse,
)
from src.presentation.api.dependencies import get_current_active_user
from src.domain.repositories.scheduled_transaction_repository import ScheduledTransactionRepository
from src.domain.repositories.transaction_repository import TransactionRepository
from src.domain.repositories.account_repository import AccountRepository
from src.infrastructure.repositories.scheduled_transaction_repository import SQLAlchemyScheduledTransactionRepository
from src.infrastructure.repositories.transaction_repository import SQLAlchemyTransactionRepository
from src.infrastructure.repositories.account_repository import SQLAlchemyAccountRepository
from src.application.use_cases.scheduled_transaction_use_cases import ScheduledTransactionUseCases
from src.infrastructure.database.base import get_db
from src.infrastructure.database.models.user import User
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


def get_scheduled_use_cases(db: AsyncSession = Depends(get_db)) -> ScheduledTransactionUseCases:
    scheduled_repo = SQLAlchemyScheduledTransactionRepository(db)
    transaction_repo = SQLAlchemyTransactionRepository(db)
    account_repo = SQLAlchemyAccountRepository(db)
    return ScheduledTransactionUseCases(scheduled_repo, transaction_repo, account_repo)


@router.post("", response_model=ScheduledTransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_scheduled_transaction(
    scheduled_data: ScheduledTransactionCreate,
    use_cases: ScheduledTransactionUseCases = Depends(get_scheduled_use_cases),
    current_user: User = Depends(get_current_active_user),
):
    """Cria uma transação agendada"""
    try:
        scheduled = await use_cases.create_scheduled_transaction(
            description=scheduled_data.description,
            amount=scheduled_data.amount,
            transaction_type=scheduled_data.transaction_type,
            account_id=scheduled_data.account_id,
            user_id=current_user.id,
            start_date=scheduled_data.start_date,
            recurrence_type=scheduled_data.recurrence_type,
            end_date=scheduled_data.end_date,
            max_executions=scheduled_data.max_executions,
            auto_execute=scheduled_data.auto_execute,
            category_id=scheduled_data.category_id,
            workspace_id=scheduled_data.workspace_id,
            notes=scheduled_data.notes,
            recurrence_day=scheduled_data.recurrence_day,
            recurrence_weekday=scheduled_data.recurrence_weekday,
        )
        return scheduled
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=List[ScheduledTransactionResponse])
async def list_scheduled_transactions(
    use_cases: ScheduledTransactionUseCases = Depends(get_scheduled_use_cases),
    current_user: User = Depends(get_current_active_user),
):
    """Lista transações agendadas do usuário"""
    scheduled = await use_cases.get_scheduled_transactions(current_user.id)
    return scheduled


@router.post("/{scheduled_id}/execute")
async def execute_scheduled_transaction(
    scheduled_id: UUID,
    use_cases: ScheduledTransactionUseCases = Depends(get_scheduled_use_cases),
    current_user: User = Depends(get_current_active_user),
):
    """Executa uma transação agendada manualmente"""
    try:
        transaction = await use_cases.execute_scheduled_transaction(scheduled_id)
        return {"message": "Transação executada com sucesso", "transaction_id": transaction.id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{scheduled_id}/pause")
async def pause_scheduled_transaction(
    scheduled_id: UUID,
    use_cases: ScheduledTransactionUseCases = Depends(get_scheduled_use_cases),
    current_user: User = Depends(get_current_active_user),
):
    """Pausa uma transação agendada"""
    try:
        scheduled = await use_cases.pause_scheduled_transaction(scheduled_id)
        return scheduled
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{scheduled_id}/resume")
async def resume_scheduled_transaction(
    scheduled_id: UUID,
    use_cases: ScheduledTransactionUseCases = Depends(get_scheduled_use_cases),
    current_user: User = Depends(get_current_active_user),
):
    """Retoma uma transação agendada"""
    try:
        scheduled = await use_cases.resume_scheduled_transaction(scheduled_id)
        return scheduled
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{scheduled_id}/cancel")
async def cancel_scheduled_transaction(
    scheduled_id: UUID,
    use_cases: ScheduledTransactionUseCases = Depends(get_scheduled_use_cases),
    current_user: User = Depends(get_current_active_user),
):
    """Cancela uma transação agendada"""
    try:
        scheduled = await use_cases.cancel_scheduled_transaction(scheduled_id)
        return scheduled
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

