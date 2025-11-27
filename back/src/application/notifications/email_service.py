import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from src.shared.config import settings


class EmailService:
    """Serviço para envio de emails"""

    def __init__(
        self,
        smtp_host: str = "smtp.gmail.com",
        smtp_port: int = 587,
        smtp_user: Optional[str] = None,
        smtp_password: Optional[str] = None,
    ):
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.smtp_user = smtp_user
        self.smtp_password = smtp_password

    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
    ) -> bool:
        """Envia um email"""
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.smtp_user
            msg["To"] = to_email

            # Adicionar conteúdo texto
            if text_content:
                text_part = MIMEText(text_content, "plain")
                msg.attach(text_part)

            # Adicionar conteúdo HTML
            html_part = MIMEText(html_content, "html")
            msg.attach(html_part)

            # Enviar email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                if self.smtp_user and self.smtp_password:
                    # Verificar se as credenciais não são placeholders
                    placeholder_users = ["seu-email@gmail.com", "seu-email@example.com", None]
                    placeholder_passwords = ["sua-senha-app", "sua-senha", "your-password", None]
                    
                    is_placeholder = (
                        self.smtp_user in placeholder_users or 
                        self.smtp_password in placeholder_passwords
                    )
                    
                    if is_placeholder:
                        print(f"⚠️  AVISO: Credenciais SMTP não configuradas corretamente")
                        print(f"   SMTP_USER: {self.smtp_user}")
                        print(f"   Configure SMTP_USER e SMTP_PASSWORD no arquivo .env")
                        return False
                    
                    try:
                        print(f"📧 Tentando enviar email via SMTP...")
                        print(f"   Host: {self.smtp_host}:{self.smtp_port}")
                        print(f"   User: {self.smtp_user}")
                        server.login(self.smtp_user, self.smtp_password)
                        print(f"✅ Autenticação SMTP bem-sucedida")
                    except smtplib.SMTPAuthenticationError as auth_error:
                        print(f"❌ Erro de autenticação SMTP: {auth_error}")
                        print(f"   Verifique se:")
                        print(f"   1. SMTP_USER está correto: {self.smtp_user}")
                        print(f"   2. SMTP_PASSWORD é uma 'Senha de App' do Gmail (não a senha normal)")
                        print(f"   3. A verificação em duas etapas está ativada na conta Google")
                        print(f"   4. Gere uma nova senha de app em: https://myaccount.google.com/apppasswords")
                        raise
                server.send_message(msg)
                print(f"✅ Email enviado com sucesso para {to_email}")

            return True
        except smtplib.SMTPAuthenticationError as e:
            print(f"❌ Erro de autenticação SMTP: {e}")
            print(f"   Verifique se SMTP_USER e SMTP_PASSWORD estão corretos")
            print(f"   Para Gmail, use uma 'Senha de App' (não a senha normal)")
            return False
        except smtplib.SMTPException as e:
            print(f"❌ Erro SMTP: {e}")
            return False
        except Exception as e:
            print(f"❌ Erro ao enviar email: {e}")
            import traceback
            traceback.print_exc()
            return False

    async def send_planning_alert(
        self,
        to_email: str,
        user_name: str,
        planning_name: str,
        target_amount: float,
        actual_amount: float,
        percentage: float,
        is_over_budget: bool,
    ) -> bool:
        """Envia alerta de planejamento"""
        if is_over_budget:
            subject = f"⚠️ Atenção: Você está fora do planejamento - {planning_name}"
            html_content = self._get_over_budget_template(
                user_name, planning_name, target_amount, actual_amount, percentage
            )
        else:
            subject = f"🎉 Parabéns! Você está no planejamento - {planning_name}"
            html_content = self._get_on_track_template(
                user_name, planning_name, target_amount, actual_amount, percentage
            )

        return await self.send_email(to_email, subject, html_content)

    def _get_over_budget_template(
        self,
        user_name: str,
        planning_name: str,
        target_amount: float,
        actual_amount: float,
        percentage: float,
    ) -> str:
        """Template HTML para quando está fora do planejamento"""
        excess = actual_amount - target_amount
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #dc3545; color: white; padding: 20px; text-align: center; border-radius: 5px 5px 0 0; }}
                .content {{ background-color: #f8f9fa; padding: 20px; border-radius: 0 0 5px 5px; }}
                .alert {{ background-color: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 20px 0; }}
                .stats {{ display: flex; justify-content: space-around; margin: 20px 0; }}
                .stat-box {{ background-color: white; padding: 15px; border-radius: 5px; text-align: center; flex: 1; margin: 0 5px; }}
                .stat-value {{ font-size: 24px; font-weight: bold; color: #dc3545; }}
                .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>⚠️ Atenção ao Seu Planejamento</h1>
                </div>
                <div class="content">
                    <p>Olá, <strong>{user_name}</strong>!</p>
                    
                    <div class="alert">
                        <h2>Você está fora do seu planejamento financeiro!</h2>
                        <p>O planejamento <strong>"{planning_name}"</strong> está acima do previsto.</p>
                    </div>

                    <div class="stats">
                        <div class="stat-box">
                            <div class="stat-label">Meta</div>
                            <div class="stat-value" style="color: #28a745;">R$ {target_amount:,.2f}</div>
                        </div>
                        <div class="stat-box">
                            <div class="stat-label">Gasto Real</div>
                            <div class="stat-value">R$ {actual_amount:,.2f}</div>
                        </div>
                        <div class="stat-box">
                            <div class="stat-label">Excesso</div>
                            <div class="stat-value">R$ {excess:,.2f}</div>
                        </div>
                    </div>

                    <p><strong>Você ultrapassou {percentage:.1f}% do seu planejamento.</strong></p>
                    
                    <p>É importante revisar seus gastos e ajustar seu orçamento para manter suas finanças saudáveis.</p>
                    
                    <p>Recomendações:</p>
                    <ul>
                        <li>Revise suas despesas recentes</li>
                        <li>Identifique gastos desnecessários</li>
                        <li>Ajuste seu planejamento se necessário</li>
                        <li>Considere reduzir despesas nas próximas semanas</li>
                    </ul>

                    <p>Acesse o FormuladoBolso para mais detalhes e ajustar seu planejamento.</p>
                </div>
                <div class="footer">
                    <p>FormuladoBolso - Seu gerenciador financeiro pessoal</p>
                </div>
            </div>
        </body>
        </html>
        """

    def _get_on_track_template(
        self,
        user_name: str,
        planning_name: str,
        target_amount: float,
        actual_amount: float,
        percentage: float,
    ) -> str:
        """Template HTML para quando está no planejamento"""
        remaining = target_amount - actual_amount
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #28a745; color: white; padding: 20px; text-align: center; border-radius: 5px 5px 0 0; }}
                .content {{ background-color: #f8f9fa; padding: 20px; border-radius: 0 0 5px 5px; }}
                .success {{ background-color: #d4edda; border-left: 4px solid #28a745; padding: 15px; margin: 20px 0; }}
                .stats {{ display: flex; justify-content: space-around; margin: 20px 0; }}
                .stat-box {{ background-color: white; padding: 15px; border-radius: 5px; text-align: center; flex: 1; margin: 0 5px; }}
                .stat-value {{ font-size: 24px; font-weight: bold; color: #28a745; }}
                .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎉 Parabéns!</h1>
                </div>
                <div class="content">
                    <p>Olá, <strong>{user_name}</strong>!</p>
                    
                    <div class="success">
                        <h2>Você está no caminho certo! 🎯</h2>
                        <p>O planejamento <strong>"{planning_name}"</strong> está dentro do previsto!</p>
                    </div>

                    <div class="stats">
                        <div class="stat-box">
                            <div class="stat-label">Meta</div>
                            <div class="stat-value">R$ {target_amount:,.2f}</div>
                        </div>
                        <div class="stat-box">
                            <div class="stat-label">Gasto Real</div>
                            <div class="stat-value">R$ {actual_amount:,.2f}</div>
                        </div>
                        <div class="stat-box">
                            <div class="stat-label">Restante</div>
                            <div class="stat-value">R$ {remaining:,.2f}</div>
                        </div>
                    </div>

                    <p><strong>Você está usando apenas {percentage:.1f}% do seu planejamento!</strong></p>
                    
                    <p>Continue assim! Você está gerenciando muito bem suas finanças. Mantenha o foco e continue seguindo seu planejamento.</p>
                    
                    <p>Dicas para continuar no caminho certo:</p>
                    <ul>
                        <li>Continue monitorando seus gastos</li>
                        <li>Mantenha o controle das despesas</li>
                        <li>Celebre suas conquistas financeiras</li>
                        <li>Considere investir o que sobrar</li>
                    </ul>

                    <p>Acesse o FormuladoBolso para ver mais detalhes do seu planejamento.</p>
                </div>
                <div class="footer">
                    <p>FormuladoBolso - Seu gerenciador financeiro pessoal</p>
                </div>
            </div>
        </body>
        </html>
        """

    async def send_password_reset_email(
        self,
        to_email: str,
        user_name: str,
        reset_token: str,
        reset_url: str,
    ) -> bool:
        """Envia email de recuperação de senha"""
        subject = "🔐 Recuperação de Senha - FormuladoBolso"
        html_content = self._get_password_reset_template(
            user_name, reset_token, reset_url
        )
        return await self.send_email(to_email, subject, html_content)

    def _get_password_reset_template(
        self,
        user_name: str,
        reset_token: str,
        reset_url: str,
    ) -> str:
        """Template HTML para recuperação de senha"""
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
                .token {{ background-color: #e9ecef; padding: 10px; border-radius: 5px; font-family: monospace; word-break: break-all; margin: 10px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔐 Recuperação de Senha</h1>
                </div>
                <div class="content">
                    <p>Olá, <strong>{user_name}</strong>!</p>
                    
                    <p>Recebemos uma solicitação para redefinir a senha da sua conta no FormuladoBolso.</p>
                    
                    <p>Clique no botão abaixo para redefinir sua senha:</p>
                    
                    <div style="text-align: center;">
                        <a href="{reset_url}" class="button">Redefinir Senha</a>
                    </div>
                    
                    <p>Ou copie e cole o link abaixo no seu navegador:</p>
                    <div class="token">{reset_url}</div>
                    
                    <div class="info-box">
                        <strong>⚠️ Importante:</strong>
                        <ul>
                            <li>Este link é válido por <strong>1 hora</strong></li>
                            <li>Se você não solicitou esta recuperação, ignore este email</li>
                            <li>Nunca compartilhe este link com ninguém</li>
                        </ul>
                    </div>
                    
                    <p>Se você não solicitou esta recuperação de senha, pode ignorar este email com segurança.</p>
                    
                    <p>Em caso de dúvidas, entre em contato conosco.</p>
                </div>
                <div class="footer">
                    <p>FormuladoBolso - Seu gerenciador financeiro pessoal</p>
                    <p>Este é um email automático, por favor não responda.</p>
                </div>
            </div>
        </body>
        </html>
        """

