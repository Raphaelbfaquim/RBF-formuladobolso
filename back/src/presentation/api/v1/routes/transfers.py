from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from src.presentation.schemas.transfer import TransferCreate, TransferResponse
from src.presentation.api.dependencies import get_current_active_user
from src.domain.repositories.transfer_repository import TransferRepository
from src.domain.repositories.account_repository import AccountRepository
from src.domain.repositories.transaction_repository import TransactionRepository
from src.infrastructure.repositories.transfer_repository import SQLAlchemyTransferRepository
from src.infrastructure.repositories.account_repository import SQLAlchemyAccountRepository
from src.infrastructure.repositories.transaction_repository import SQLAlchemyTransactionRepository
from src.application.use_cases.transfer_use_cases import TransferUseCases
from src.infrastructure.database.base import get_db
from src.infrastructure.database.models.user import User
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


def get_transfer_use_cases(db: AsyncSession = Depends(get_db)) -> TransferUseCases:
    transfer_repo = SQLAlchemyTransferRepository(db)
    account_repo = SQLAlchemyAccountRepository(db)
    transaction_repo = SQLAlchemyTransactionRepository(db)
    return TransferUseCases(transfer_repo, account_repo, transaction_repo)


@router.post("", response_model=TransferResponse, status_code=status.HTTP_201_CREATED)
async def create_transfer(
    transfer_data: TransferCreate,
    use_cases: TransferUseCases = Depends(get_transfer_use_cases),
    current_user: User = Depends(get_current_active_user),
):
    """Cria uma transferência entre contas"""
    try:
        transfer = await use_cases.create_transfer(
            from_account_id=transfer_data.from_account_id,
            to_account_id=transfer_data.to_account_id,
            amount=transfer_data.amount,
            user_id=current_user.id,
            transfer_date=transfer_data.transfer_date,
            description=transfer_data.description,
            workspace_id=transfer_data.workspace_id,
            scheduled_date=transfer_data.scheduled_date,
            notes=transfer_data.notes,
        )
        return transfer
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=List[TransferResponse])
async def list_transfers(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    use_cases: TransferUseCases = Depends(get_transfer_use_cases),
    current_user: User = Depends(get_current_active_user),
):
    """Lista transferências do usuário"""
    transfers = await use_cases.get_user_transfers(
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date,
    )
    return transfers


@router.get("/{transfer_id}", response_model=TransferResponse)
async def get_transfer(
    transfer_id: UUID,
    use_cases: TransferUseCases = Depends(get_transfer_use_cases),
    current_user: User = Depends(get_current_active_user),
):
    """Obtém uma transferência específica"""
    try:
        transfer = await use_cases.get_transfer(transfer_id)
        return transfer
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{transfer_id}/cancel", response_model=TransferResponse)
async def cancel_transfer(
    transfer_id: UUID,
    use_cases: TransferUseCases = Depends(get_transfer_use_cases),
    current_user: User = Depends(get_current_active_user),
):
    """Cancela uma transferência"""
    try:
        transfer = await use_cases.cancel_transfer(transfer_id)
        return transfer
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

