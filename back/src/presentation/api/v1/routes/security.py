from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from src.presentation.api.dependencies import get_current_active_user
from src.infrastructure.database.base import get_db
from src.application.services.security_service import SecurityService
from src.infrastructure.database.models.user import User
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


class Enable2FARequest(BaseModel):
    method: str = "totp"


class Verify2FARequest(BaseModel):
    code: str


def get_security_service(db: AsyncSession = Depends(get_db)) -> SecurityService:
    return SecurityService(db)


@router.post("/2fa/enable")
async def enable_2fa(
    request: Enable2FARequest,
    security_service: SecurityService = Depends(get_security_service),
    current_user: User = Depends(get_current_active_user),
):
    """Habilita autenticação de dois fatores"""
    result = await security_service.enable_2fa(current_user.id, request.method, user_email=current_user.email)
    return result


@router.post("/2fa/verify")
async def verify_2fa(
    request: Verify2FARequest,
    security_service: SecurityService = Depends(get_security_service),
    current_user: User = Depends(get_current_active_user),
):
    """Verifica código 2FA"""
    is_valid = await security_service.verify_2fa(current_user.id, request.code)
    return {"valid": is_valid}


@router.get("/audit-logs")
async def get_audit_logs(
    limit: int = 50,
    security_service: SecurityService = Depends(get_security_service),
    current_user: User = Depends(get_current_active_user),
):
    """Obtém logs de auditoria do usuário"""
    # TODO: Implementar busca de logs
    return {"logs": []}


@router.get("/alerts")
async def get_security_alerts(
    security_service: SecurityService = Depends(get_security_service),
    current_user: User = Depends(get_current_active_user),
):
    """Obtém alertas de segurança"""
    # TODO: Implementar busca de alertas
    return {"alerts": []}

