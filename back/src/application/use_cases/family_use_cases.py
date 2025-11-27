from typing import List, Optional
from uuid import UUID
from datetime import datetime
import pytz

from src.domain.repositories.family_repository import (
    FamilyRepository,
    FamilyMemberRepository,
    FamilyChatRepository,
)
from src.domain.repositories.family_invite_repository import FamilyInviteRepository
from src.domain.repositories.user_repository import UserRepository
from src.infrastructure.database.models.user import Family, FamilyMember, FamilyMemberRole
from src.infrastructure.database.models.family_chat import FamilyChatMessage
from src.infrastructure.database.models.family_invite import FamilyInvite, FamilyInviteStatus
from src.application.notifications.notification_service import NotificationService
from src.shared.exceptions import NotFoundException, UnauthorizedException
import secrets
from datetime import timedelta

# Aliases para compatibilidade
NotFoundError = NotFoundException
UnauthorizedError = UnauthorizedException


class FamilyUseCases:
    """Casos de uso para gerenciamento de famílias"""

    def __init__(
        self,
        family_repository: FamilyRepository,
        family_member_repository: FamilyMemberRepository,
        family_chat_repository: FamilyChatRepository,
        family_invite_repository: FamilyInviteRepository,
        user_repository: UserRepository,
        notification_service: NotificationService,
    ):
        self.family_repository = family_repository
        self.family_member_repository = family_member_repository
        self.family_chat_repository = family_chat_repository
        self.family_invite_repository = family_invite_repository
        self.user_repository = user_repository
        self.notification_service = notification_service

    async def create_family(self, name: str, description: Optional[str], owner_id: UUID) -> Family:
        """Cria uma nova família/grupo"""
        family = Family(
            name=name,
            description=description,
            created_by=owner_id,
        )
        family = await self.family_repository.create(family)

        # Adicionar criador como OWNER
        owner_member = FamilyMember(
            family_id=family.id,
            user_id=owner_id,
            role=FamilyMemberRole.OWNER,
        )
        await self.family_member_repository.create(owner_member)

        return family

    async def invite_member(
        self, family_id: UUID, user_email: str, inviter_id: UUID, role: FamilyMemberRole = FamilyMemberRole.MEMBER, frontend_url: str = "http://localhost:3000"
    ) -> dict:
        """Convida um usuário para a família (cria convite com token)"""
        # Verificar se o inviter tem permissão
        inviter_member = await self.family_member_repository.get_member_in_family(inviter_id, family_id)
        if not inviter_member or inviter_member.role not in [FamilyMemberRole.OWNER, FamilyMemberRole.ADMIN]:
            raise UnauthorizedError("Você não tem permissão para convidar membros")

        # Verificar se usuário já existe
        existing_user = await self.user_repository.get_by_email(user_email)
        if existing_user:
            # Se usuário já existe, verificar se já é membro
            existing_member = await self.family_member_repository.get_member_in_family(existing_user.id, family_id)
            if existing_member:
                raise ValueError("Usuário já é membro desta família")
            # Se usuário existe mas não é membro, criar membro diretamente
            member = FamilyMember(
                family_id=family_id,
                user_id=existing_user.id,
                role=role,
            )
            member = await self.family_member_repository.create(member)
            
            # Criar permissões padrão (será feito no endpoint que chama este use case)
            
            # Enviar notificação
            family = await self.family_repository.get_by_id(family_id)
            inviter_user = await self.user_repository.get_by_id(inviter_id)
            await self.notification_service.send_family_invitation_notification(
                user_email=existing_user.email,
                family_name=family.name if family else "Família",
                inviter_name=inviter_user.username if inviter_user else "Admin",
            )
            
            return {"member": member, "invite_created": False}

        # Se usuário não existe, criar convite com token
        # Verificar se já existe convite pendente
        existing_invite = await self.family_invite_repository.get_by_email_and_family(user_email, family_id)
        was_resent = False  # Flag para indicar se foi reenvio
        
        if existing_invite:
            # Se já existe convite pendente, atualizar token e reenviar email
            # Gerar novo token único (tentar até conseguir um único)
            max_attempts = 5
            new_token = None
            for attempt in range(max_attempts):
                candidate_token = secrets.token_urlsafe(32)
                # Verificar se o token já existe
                existing_token_invite = await self.family_invite_repository.get_by_token(candidate_token)
                if not existing_token_invite:
                    new_token = candidate_token
                    break
            
            if not new_token:
                # Se não conseguiu gerar token único após várias tentativas, usar o token existente
                new_token = existing_invite.token
                print(f"⚠️  Usando token existente para reenvio (não foi possível gerar novo token único)")
                invite = existing_invite
            else:
                # Atualizar convite existente com novo token e renovar expiração
                existing_invite.token = new_token
                existing_invite.expires_at = datetime.now(pytz.UTC) + timedelta(days=7)
                existing_invite.role = role  # Atualizar role caso tenha mudado
                existing_invite.invited_by = inviter_id  # Atualizar quem convidou
                
                try:
                    invite = await self.family_invite_repository.update(existing_invite)
                except Exception as e:
                    print(f"⚠️  Erro ao atualizar convite: {e}")
                    print(f"   Continuando com reenvio usando token existente")
                    # Se falhar, usar o convite existente mesmo assim e reenviar email
                    invite = existing_invite
                    new_token = existing_invite.token
            
            token = new_token
            was_resent = True
            print(f"📧 Reenviando email de convite para {user_email} (convite existente atualizado)")
        else:
            # Gerar token único
            token = secrets.token_urlsafe(32)
            
            # Criar novo convite (válido por 7 dias)
            invite = FamilyInvite(
                family_id=family_id,
                invited_by=inviter_id,
                email=user_email,
                token=token,
                role=role,
                status=FamilyInviteStatus.PENDING,
                expires_at=datetime.now(pytz.UTC) + timedelta(days=7),
            )
            invite = await self.family_invite_repository.create(invite)

        # Enviar email com link de cadastro (ou reenviar se já existia)
        # SEMPRE tentar enviar o email, mesmo que já exista convite pendente
        family = await self.family_repository.get_by_id(family_id)
        inviter_user = await self.user_repository.get_by_id(inviter_id)
        signup_url = f"{frontend_url}/register/invite?token={token}"
        
        if was_resent:
            print(f"🔄 Reenviando email de convite para {user_email}")
        else:
            print(f"📧 Enviando email de convite para {user_email}")
        
        notification_result = await self.notification_service.send_family_invitation_notification(
            user_email=user_email,
            family_name=family.name if family else "Família",
            inviter_name=inviter_user.username if inviter_user else "Admin",
            signup_url=signup_url,
        )

        return {
            "invite": invite, 
            "invite_created": True,
            "email_sent": notification_result.get("email_sent", False),
            "signup_url": notification_result.get("signup_url") or signup_url,
            "resent": was_resent  # Indica se foi um reenvio
        }

    async def get_family_members(self, family_id: UUID, user_id: UUID) -> List[FamilyMember]:
        """Obtém membros da família"""
        # Verificar se é membro
        member = await self.family_member_repository.get_member_in_family(user_id, family_id)
        if not member:
            raise UnauthorizedError("Você não é membro desta família")

        return await self.family_member_repository.get_by_family_id(family_id)

    async def send_chat_message(
        self, family_id: UUID, user_id: UUID, message: str
    ) -> FamilyChatMessage:
        """Envia mensagem no chat familiar"""
        # Verificar se é membro
        member = await self.family_member_repository.get_member_in_family(user_id, family_id)
        if not member:
            raise UnauthorizedError("Você não é membro desta família")

        # Criar mensagem
        chat_message = FamilyChatMessage(
            family_id=family_id,
            user_id=user_id,
            message=message,
            is_system_message=False,
        )
        chat_message = await self.family_chat_repository.create(chat_message)

        # Notificar outros membros
        members = await self.family_member_repository.get_by_family_id(family_id)
        user = await self.user_repository.get_by_id(user_id)
        family = await self.family_repository.get_by_id(family_id)
        
        for m in members:
            if m.user_id != user_id:
                member_user = await self.user_repository.get_by_id(m.user_id)
                if member_user:
                    await self.notification_service.send_family_chat_notification(
                        user_email=member_user.email,
                        user_phone=member_user.phone_number,
                        family_name=family.name if family else "Família",
                        sender_name=user.username if user else "Usuário",
                        message=message,
                    )

        return chat_message

    async def get_chat_messages(
        self, family_id: UUID, user_id: UUID, limit: int = 50
    ) -> List[FamilyChatMessage]:
        """Obtém mensagens do chat familiar"""
        # Verificar se é membro
        member = await self.family_member_repository.get_member_in_family(user_id, family_id)
        if not member:
            raise UnauthorizedError("Você não é membro desta família")

        return await self.family_chat_repository.get_by_family_id(family_id, limit)

    async def remove_member(self, family_id: UUID, member_id: UUID, remover_id: UUID) -> bool:
        """Remove um membro da família"""
        # Verificar permissões
        remover_member = await self.family_member_repository.get_member_in_family(remover_id, family_id)
        if not remover_member or remover_member.role not in [FamilyMemberRole.OWNER, FamilyMemberRole.ADMIN]:
            raise UnauthorizedError("Você não tem permissão para remover membros")

        member = await self.family_member_repository.get_by_id(member_id)
        if not member or member.family_id != family_id:
            raise NotFoundError("Membro não encontrado")

        # Não permitir remover o owner
        if member.role == FamilyMemberRole.OWNER:
            raise ValueError("Não é possível remover o dono da família")

        return await self.family_member_repository.delete(member_id)

