from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Enum as SQLEnum, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
import pytz
import enum

from src.infrastructure.database.base import Base


class BankConnectionStatus(str, enum.Enum):
    PENDING = "pending"  # Pendente
    CONNECTED = "connected"  # Conectado
    DISCONNECTED = "disconnected"  # Desconectado
    ERROR = "error"  # Erro


class BankConnection(Base):
    __tablename__ = "bank_connections"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    bank_name = Column(String(255), nullable=False)
    bank_code = Column(String(20), nullable=True)  # Código do banco (ex: 001, 341)
    account_number = Column(String(100), nullable=True)
    account_type = Column(String(50), nullable=True)  # checking, savings, etc.
    status = Column(SQLEnum(BankConnectionStatus), default=BankConnectionStatus.PENDING, nullable=False)
    consent_token = Column(Text, nullable=True)  # Token de consentimento Open Banking
    last_sync_at = Column(DateTime(timezone=True), nullable=True)
    sync_error = Column(Text, nullable=True)
    bank_metadata = Column(JSON, nullable=True)  # Dados adicionais do banco (renomeado de 'metadata' para evitar conflito)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(pytz.UTC), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(pytz.UTC), onupdate=lambda: datetime.now(pytz.UTC), nullable=False)

    # Relacionamentos
    user = relationship("User", backref="bank_connections")

