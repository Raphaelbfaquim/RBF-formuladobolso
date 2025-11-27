from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from src.infrastructure.database.base import get_db
from src.domain.repositories.user_repository import UserRepository
from src.infrastructure.repositories.user_repository import SQLAlchemyUserRepository
from src.application.auth.auth_service import AuthService
from src.infrastructure.database.models.user import User
from src.shared.exceptions import UnauthorizedException

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")


def get_user_repository(
    db: AsyncSession = Depends(get_db),
) -> UserRepository:
    """Dependency para obter repositório de usuários"""
    return SQLAlchemyUserRepository(db)


def get_auth_service(
    user_repository: UserRepository = Depends(get_user_repository),
) -> AuthService:
    """Dependency para obter serviço de autenticação"""
    return AuthService(user_repository)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service),
) -> User:
    """Dependency para obter usuário atual autenticado"""
    try:
        return await auth_service.get_current_user(token)
    except UnauthorizedException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message,
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Dependency para obter usuário ativo"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Usuário inativo")
    return current_user

