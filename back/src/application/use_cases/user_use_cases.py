from typing import Optional
from uuid import UUID
from src.domain.repositories.user_repository import UserRepository
from src.infrastructure.database.models.user import User, UserRole
from src.application.auth.jwt_service import JWTService
from src.shared.exceptions import ValidationException, ConflictException, NotFoundException


class UserUseCases:
    """Casos de uso para gerenciamento de usuários"""

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
        self.jwt_service = JWTService()

    async def create_user(
        self,
        email: str,
        username: str,
        password: str,
        full_name: Optional[str] = None,
    ) -> User:
        """Cria um novo usuário"""
        # Verificar se email já existe
        existing_user = await self.user_repository.get_by_email(email)
        if existing_user:
            raise ConflictException("Email já está em uso")

        # Verificar se username já existe
        existing_username = await self.user_repository.get_by_username(username)
        if existing_username:
            raise ConflictException("Username já está em uso")

        # Criar usuário
        hashed_password = self.jwt_service.get_password_hash(password)
        user = User(
            email=email,
            username=username,
            hashed_password=hashed_password,
            full_name=full_name,
            is_active=True,
            is_verified=False,
            role=UserRole.USER,
        )

        return await self.user_repository.create(user)

    async def get_user(self, user_id: UUID) -> User:
        """Obtém um usuário por ID"""
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise NotFoundException("Usuário", str(user_id))
        return user

    async def update_user(
        self,
        user_id: UUID,
        email: Optional[str] = None,
        username: Optional[str] = None,
        full_name: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> User:
        """Atualiza um usuário"""
        user = await self.get_user(user_id)

        if email and email != user.email:
            existing_user = await self.user_repository.get_by_email(email)
            if existing_user:
                raise ConflictException("Email já está em uso")
            user.email = email

        if username and username != user.username:
            existing_username = await self.user_repository.get_by_username(username)
            if existing_username:
                raise ConflictException("Username já está em uso")
            user.username = username

        if full_name is not None:
            user.full_name = full_name

        if is_active is not None:
            user.is_active = is_active

        return await self.user_repository.update(user)

    async def delete_user(self, user_id: UUID) -> bool:
        """Deleta um usuário"""
        user = await self.get_user(user_id)
        return await self.user_repository.delete(user_id)

