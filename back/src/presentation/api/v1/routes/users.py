from fastapi import APIRouter, Depends, status
from typing import List
from uuid import UUID
from src.presentation.schemas.user import UserResponse, UserUpdate
from src.presentation.api.dependencies import get_current_active_user, get_user_repository
from src.domain.repositories.user_repository import UserRepository
from src.application.use_cases.user_use_cases import UserUseCases
from src.infrastructure.database.models.user import User

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
