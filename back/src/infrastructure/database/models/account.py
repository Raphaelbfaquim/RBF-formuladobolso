from sqlalchemy import Column, String, Numeric, Boolean, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
import pytz
import enum

from src.infrastructure.database.base import Base


class AccountType(str, enum.Enum):
    CHECKING = "checking"  # Conta corrente
    SAVINGS = "savings"  # Poupança
    CREDIT_CARD = "credit_card"  # Cartão de crédito
    CASH = "cash"  # Dinheiro
    OTHER = "other"  # Outros


class Account(Base):
    __tablename__ = "accounts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(String(500), nullable=True)
    account_type = Column(SQLEnum(AccountType), nullable=False)
    balance = Column(Numeric(15, 2), default=0, nullable=False)
    initial_balance = Column(Numeric(15, 2), default=0, nullable=False)
    currency = Column(String(3), default="BRL", nullable=False)
    bank_name = Column(String(255), nullable=True)
    account_number = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relacionamentos
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    family_id = Column(UUID(as_uuid=True), ForeignKey("families.id"), nullable=True)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id"), nullable=True)  # Workspace/Contexto
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(pytz.UTC), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(pytz.UTC), onupdate=lambda: datetime.now(pytz.UTC), nullable=False)

    # Relacionamentos
    owner = relationship("User", back_populates="accounts")
    family = relationship("Family", back_populates="accounts")
    transactions = relationship("Transaction", back_populates="account", cascade="all, delete-orphan")

