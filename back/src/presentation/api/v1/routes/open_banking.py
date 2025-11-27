from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID
from src.presentation.api.dependencies import get_current_active_user
from src.infrastructure.open_banking.bacen_client import OpenBankingService
from src.infrastructure.database.models.user import User

router = APIRouter()


class ConnectBankRequest(BaseModel):
    bank_name: str
    consent_token: str
    account_number: Optional[str] = None


@router.post("/connect")
async def connect_bank(
    request: ConnectBankRequest,
    open_banking_service: OpenBankingService = Depends(lambda: OpenBankingService()),
    current_user: User = Depends(get_current_active_user),
):
    """Conecta conta bancária via Open Banking"""
    accounts = await open_banking_service.sync_user_accounts(
        str(current_user.id), request.consent_token
    )
    return {
        "message": "Conta conectada com sucesso",
        "accounts": accounts,
    }


@router.get("/accounts")
async def get_bank_accounts(
    open_banking_service: OpenBankingService = Depends(lambda: OpenBankingService()),
    current_user: User = Depends(get_current_active_user),
):
    """Lista contas conectadas"""
    # TODO: Buscar do banco de dados
    return {"accounts": []}


@router.post("/sync/{connection_id}")
async def sync_account(
    connection_id: UUID,
    days: int = 30,
    open_banking_service: OpenBankingService = Depends(lambda: OpenBankingService()),
    current_user: User = Depends(get_current_active_user),
):
    """Sincroniza transações de uma conta conectada"""
    # TODO: Implementar sincronização
    return {"message": "Sincronização iniciada"}

