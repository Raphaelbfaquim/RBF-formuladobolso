from typing import Optional
from uuid import UUID
from datetime import datetime, timedelta
import secrets
import pytz
from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.repositories.user_repository import UserRepository
from src.infrastructure.database.models.user import User
from src.application.auth.jwt_service import JWTService
from src.shared.exceptions import UnauthorizedException, ValidationException


class AuthService:
    """Serviço de autenticação"""

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
        self.jwt_service = JWTService()

    async def authenticate(self, email: str, password: str) -> Optional[dict]:
        """Autentica usuário e retorna tokens"""
        print(f"🔍 Buscando usuário com email: {email}")
        user = await self.user_repository.get_by_email(email)
        
        if not user:
            print(f"❌ Usuário não encontrado para email: {email}")
            raise UnauthorizedException("Email ou senha incorretos")
        
        print(f"✅ Usuário encontrado: {user.email}, is_active: {user.is_active}, is_verified: {user.is_verified}")
        
        if not user.is_active:
            print(f"❌ Usuário inativo: {email}")
            raise UnauthorizedException("Usuário inativo")
        
        print(f"🔐 Verificando senha para usuário: {email}")
        password_valid = self.jwt_service.verify_password(password, user.hashed_password)
        print(f"🔐 Resultado da verificação de senha: {password_valid}")
        
        if not password_valid:
            print(f"❌ Senha incorreta para usuário: {email}")
            raise UnauthorizedException("Email ou senha incorretos")
        
        access_token = self.jwt_service.create_access_token(
            data={"sub": str(user.id), "email": user.email}
        )
        refresh_token = self.jwt_service.create_refresh_token(
            data={"sub": str(user.id)}
        )
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "full_name": user.full_name,
                "is_active": user.is_active,
                "is_verified": user.is_verified,
                "role": user.role.value if hasattr(user.role, 'value') else str(user.role),
                "created_at": user.created_at,
                "updated_at": user.updated_at,
            },
        }

    async def refresh_token(self, refresh_token: str) -> dict:
        """Gera novo access token a partir do refresh token"""
        payload = self.jwt_service.decode_token(refresh_token)
        
        if not payload or payload.get("type") != "refresh":
            raise UnauthorizedException("Token inválido")
        
        user_id = UUID(payload.get("sub"))
        user = await self.user_repository.get_by_id(user_id)
        
        if not user or not user.is_active:
            raise UnauthorizedException("Usuário inválido")
        
        access_token = self.jwt_service.create_access_token(
            data={"sub": str(user.id), "email": user.email}
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
        }

    async def get_current_user(self, token: str) -> User:
        """Obtém usuário atual a partir do token"""
        payload = self.jwt_service.decode_token(token)
        
        if not payload or payload.get("type") != "access":
            raise UnauthorizedException("Token inválido")
        
        user_id = UUID(payload.get("sub"))
        user = await self.user_repository.get_by_id(user_id)
        
        if not user or not user.is_active:
            raise UnauthorizedException("Usuário inválido")
        
        return user

    async def request_password_reset(self, email: str) -> Optional[str]:
        """Gera token de reset de senha e salva no usuário. Retorna o token ou None se usuário não existir"""
        user = await self.user_repository.get_by_email(email)
        
        if not user:
            return None
        
        # Gerar token seguro
        reset_token = secrets.token_urlsafe(32)
        reset_token_expires = datetime.now(pytz.UTC) + timedelta(hours=1)  # Token válido por 1 hora
        
        # Atualizar usuário com token
        await self.user_repository.update_reset_token(
            user_id=user.id,
            reset_token=reset_token,
            reset_token_expires=reset_token_expires
        )
        
        return reset_token

    async def reset_password(self, token: str, new_password: str) -> bool:
        """Redefine a senha usando o token de reset"""
        user = await self.user_repository.get_by_reset_token(token)
        
        if not user:
            raise ValidationException("Token de reset inválido ou expirado")
        
        # Verificar se o token não expirou
        if user.reset_token_expires and user.reset_token_expires < datetime.now(pytz.UTC):
            raise ValidationException("Token de reset expirado")
        
        # Atualizar senha
        hashed_password = self.jwt_service.get_password_hash(new_password)
        await self.user_repository.update_password(user.id, hashed_password)
        
        # Limpar token de reset
        await self.user_repository.update_reset_token(
            user_id=user.id,
            reset_token=None,
            reset_token_expires=None
        )
        
        return True

