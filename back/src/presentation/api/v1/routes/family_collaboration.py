from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List
from uuid import UUID
from datetime import datetime
import pytz
from src.presentation.api.dependencies import get_current_active_user
from src.infrastructure.database.models.user import User, FamilyMemberRole
from src.infrastructure.database.models.family_permission import FamilyMemberPermission, ModulePermission
from src.domain.repositories.family_permission_repository import FamilyPermissionRepository
from src.shared.exceptions import NotFoundException, UnauthorizedException
from src.domain.repositories.family_repository import (
    FamilyRepository,
    FamilyMemberRepository,
    FamilyChatRepository,
)
from src.domain.repositories.user_repository import UserRepository
from src.domain.repositories.family_permission_repository import FamilyPermissionRepository
from src.infrastructure.repositories.family_repository import (
    SQLAlchemyFamilyRepository,
    SQLAlchemyFamilyMemberRepository,
    SQLAlchemyFamilyChatRepository,
)
from src.infrastructure.repositories.family_invite_repository import SQLAlchemyFamilyInviteRepository
from src.infrastructure.repositories.family_permission_repository import SQLAlchemyFamilyPermissionRepository
from src.infrastructure.repositories.user_repository import SQLAlchemyUserRepository
from src.shared.config import settings
from src.application.use_cases.family_use_cases import FamilyUseCases
from src.application.notifications.notification_service import NotificationService
from src.infrastructure.database.base import get_db
from src.presentation.schemas.family import (
    FamilyCreate,
    FamilyResponse,
    FamilyMemberInvite,
    FamilyMemberResponse,
    FamilyMemberWithPermissionsResponse,
    ChatMessageCreate,
    ChatMessageResponse,
    PermissionUpdate,
    MemberPermissionResponse,
    InviteTokenResponse,
    InviteRegisterRequest,
)
from src.infrastructure.database.models.family_invite import FamilyInviteStatus
from src.application.use_cases.user_use_cases import UserUseCases
from src.presentation.api.dependencies import get_auth_service
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


async def create_default_permissions_for_member(
    member: "FamilyMember",
    permission_repo: FamilyPermissionRepository
) -> None:
    """Cria permissões padrão para um membro baseado no seu role"""
    from src.infrastructure.database.models.user import FamilyMemberRole
    
    # Definir permissões padrão baseadas no role
    if member.role == FamilyMemberRole.OWNER:
        # OWNER tem todas as permissões
        default_permissions = {
            module: {"can_view": True, "can_edit": True, "can_delete": True}
            for module in ModulePermission
        }
    elif member.role == FamilyMemberRole.ADMIN:
        # ADMIN tem permissões de visualização e edição (sem delete em alguns módulos críticos)
        default_permissions = {
            module: {"can_view": True, "can_edit": True, "can_delete": module not in [ModulePermission.FAMILY, ModulePermission.SETTINGS]}
            for module in ModulePermission
        }
    elif member.role == FamilyMemberRole.MEMBER:
        # MEMBER tem permissões limitadas (apenas visualização e edição básica)
        view_only_modules = [ModulePermission.SETTINGS, ModulePermission.FAMILY]
        default_permissions = {
            module: {
                "can_view": True,
                "can_edit": module not in view_only_modules,
                "can_delete": False
            }
            for module in ModulePermission
        }
    else:  # VIEWER
        # VIEWER tem apenas permissão de visualização
        default_permissions = {
            module: {"can_view": True, "can_edit": False, "can_delete": False}
            for module in ModulePermission
        }
    
    # Criar permissões no banco
    for module, perms in default_permissions.items():
        permission = FamilyMemberPermission(
            family_member_id=member.id,
            module=module,
            can_view=perms["can_view"],
            can_edit=perms["can_edit"],
            can_delete=perms["can_delete"],
        )
        await permission_repo.create(permission)
    
    print(f"✅ Permissões padrão criadas para membro {member.id} com role {member.role}")


def get_family_use_cases(db: AsyncSession = Depends(get_db)) -> FamilyUseCases:
    family_repo = SQLAlchemyFamilyRepository(db)
    member_repo = SQLAlchemyFamilyMemberRepository(db)
    chat_repo = SQLAlchemyFamilyChatRepository(db)
    invite_repo = SQLAlchemyFamilyInviteRepository(db)
    user_repo = SQLAlchemyUserRepository(db)
    notification_service = NotificationService()
    
    return FamilyUseCases(family_repo, member_repo, chat_repo, invite_repo, user_repo, notification_service)


def get_gamification_service_helper(db: AsyncSession):
    """Helper para criar GamificationService"""
    try:
        from src.domain.repositories.gamification_repository import (
            BadgeRepository,
            UserBadgeRepository,
            UserLevelRepository,
            ChallengeRepository,
            UserChallengeRepository,
        )
        from src.domain.repositories.transaction_repository import TransactionRepository
        from src.domain.repositories.goal_repository import GoalRepository
        from src.infrastructure.repositories.gamification_repository import (
            SQLAlchemyBadgeRepository,
            SQLAlchemyUserBadgeRepository,
            SQLAlchemyUserLevelRepository,
            SQLAlchemyChallengeRepository,
            SQLAlchemyUserChallengeRepository,
        )
        from src.infrastructure.repositories.transaction_repository import SQLAlchemyTransactionRepository
        from src.infrastructure.repositories.goal_repository import SQLAlchemyGoalRepository
        from src.application.services.gamification_service import GamificationService
        
        badge_repo = SQLAlchemyBadgeRepository(db)
        user_badge_repo = SQLAlchemyUserBadgeRepository(db)
        user_level_repo = SQLAlchemyUserLevelRepository(db)
        challenge_repo = SQLAlchemyChallengeRepository(db)
        user_challenge_repo = SQLAlchemyUserChallengeRepository(db)
        transaction_repo = SQLAlchemyTransactionRepository(db)
        goal_repo = SQLAlchemyGoalRepository(db)
        
        return GamificationService(
            badge_repo,
            user_badge_repo,
            user_level_repo,
            challenge_repo,
            user_challenge_repo,
            transaction_repo,
            goal_repo,
        )
    except Exception as e:
        print(f"[WARNING] Erro ao criar GamificationService: {e}")
        return None


@router.post("", response_model=FamilyResponse, status_code=status.HTTP_201_CREATED)
async def create_family(
    family_data: FamilyCreate,
    use_cases: FamilyUseCases = Depends(get_family_use_cases),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Cria um novo grupo/família"""
    family = await use_cases.create_family(
        name=family_data.name,
        description=family_data.description,
        owner_id=current_user.id,
    )
    
    # Adicionar XP por criar família (gamificação)
    gamification_service = get_gamification_service_helper(db)
    if gamification_service:
        try:
            await gamification_service.add_points(current_user.id, 50, "Criar família")
        except Exception as e:
            print(f"[WARNING] Erro ao adicionar XP por criar família: {e}")
    
    return family


@router.get("", response_model=List[FamilyResponse])
async def list_families(
    use_cases: FamilyUseCases = Depends(get_family_use_cases),
    current_user: User = Depends(get_current_active_user),
):
    """Lista todas as famílias/grupos do usuário"""
    families = await use_cases.family_repository.get_by_user_id(current_user.id)
    return families


@router.get("/my-permissions", response_model=dict)
async def get_my_permissions(
    use_cases: FamilyUseCases = Depends(get_family_use_cases),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Retorna todas as permissões do usuário atual em todas as famílias"""
    try:
        # Buscar todas as famílias do usuário
        families = await use_cases.family_repository.get_by_user_id(current_user.id)
        permission_repo = SQLAlchemyFamilyPermissionRepository(db)
        
        all_permissions = {}
        
        is_owner_or_admin = False
        
        for family in families:
            # Buscar membro na família
            member = await use_cases.family_member_repository.get_member_in_family(
                current_user.id, family.id
            )
            if member:
                role = member.role.value if hasattr(member.role, 'value') else str(member.role)
                # Se for OWNER ou ADMIN, tem acesso total
                if role in ['owner', 'admin']:
                    is_owner_or_admin = True
                
                # Buscar permissões do membro
                permissions = await permission_repo.get_by_family_member_id(member.id)
                all_permissions[str(family.id)] = {
                    "family_name": family.name,
                    "role": role,
                    "permissions": {
                        p.module.value if hasattr(p.module, 'value') else str(p.module): {
                            "can_view": p.can_view,
                            "can_edit": p.can_edit,
                            "can_delete": p.can_delete,
                        }
                        for p in permissions
                    }
                }
        
        return {
            "permissions_by_family": all_permissions,
            "has_any_family": len(families) > 0,
            "is_owner_or_admin": is_owner_or_admin
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro ao buscar permissões: {str(e)}")


@router.get("/{family_id}", response_model=FamilyResponse)
async def get_family(
    family_id: UUID,
    use_cases: FamilyUseCases = Depends(get_family_use_cases),
    current_user: User = Depends(get_current_active_user),
):
    """Obtém detalhes de uma família"""
    family = await use_cases.family_repository.get_by_id(family_id)
    if not family:
        raise HTTPException(status_code=404, detail="Família não encontrada")
    
    # Verificar se é membro
    member = await use_cases.family_member_repository.get_member_in_family(
        current_user.id, family_id
    )
    if not member:
        raise HTTPException(status_code=403, detail="Você não é membro desta família")
    
    return family


@router.post("/{family_id}/invite", response_model=dict, status_code=status.HTTP_201_CREATED)
async def invite_member(
    family_id: UUID,
    invite_data: FamilyMemberInvite,
    use_cases: FamilyUseCases = Depends(get_family_use_cases),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Convida um usuário para a família"""
    try:
        frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
        result = await use_cases.invite_member(
            family_id=family_id,
            user_email=invite_data.user_email,
            inviter_id=current_user.id,
            role=invite_data.role,
            frontend_url=frontend_url,
        )
        
        # Adicionar XP por convidar membro (gamificação)
        gamification_service = get_gamification_service_helper(db)
        if gamification_service:
            try:
                await gamification_service.add_points(current_user.id, 25, "Convidar membro para família")
            except Exception as e:
                print(f"[WARNING] Erro ao adicionar XP por convidar membro: {e}")
        
        # Se membro foi criado diretamente (usuário já existia), criar permissões padrão
        if not result.get("invite_created") and result.get("member"):
            member = result["member"]
            permission_repo = SQLAlchemyFamilyPermissionRepository(db)
            await create_default_permissions_for_member(member, permission_repo)
        
        # Retornar resposta apropriada
        if result.get("invite_created"):
            email_sent = result.get("email_sent", False)
            signup_url = result.get("signup_url")
            was_resent = result.get("resent", False)
            
            if was_resent:
                status_message = "Convite reenviado por email. O usuário receberá um novo link para criar a conta." if email_sent else "Convite reenviado, mas o email não pôde ser enviado. Use o link abaixo para compartilhar manualmente."
            else:
                status_message = "Convite enviado por email. O usuário receberá um link para criar a conta." if email_sent else "Convite criado, mas o email não pôde ser enviado. Use o link abaixo para compartilhar manualmente."
            
            response = {
                "id": result["invite"].id,
                "email": result["invite"].email,
                "status": "invite_sent" if email_sent else "invite_created",
                "message": status_message,
                "resent": was_resent
            }
            
            # Se o email não foi enviado, incluir o link na resposta
            if not email_sent and signup_url:
                response["signup_url"] = signup_url
                print(f"")
                print(f"⚠️  ATENÇÃO: Email não foi enviado. Link do convite:")
                print(f"   {signup_url}")
                print(f"")
            
            return response
        else:
            # Usuário já existia, retornar membro criado
            member = result["member"]
            return {
                "id": member.id,
                "family_id": member.family_id,
                "user_id": member.user_id,
                "role": member.role,
                "joined_at": member.joined_at,
                "status": "member_created",
                "message": "Usuário adicionado à família com sucesso."
            }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except UnauthorizedException as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro ao convidar membro: {str(e)}")


@router.get("/{family_id}/members", response_model=List[FamilyMemberWithPermissionsResponse])
async def get_family_members(
    family_id: UUID,
    use_cases: FamilyUseCases = Depends(get_family_use_cases),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Lista membros da família com permissões"""
    try:
        # Verificar se é membro
        member = await use_cases.family_member_repository.get_member_in_family(
            current_user.id, family_id
        )
        if not member:
            raise HTTPException(status_code=403, detail="Você não é membro desta família")
        
        members = await use_cases.get_family_members(family_id, current_user.id)
        permission_repo = SQLAlchemyFamilyPermissionRepository(db)
        user_repo = SQLAlchemyUserRepository(db)
        
        # Buscar permissões e dados do usuário para cada membro
        result = []
        for mem in members:
            # Buscar dados do usuário
            user = await user_repo.get_by_id(mem.user_id)
            permissions = await permission_repo.get_by_family_member_id(mem.id)
            
            result.append({
                "id": mem.id,
                "family_id": mem.family_id,
                "user_id": mem.user_id,
                "role": mem.role,
                "joined_at": mem.joined_at,
                "user_username": user.username if user else None,
                "user_email": user.email if user else None,
                "permissions": [
                    {
                        "id": p.id,
                        "family_member_id": p.family_member_id,
                        "module": p.module.value if hasattr(p.module, 'value') else str(p.module),
                        "can_view": p.can_view,
                        "can_edit": p.can_edit,
                        "can_delete": p.can_delete,
                    }
                    for p in permissions
                ],
            })
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro ao carregar membros: {str(e)}")


@router.delete("/{family_id}/members/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_member(
    family_id: UUID,
    member_id: UUID,
    use_cases: FamilyUseCases = Depends(get_family_use_cases),
    current_user: User = Depends(get_current_active_user),
):
    """Remove um membro da família"""
    try:
        await use_cases.remove_member(family_id, member_id, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.post("/chat/messages", response_model=ChatMessageResponse, status_code=status.HTTP_201_CREATED)
async def send_chat_message(
    message_data: ChatMessageCreate,
    use_cases: FamilyUseCases = Depends(get_family_use_cases),
    current_user: User = Depends(get_current_active_user),
):
    """Envia mensagem no chat familiar"""
    try:
        message = await use_cases.send_chat_message(
            family_id=message_data.family_id,
            user_id=current_user.id,
            message=message_data.message,
        )
        return message
    except Exception as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.get("/chat/{family_id}/messages", response_model=List[ChatMessageResponse])
async def get_chat_messages(
    family_id: UUID,
    limit: int = 50,
    use_cases: FamilyUseCases = Depends(get_family_use_cases),
    current_user: User = Depends(get_current_active_user),
):
    """Obtém mensagens do chat familiar"""
    try:
        messages = await use_cases.get_chat_messages(family_id, current_user.id, limit)
        return messages
    except Exception as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.put("/{family_id}/members/{member_id}/permissions", response_model=List[MemberPermissionResponse])
async def update_member_permissions(
    family_id: UUID,
    member_id: UUID,
    permissions: List[PermissionUpdate],
    use_cases: FamilyUseCases = Depends(get_family_use_cases),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Atualiza permissões de um membro da família"""
    try:
        # Verificar se é OWNER ou ADMIN
        member = await use_cases.family_member_repository.get_member_in_family(
            current_user.id, family_id
        )
        if not member or member.role not in [FamilyMemberRole.OWNER, FamilyMemberRole.ADMIN]:
            raise HTTPException(status_code=403, detail="Apenas administradores podem gerenciar permissões")
        
        # Verificar se o membro existe e pertence à família
        target_member = await use_cases.family_member_repository.get_by_id(member_id)
        if not target_member or target_member.family_id != family_id:
            raise HTTPException(status_code=404, detail="Membro não encontrado")
        
        # OWNER não pode ter permissões alteradas
        if target_member.role == FamilyMemberRole.OWNER:
            raise HTTPException(status_code=400, detail="Não é possível alterar permissões do proprietário")
        
        permission_repo = SQLAlchemyFamilyPermissionRepository(db)
        
        # Atualizar ou criar permissões
        result = []
        for perm_data in permissions:
            # Garantir que module é um enum ModulePermission
            module = perm_data.module
            
            # Debug: verificar tipo recebido
            if isinstance(module, str):
                print(f"⚠️  Módulo recebido como string: {module} (tipo: {type(module)})")
                # Converter string para enum (case-insensitive)
                module_lower = module.lower()
                try:
                    module = ModulePermission(module_lower)
                    print(f"✅ Convertido para enum: {module} (valor: {module.value})")
                except ValueError:
                    # Tentar pelo nome do enum (ex: "TRANSACTIONS" -> ModulePermission.TRANSACTIONS)
                    module_upper = module.upper()
                    if hasattr(ModulePermission, module_upper):
                        module = getattr(ModulePermission, module_upper)
                        print(f"✅ Convertido pelo nome do enum: {module} (valor: {module.value})")
                    else:
                        raise HTTPException(
                            status_code=400, 
                            detail=f"Módulo inválido: {module}. Módulos válidos: {[m.value for m in ModulePermission]}"
                        )
            elif isinstance(module, ModulePermission):
                print(f"✅ Módulo já é enum: {module} (valor: {module.value})")
            else:
                print(f"❌ Tipo inesperado: {type(module)}, valor: {module}")
                raise HTTPException(
                    status_code=400,
                    detail=f"Tipo inválido para módulo: {type(module)}. Esperado: ModulePermission ou string"
                )
            
            # Garantir que temos um enum válido antes de fazer a query
            if not isinstance(module, ModulePermission):
                raise HTTPException(
                    status_code=500,
                    detail=f"Erro interno: módulo não é um enum válido após conversão"
                )
            
            existing = await permission_repo.get_by_family_member_and_module(
                member_id, module
            )
            
            if existing:
                existing.can_view = perm_data.can_view
                existing.can_edit = perm_data.can_edit
                existing.can_delete = perm_data.can_delete
                permission = await permission_repo.update(existing)
            else:
                permission = FamilyMemberPermission(
                    family_member_id=member_id,
                    module=module,  # Usar o módulo convertido
                    can_view=perm_data.can_view,
                    can_edit=perm_data.can_edit,
                    can_delete=perm_data.can_delete,
                )
                permission = await permission_repo.create(permission)
            
            result.append({
                "id": permission.id,
                "family_member_id": permission.family_member_id,
                "module": permission.module.value if hasattr(permission.module, 'value') else str(permission.module),
                "can_view": permission.can_view,
                "can_edit": permission.can_edit,
                "can_delete": permission.can_delete,
            })
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{family_id}/members/{member_id}/permissions", response_model=List[MemberPermissionResponse])
async def get_member_permissions(
    family_id: UUID,
    member_id: UUID,
    use_cases: FamilyUseCases = Depends(get_family_use_cases),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Obtém permissões de um membro da família"""
    try:
        # Verificar se é membro
        member = await use_cases.family_member_repository.get_member_in_family(
            current_user.id, family_id
        )
        if not member:
            raise HTTPException(status_code=403, detail="Você não é membro desta família")
        
        # Verificar se o membro existe e pertence à família
        target_member = await use_cases.family_member_repository.get_by_id(member_id)
        if not target_member or target_member.family_id != family_id:
            raise HTTPException(status_code=404, detail="Membro não encontrado")
        
        # Apenas OWNER, ADMIN ou o próprio membro podem ver permissões
        if member.role not in [FamilyMemberRole.OWNER, FamilyMemberRole.ADMIN] and member.id != member_id:
            raise HTTPException(status_code=403, detail="Você não tem permissão para ver estas permissões")
        
        permission_repo = SQLAlchemyFamilyPermissionRepository(db)
        permissions = await permission_repo.get_by_family_member_id(member_id)
        
        return [
            {
                "id": p.id,
                "family_member_id": p.family_member_id,
                "module": p.module.value if hasattr(p.module, 'value') else str(p.module),
                "can_view": p.can_view,
                "can_edit": p.can_edit,
                "can_delete": p.can_delete,
            }
            for p in permissions
        ]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/invite/validate", response_model=InviteTokenResponse)
async def validate_invite_token(
    token: str = Query(..., description="Token do convite"),
    use_cases: FamilyUseCases = Depends(get_family_use_cases),
    db: AsyncSession = Depends(get_db),
):
    """Valida token de convite e retorna informações"""
    try:
        invite_repo = SQLAlchemyFamilyInviteRepository(db)
        invite = await invite_repo.get_by_token(token)
        
        if not invite:
            return InviteTokenResponse(
                valid=False,
                message="Token de convite inválido ou não encontrado"
            )
        
        # Verificar se está expirado
        if datetime.now(pytz.UTC) > invite.expires_at:
            invite.status = FamilyInviteStatus.EXPIRED
            await invite_repo.update(invite)
            return InviteTokenResponse(
                valid=False,
                message="Token de convite expirado"
            )
        
        # Verificar se já foi aceito
        if invite.status != FamilyInviteStatus.PENDING:
            return InviteTokenResponse(
                valid=False,
                message="Este convite já foi utilizado ou cancelado"
            )
        
        # Buscar informações da família e do convidante
        family = await use_cases.family_repository.get_by_id(invite.family_id)
        inviter = await use_cases.user_repository.get_by_id(invite.invited_by)
        
        return InviteTokenResponse(
            valid=True,
            email=invite.email,
            family_name=family.name if family else "Família",
            inviter_name=inviter.username if inviter else "Administrador",
            role=invite.role.value if hasattr(invite.role, 'value') else str(invite.role),
            expires_at=invite.expires_at,
            message="Token válido. Você pode prosseguir com o cadastro."
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        return InviteTokenResponse(
            valid=False,
            message=f"Erro ao validar token: {str(e)}"
        )


@router.post("/invite/register", response_model=dict, status_code=status.HTTP_201_CREATED)
async def register_via_invite(
    request: InviteRegisterRequest,
    use_cases: FamilyUseCases = Depends(get_family_use_cases),
    db: AsyncSession = Depends(get_db),
):
    """Registra usuário via convite da família"""
    try:
        from src.application.services.security_service import SecurityService
        from src.infrastructure.database.models.user import FamilyMember
        
        invite_repo = SQLAlchemyFamilyInviteRepository(db)
        invite = await invite_repo.get_by_token(request.token)
        
        if not invite:
            raise HTTPException(status_code=404, detail="Token de convite inválido")
        
        # Verificar se está expirado
        if datetime.now(pytz.UTC) > invite.expires_at:
            invite.status = FamilyInviteStatus.EXPIRED
            await invite_repo.update(invite)
            raise HTTPException(status_code=400, detail="Token de convite expirado")
        
        # Verificar se já foi aceito
        if invite.status != FamilyInviteStatus.PENDING:
            raise HTTPException(status_code=400, detail="Este convite já foi utilizado")
        
        # Criar usuário
        user_use_cases = UserUseCases(use_cases.user_repository)
        user = await user_use_cases.create_user(
            email=invite.email,
            username=request.username,
            password=request.password,
            full_name=request.full_name,
        )
        
        # Habilitar 2FA (igual ao cadastro normal)
        security_service = SecurityService(db)
        # Passar email do usuário para melhor identificação no QR code
        two_factor_data = await security_service.enable_2fa(user.id, "totp", user_email=user.email)
        
        # Verificar código 2FA se fornecido
        if request.two_factor_code:
            # TODO: Implementar verificação do código 2FA
            # Por enquanto, apenas validamos que foi fornecido
            pass
        
        # Criar membro da família
        member = FamilyMember(
            family_id=invite.family_id,
            user_id=user.id,
            role=invite.role,
        )
        member = await use_cases.family_member_repository.create(member)
        
        # Criar permissões padrão baseadas no role
        permission_repo = SQLAlchemyFamilyPermissionRepository(db)
        await create_default_permissions_for_member(member, permission_repo)
        
        # Marcar convite como aceito
        invite.status = FamilyInviteStatus.ACCEPTED
        invite.user_id = user.id
        invite.accepted_at = datetime.now(pytz.UTC)
        await invite_repo.update(invite)
        
        # Gerar tokens de autenticação
        auth_service = get_auth_service(use_cases.user_repository)
        tokens = await auth_service.authenticate(invite.email, request.password)
        
        # Inicializar nível de gamificação
        gamification_service = get_gamification_service_helper(db)
        if gamification_service:
            try:
                await gamification_service.initialize_user_level(user.id)
                await gamification_service.add_points(user.id, 50, "Cadastro via convite familiar")
            except Exception as e:
                print(f"[WARNING] Erro ao inicializar gamificação: {e}")
        
        # Converter QR code para base64 string
        import base64
        qr_code_base64 = None
        qr_code_data = two_factor_data.get("qr_code")
        
        if qr_code_data:
            if isinstance(qr_code_data, bytes):
                qr_code_base64 = base64.b64encode(qr_code_data).decode('utf-8')
                print(f"✅ QR Code gerado e convertido para base64 (tamanho: {len(qr_code_base64)} caracteres)")
            else:
                print(f"⚠️  QR Code não é bytes, tipo: {type(qr_code_data)}")
        else:
            print(f"❌ QR Code não foi gerado (qr_code_data é None)")
        
        return {
            "user": {
                "id": str(user.id),
                "email": user.email,
                "username": user.username,
            },
            "tokens": tokens,
            "two_factor": {
                "secret": two_factor_data["secret"],
                "qr_code": qr_code_base64,
                "backup_codes": two_factor_data["backup_codes"],
            },
            "family_member": {
                "id": str(member.id),
                "family_id": str(member.family_id),
                "role": member.role.value if hasattr(member.role, 'value') else str(member.role),
            },
            "message": "Conta criada com sucesso! Configure seu autenticador 2FA."
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro ao registrar via convite: {str(e)}")

