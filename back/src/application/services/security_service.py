from typing import Optional, Dict, List
from uuid import UUID
from datetime import datetime
import pytz
import pyotp
import qrcode
from io import BytesIO
from src.infrastructure.database.models.security import TwoFactorAuth, AuditLog, SecurityAlert, TwoFactorMethod
from sqlalchemy.ext.asyncio import AsyncSession


class SecurityService:
    """Serviço de segurança avançada"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def enable_2fa(self, user_id: UUID, method: str = "totp", user_email: Optional[str] = None) -> Dict:
        """Habilita 2FA para usuário"""
        # Gerar secret para TOTP
        secret = pyotp.random_base32()
        
        # Criar URI para QR Code
        totp = pyotp.TOTP(secret)
        # Usar email se disponível, senão usar ID
        name = user_email if user_email else f"user_{user_id}"
        uri = totp.provisioning_uri(
            name=name,
            issuer_name="FormuladoBolso"
        )
        
        # Gerar QR Code
        try:
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(uri)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            qr_code_data = buffer.getvalue()
            
            print(f"✅ QR Code gerado com sucesso (tamanho: {len(qr_code_data)} bytes)")
            print(f"   URI: {uri}")
            
            return {
                "secret": secret,
                "qr_code": qr_code_data,
                "backup_codes": self._generate_backup_codes(),
            }
        except Exception as e:
            print(f"❌ Erro ao gerar QR Code: {e}")
            import traceback
            traceback.print_exc()
            # Retornar mesmo sem QR code para não quebrar o fluxo
            return {
                "secret": secret,
                "qr_code": None,
                "backup_codes": self._generate_backup_codes(),
            }

    def _generate_backup_codes(self) -> List[str]:
        """Gera códigos de backup"""
        import secrets
        return [secrets.token_hex(4).upper() for _ in range(10)]

    async def verify_2fa(self, user_id: UUID, code: str) -> bool:
        """Verifica código 2FA"""
        # TODO: Buscar secret do banco e verificar
        return False

    async def log_action(
        self,
        user_id: Optional[UUID],
        action: str,
        resource_type: Optional[str] = None,
        resource_id: Optional[UUID] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        details: Optional[Dict] = None,
    ):
        """Registra ação no log de auditoria"""
        import json
        
        log = AuditLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=ip_address,
            user_agent=user_agent,
            details=json.dumps(details) if details else None,
        )
        
        self.session.add(log)
        await self.session.commit()

    async def create_security_alert(
        self,
        user_id: UUID,
        alert_type: str,
        message: str,
        severity: str = "info",
    ):
        """Cria alerta de segurança"""
        alert = SecurityAlert(
            user_id=user_id,
            alert_type=alert_type,
            message=message,
            severity=severity,
        )
        
        self.session.add(alert)
        await self.session.commit()

