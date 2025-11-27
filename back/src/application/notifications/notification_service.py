from typing import Optional
from decimal import Decimal
from src.application.notifications.email_service import EmailService
from src.application.notifications.whatsapp_service import WhatsAppService
from src.shared.config import settings


class NotificationService:
    """Serviço orquestrador de notificações"""

    def __init__(
        self,
        email_service: Optional[EmailService] = None,
        whatsapp_service: Optional[WhatsAppService] = None,
    ):
        self.email_service = email_service or EmailService(
            smtp_host=getattr(settings, "SMTP_HOST", "smtp.gmail.com"),
            smtp_port=getattr(settings, "SMTP_PORT", 587),
            smtp_user=getattr(settings, "SMTP_USER", None),
            smtp_password=getattr(settings, "SMTP_PASSWORD", None),
        )
        self.whatsapp_service = whatsapp_service or WhatsAppService()

    async def send_planning_notification(
        self,
        user_email: str,
        user_name: str,
        phone_number: Optional[str],
        planning_name: str,
        target_amount: Decimal,
        actual_amount: Decimal,
        percentage: float,
        threshold: float = 10.0,  # 10% de tolerância
    ) -> dict:
        """
        Envia notificações de planejamento
        
        Args:
            user_email: Email do usuário
            user_name: Nome do usuário
            phone_number: Número de telefone (opcional)
            planning_name: Nome do planejamento
            target_amount: Valor alvo
            actual_amount: Valor atual
            percentage: Porcentagem utilizada
            threshold: Limite de tolerância em porcentagem (padrão 10%)
        
        Returns:
            dict com status dos envios
        """
        is_over_budget = percentage > (100 + threshold)
        is_on_track = percentage <= 100

        results = {
            "email_sent": False,
            "whatsapp_sent": False,
            "is_over_budget": is_over_budget,
            "is_on_track": is_on_track,
        }

        # Converter para float para os templates
        target_float = float(target_amount)
        actual_float = float(actual_amount)

        # Enviar email
        try:
            results["email_sent"] = await self.email_service.send_planning_alert(
                to_email=user_email,
                user_name=user_name,
                planning_name=planning_name,
                target_amount=target_float,
                actual_amount=actual_float,
                percentage=percentage,
                is_over_budget=is_over_budget,
            )
        except Exception as e:
            print(f"Erro ao enviar email: {e}")

        # Enviar WhatsApp se número fornecido
        if phone_number:
            try:
                results["whatsapp_sent"] = await self.whatsapp_service.send_planning_alert(
                    phone_number=phone_number,
                    user_name=user_name,
                    planning_name=planning_name,
                    target_amount=target_float,
                    actual_amount=actual_float,
                    percentage=percentage,
                    is_over_budget=is_over_budget,
                )
            except Exception as e:
                print(f"Erro ao enviar WhatsApp: {e}")

        return results

    def should_send_notification(
        self, percentage: float, threshold: float = 10.0, last_notification_percentage: Optional[float] = None
    ) -> bool:
        """
        Determina se deve enviar notificação
        
        Args:
            percentage: Porcentagem atual
            threshold: Limite de tolerância
            last_notification_percentage: Última porcentagem que gerou notificação
        
        Returns:
            True se deve enviar notificação
        """
        # Sempre notificar se está muito fora (acima de 100% + threshold)
        if percentage > (100 + threshold):
            # Evitar spam: só notificar se mudou significativamente desde última notificação
            if last_notification_percentage is None:
                return True
            # Notificar se aumentou mais de 5% desde última notificação
            return percentage > (last_notification_percentage + 5.0)

        # Notificar quando está no planejamento (abaixo de 100%)
        if percentage <= 100:
            # Notificar apenas se está em marcos importantes (50%, 75%, 90%)
            milestones = [50.0, 75.0, 90.0, 100.0]
            if last_notification_percentage is None:
                return percentage >= 50.0
            
            # Verificar se passou algum marco
            for milestone in milestones:
                if (
                    last_notification_percentage < milestone
                    and percentage >= milestone
                ):
                    return True

        return False

    async def send_family_invitation_notification(
        self,
        user_email: str,
        family_name: str,
        inviter_name: str,
        signup_url: Optional[str] = None,
    ) -> dict:
        """Envia notificação de convite para família"""
        email_sent = False
        whatsapp_sent = False

        # Email
        subject = f"Convite para o grupo {family_name}"
        
        if signup_url:
            # Convite para novo usuário (com link de cadastro)
            html_content = self._get_family_invite_template(user_email, family_name, inviter_name, signup_url)
            text_content = f"""
Olá!

Você foi convidado(a) por {inviter_name} para participar do grupo "{family_name}" no FormuladoBolso.

Para aceitar o convite e criar sua conta, clique no link abaixo:

{signup_url}

Este link é válido por 7 dias.

Após criar sua conta, você terá acesso às funcionalidades permitidas pelo administrador do grupo.

Atenciosamente,
Equipe FormuladoBolso
            """
        else:
            # Notificação para usuário existente
            html_content = self._get_family_invite_existing_user_template(user_email, family_name, inviter_name)
            text_content = f"""
Olá!

Você foi convidado(a) por {inviter_name} para participar do grupo "{family_name}" no FormuladoBolso.

Acesse o sistema para ver o convite e começar a colaborar com sua família!

Atenciosamente,
Equipe FormuladoBolso
            """
        
        try:
            email_sent = await self.email_service.send_email(user_email, subject, html_content, text_content)
            if email_sent:
                print(f"✅ Email de convite enviado com sucesso para {user_email}")
            else:
                print(f"❌ Falha ao enviar email de convite para {user_email}")
                print(f"   Verifique os logs acima para mais detalhes")
                # Se o email falhou e temos um link de cadastro, mostrar no console
                if signup_url:
                    print(f"")
                    print(f"🔗 LINK DE CONVITE (copie e envie manualmente):")
                    print(f"   {signup_url}")
                    print(f"")
        except Exception as e:
            print(f"❌ Erro ao enviar email de convite para {user_email}: {e}")
            import traceback
            traceback.print_exc()
            # Se o email falhou e temos um link de cadastro, mostrar no console
            if signup_url:
                print(f"")
                print(f"🔗 LINK DE CONVITE (copie e envie manualmente):")
                print(f"   {signup_url}")
                print(f"")

        return {
            "email_sent": email_sent, 
            "whatsapp_sent": whatsapp_sent,
            "signup_url": signup_url if not email_sent and signup_url else None
        }
    
    def _get_family_invite_template(
        self,
        user_email: str,
        family_name: str,
        inviter_name: str,
        signup_url: str,
    ) -> str:
        """Template HTML para convite de família (novo usuário)"""
        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
        .content {{ background-color: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px; }}
        .button {{ display: inline-block; padding: 15px 30px; background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; font-weight: bold; }}
        .button:hover {{ opacity: 0.9; }}
        .info-box {{ background-color: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 20px 0; border-radius: 5px; }}
        .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
        .url-box {{ background-color: #e9ecef; padding: 10px; border-radius: 5px; font-family: monospace; word-break: break-all; margin: 10px 0; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎉 Você foi convidado(a)!</h1>
        </div>
        <div class="content">
            <p>Olá!</p>
            
            <p>Você foi convidado(a) por <strong>{inviter_name}</strong> para participar do grupo <strong>"{family_name}"</strong> no FormuladoBolso.</p>
            
            <p>Para aceitar o convite e criar sua conta, clique no botão abaixo:</p>
            
            <div style="text-align: center;">
                <a href="{signup_url}" class="button">Aceitar Convite e Criar Conta</a>
            </div>
            
            <p>Ou copie e cole o link abaixo no seu navegador:</p>
            <div class="url-box">{signup_url}</div>
            
            <div class="info-box">
                <strong>ℹ️ Informações importantes:</strong>
                <ul>
                    <li>Este link é válido por <strong>7 dias</strong></li>
                    <li>Após criar sua conta, você terá acesso às funcionalidades permitidas pelo administrador do grupo</li>
                    <li>Você precisará configurar autenticação de dois fatores (2FA) durante o cadastro</li>
                </ul>
            </div>
            
            <p>Estamos ansiosos para tê-lo(a) conosco!</p>
        </div>
        <div class="footer">
            <p>FormuladoBolso - Seu gerenciador financeiro pessoal</p>
            <p>Este é um email automático, por favor não responda.</p>
        </div>
    </div>
</body>
</html>
        """
    
    def _get_family_invite_existing_user_template(
        self,
        user_email: str,
        family_name: str,
        inviter_name: str,
    ) -> str:
        """Template HTML para convite de família (usuário existente)"""
        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
        .content {{ background-color: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px; }}
        .button {{ display: inline-block; padding: 15px 30px; background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; font-weight: bold; }}
        .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎉 Você foi convidado(a)!</h1>
        </div>
        <div class="content">
            <p>Olá!</p>
            
            <p>Você foi convidado(a) por <strong>{inviter_name}</strong> para participar do grupo <strong>"{family_name}"</strong> no FormuladoBolso.</p>
            
            <p>Acesse o sistema para ver o convite e começar a colaborar com sua família!</p>
            
            <div style="text-align: center;">
                <a href="http://localhost:3000/family" class="button">Ver Convite</a>
            </div>
        </div>
        <div class="footer">
            <p>FormuladoBolso - Seu gerenciador financeiro pessoal</p>
            <p>Este é um email automático, por favor não responda.</p>
        </div>
    </div>
</body>
</html>
        """

    async def send_family_chat_notification(
        self,
        user_email: str,
        user_phone: Optional[str],
        family_name: str,
        sender_name: str,
        message: str,
    ) -> dict:
        """Envia notificação de nova mensagem no chat familiar"""
        email_sent = False
        whatsapp_sent = False

        # Email
        subject = f"Nova mensagem no grupo {family_name}"
        body = f"""
        Olá!

        {sender_name} enviou uma nova mensagem no grupo "{family_name}":

        "{message}"

        Acesse o sistema para ver todas as mensagens e responder!

        Atenciosamente,
        Equipe FormuladoBolso
        """
        try:
            email_sent = await self.email_service.send_email(user_email, subject, body)
        except Exception as e:
            print(f"Erro ao enviar email: {e}")

        # WhatsApp
        if user_phone:
            whatsapp_message = f"💬 Nova mensagem no grupo {family_name}\n\n{sender_name}: {message}\n\nAcesse o app para responder!"
            try:
                whatsapp_sent = await self.whatsapp_service.send_message(user_phone, whatsapp_message)
            except Exception as e:
                print(f"Erro ao enviar WhatsApp: {e}")

        return {"email_sent": email_sent, "whatsapp_sent": whatsapp_sent}

