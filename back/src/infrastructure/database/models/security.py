from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
import pytz
import enum

from src.infrastructure.database.base import Base


class TwoFactorMethod(str, enum.Enum):
    TOTP = "totp"  # Authenticator app
    SMS = "sms"  # SMS
    EMAIL = "email"  # Email


class TwoFactorAuth(Base):
    __tablename__ = "two_factor_auth"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=False)
    is_enabled = Column(Boolean, default=False, nullable=False)
    method = Column(SQLEnum(TwoFactorMethod), nullable=True)
    secret = Column(String(255), nullable=True)  # Secret para TOTP
    backup_codes = Column(Text, nullable=True)  # JSON com códigos de backup
    phone_number = Column(String(20), nullable=True)  # Para SMS
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(pytz.UTC), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(pytz.UTC), onupdate=lambda: datetime.now(pytz.UTC), nullable=False)

    # Relacionamentos
    user = relationship("User", backref="two_factor_auth")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    action = Column(String(100), nullable=False)  # login, create_transaction, update_account, etc.
    resource_type = Column(String(50), nullable=True)  # transaction, account, etc.
    resource_id = Column(UUID(as_uuid=True), nullable=True)
    ip_address = Column(String(45), nullable=True)  # IPv4 ou IPv6
    user_agent = Column(String(500), nullable=True)
    details = Column(Text, nullable=True)  # JSON com detalhes adicionais
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(pytz.UTC), nullable=False)

    # Relacionamentos
    user = relationship("User", backref="audit_logs")


class SecurityAlert(Base):
    __tablename__ = "security_alerts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    alert_type = Column(String(50), nullable=False)  # suspicious_login, password_change, etc.
    message = Column(Text, nullable=False)
    severity = Column(String(20), default="info", nullable=False)  # info, warning, critical
    is_read = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(pytz.UTC), nullable=False)

    # Relacionamentos
    user = relationship("User", backref="security_alerts")

