from fastapi import APIRouter, Depends, status
from typing import List
from uuid import UUID
from src.presentation.schemas.user import UserResponse, UserUpdate, ChangePasswordRequest
from src.presentation.api.dependencies import get_current_active_user, get_user_repository, get_auth_service
from src.domain.repositories.user_repository import UserRepository
from src.application.use_cases.user_use_cases import UserUseCases
from src.application.auth.auth_service import AuthService
from src.infrastructure.database.models.user import User
from src.shared.exceptions import UnauthorizedException

router = APIRouter()


def get_user_use_cases(user_repository: UserRepository = Depends(get_user_repository)) -> UserUseCases:
    return UserUseCases(user_repository)


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user),
):
    """Obtém informações do usuário atual"""
    return current_user


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    use_cases: UserUseCases = Depends(get_user_use_cases),
    current_user: User = Depends(get_current_active_user),
):
    """Obtém um usuário específico"""
    user = await use_cases.get_user(user_id)
    return user


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    use_cases: UserUseCases = Depends(get_user_use_cases),
    current_user: User = Depends(get_current_active_user),
):
    """Atualiza o usuário atual"""
    user = await use_cases.update_user(
        user_id=current_user.id,
        email=user_update.email,
        username=user_update.username,
        full_name=user_update.full_name,
        is_active=user_update.is_active,
    )
    return user


@router.post("/me/change-password", status_code=status.HTTP_200_OK)
async def change_password(
    password_data: ChangePasswordRequest,
    current_user: User = Depends(get_current_active_user),
    auth_service: AuthService = Depends(get_auth_service),
    user_repository: UserRepository = Depends(get_user_repository),
):
    """Altera a senha do usuário atual"""
    from src.application.auth.jwt_service import JWTService
    
    jwt_service = JWTService()
    
    # Verificar senha atual
    password_valid = jwt_service.verify_password(
        password_data.current_password,
        current_user.hashed_password
    )
    
    if not password_valid:
        raise UnauthorizedException("Senha atual incorreta")
    
    # Atualizar senha
    hashed_password = jwt_service.get_password_hash(password_data.new_password)
    await user_repository.update_password(current_user.id, hashed_password)
    
    return {"message": "Senha alterada com sucesso"}
