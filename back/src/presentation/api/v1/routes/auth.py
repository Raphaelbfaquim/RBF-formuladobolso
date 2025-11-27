from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.infrastructure.database.base import get_db
from src.domain.repositories.user_repository import UserRepository
from src.infrastructure.repositories.user_repository import SQLAlchemyUserRepository
from src.application.auth.auth_service import AuthService
from src.application.use_cases.user_use_cases import UserUseCases
from src.application.notifications.email_service import EmailService
from src.presentation.schemas.user import (
    UserCreate,
    UserResponse,
    UserLogin,
    TokenResponse,
    RefreshTokenRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
)
from src.presentation.api.dependencies import get_auth_service, get_user_repository
from src.shared.config import settings
from src.shared.exceptions import UnauthorizedException

router = APIRouter()


def get_user_use_cases(
    user_repository: UserRepository = Depends(get_user_repository),
) -> UserUseCases:
    return UserUseCases(user_repository)


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    use_cases: UserUseCases = Depends(get_user_use_cases),
    db: AsyncSession = Depends(get_db),
):
    """Registra um novo usuário e habilita 2FA"""
    try:
        from src.application.services.security_service import SecurityService
        import base64
        
        print(f"🔐 Iniciando registro de usuário: {user_data.email}")
        
        # Criar usuário
        user = await use_cases.create_user(
            email=user_data.email,
            username=user_data.username,
            password=user_data.password,
            full_name=user_data.full_name,
        )
        print(f"✅ Usuário criado: {user.id}")
        
        # Habilitar 2FA (igual ao cadastro via convite)
        print(f"🔐 Habilitando 2FA para usuário: {user.id}")
        security_service = SecurityService(db)
        two_factor_data = await security_service.enable_2fa(user.id, "totp", user_email=user.email)
        print(f"✅ 2FA habilitado. Secret gerado: {two_factor_data.get('secret')[:10]}...")
        
        # Converter QR code para base64 string
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
        
        # Retornar dados do usuário e 2FA
        response_data = {
            "user": {
                "id": str(user.id),
                "email": user.email,
                "username": user.username,
                "full_name": user.full_name,
                "is_active": user.is_active,
                "is_verified": user.is_verified,
                "created_at": user.created_at.isoformat() if user.created_at else None,
            },
            "two_factor": {
                "secret": two_factor_data["secret"],
                "qr_code": qr_code_base64,
                "backup_codes": two_factor_data["backup_codes"],
            },
            "message": "Conta criada com sucesso! Configure seu autenticador 2FA."
        }
        
        print(f"✅ Registro concluído. Retornando dados com 2FA: {bool(response_data.get('two_factor'))}")
        return response_data
        
    except Exception as e:
        print(f"❌ Erro no registro: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar conta: {str(e)}"
        )


@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: UserLogin,
    auth_service: AuthService = Depends(get_auth_service),
):
    """Autentica usuário e retorna tokens"""
    try:
        print(f"🔐 Tentativa de login para email: {credentials.email}")
        result = await auth_service.authenticate(credentials.email, credentials.password)
        print(f"✅ Login bem-sucedido para: {credentials.email}")
        return result
    except UnauthorizedException:
        # Deixa passar para o handler global tratar (retorna 401)
        raise
    except Exception as e:
        # Log do erro interno mas retorna mensagem genérica
        print(f"❌ Erro interno no login para {credentials.email}: {str(e)}")
        import traceback
        traceback.print_exc()
        # Retorna erro genérico de autenticação para não expor detalhes
        raise UnauthorizedException("Email ou senha incorretos")


@router.post("/refresh", response_model=dict)
async def refresh_token(
    token_data: RefreshTokenRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    """Gera novo access token a partir do refresh token"""
    result = await auth_service.refresh_token(token_data.refresh_token)
    return result


def get_email_service() -> EmailService:
    """Dependency para obter serviço de email"""
    return EmailService(
        smtp_host=getattr(settings, 'SMTP_HOST', 'smtp.gmail.com'),
        smtp_port=getattr(settings, 'SMTP_PORT', 587),
        smtp_user=getattr(settings, 'SMTP_USER', None),
        smtp_password=getattr(settings, 'SMTP_PASSWORD', None),
    )


@router.post("/forgot-password", status_code=status.HTTP_200_OK)
async def forgot_password(
    request: ForgotPasswordRequest,
    auth_service: AuthService = Depends(get_auth_service),
    user_repository: UserRepository = Depends(get_user_repository),
    email_service: EmailService = Depends(get_email_service),
):
    """Solicita recuperação de senha"""
    try:
        # Gerar token de reset
        reset_token = await auth_service.request_password_reset(request.email)
        
        if reset_token:
            # Buscar usuário para enviar email
            user = await user_repository.get_by_email(request.email)
            
            if user:
                # Construir URL de reset
                frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
                reset_url = f"{frontend_url}/reset-password?token={reset_token}"
                
                # Enviar email (não falhar se email não for enviado)
                try:
                    user_name = user.full_name or user.username
                    email_sent = await email_service.send_password_reset_email(
                        to_email=user.email,
                        user_name=user_name,
                        reset_token=reset_token,
                        reset_url=reset_url,
                    )
                    if not email_sent:
                        # Log do erro mas não falhar a requisição
                        print(f"\n{'='*80}")
                        print(f"❌ ERRO: Email de recuperação NÃO foi enviado para {user.email}")
                        print(f"{'='*80}")
                        print(f"🔑 TOKEN DE RESET GERADO (válido por 1 hora):")
                        print(f"   {reset_token}")
                        print(f"\n🔗 LINK DE RESET:")
                        print(f"   {reset_url}")
                        print(f"\n⚠️  Para configurar o envio de emails:")
                        print(f"   1. Configure SMTP_USER e SMTP_PASSWORD no arquivo back/.env")
                        print(f"   2. Para Gmail, use uma 'Senha de App' (não a senha normal)")
                        print(f"   3. Acesse: https://myaccount.google.com/apppasswords")
                        print(f"{'='*80}\n")
                    else:
                        print(f"✅ Email de recuperação enviado com sucesso para {user.email}")
                except Exception as e:
                    # Log do erro mas não falhar a requisição
                    print(f"❌ EXCEÇÃO ao enviar email de recuperação para {user.email}: {e}")
                    print(f"   Token gerado: {reset_token}")
                    print(f"   URL de reset: {reset_url}")
                    import traceback
                    traceback.print_exc()
        
        # Sempre retornar sucesso por segurança (não revelar se email existe)
        return {"message": "Se o email existir, você receberá um link para redefinir sua senha"}
    except Exception as e:
        # Log do erro
        print(f"Erro no forgot-password: {e}")
        # Sempre retornar sucesso por segurança
        return {"message": "Se o email existir, você receberá um link para redefinir sua senha"}


@router.post("/reset-password", status_code=status.HTTP_200_OK)
async def reset_password(
    request: ResetPasswordRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    """Redefine a senha usando o token"""
    try:
        await auth_service.reset_password(request.token, request.new_password)
        return {"message": "Senha redefinida com sucesso"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

