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


@router.get("/2fa/status")
async def get_2fa_status(
    security_service: SecurityService = Depends(get_security_service),
    current_user: User = Depends(get_current_active_user),
):
    """Obtém status do 2FA do usuário"""
    from sqlalchemy import select
    from src.infrastructure.database.models.security import TwoFactorAuth
    
    stmt = select(TwoFactorAuth).where(TwoFactorAuth.user_id == current_user.id)
    result = await security_service.session.execute(stmt)
    two_factor = result.scalar_one_or_none()
    
    return {
        "is_enabled": two_factor.is_enabled if two_factor else False,
        "method": two_factor.method.value if two_factor and two_factor.method else None,
    }


@router.post("/2fa/disable")
async def disable_2fa(
    security_service: SecurityService = Depends(get_security_service),
    current_user: User = Depends(get_current_active_user),
):
    """Desabilita 2FA para o usuário"""
    from sqlalchemy import select
    from src.infrastructure.database.models.security import TwoFactorAuth
    
    stmt = select(TwoFactorAuth).where(TwoFactorAuth.user_id == current_user.id)
    result = await security_service.session.execute(stmt)
    two_factor = result.scalar_one_or_none()
    
    if two_factor:
        two_factor.is_enabled = False
        two_factor.secret = None
        two_factor.backup_codes = None
        await security_service.session.commit()
    
    return {"message": "2FA desabilitado com sucesso"}


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

