from sqlalchemy import Column, String, Numeric, DateTime, ForeignKey, Enum as SQLEnum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
import pytz
import enum

from src.infrastructure.database.base import Base


class TransactionType(str, enum.Enum):
    INCOME = "income"  # Receita
    EXPENSE = "expense"  # Despesa
    TRANSFER = "transfer"  # Transferência


class TransactionStatus(str, enum.Enum):
    PENDING = "pending"  # Pendente
    COMPLETED = "completed"  # Concluída
    CANCELLED = "cancelled"  # Cancelada


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    description = Column(String(500), nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    transaction_type = Column(SQLEnum(TransactionType), nullable=False)
    status = Column(SQLEnum(TransactionStatus), default=TransactionStatus.COMPLETED, nullable=False)
    transaction_date = Column(DateTime(timezone=True), nullable=False)
    notes = Column(Text, nullable=True)
    
    # Relacionamentos
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=False)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id"), nullable=True)  # Workspace/Contexto
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"), nullable=True)
    receipt_id = Column(UUID(as_uuid=True), ForeignKey("receipts.id"), nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(pytz.UTC), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(pytz.UTC), onupdate=lambda: datetime.now(pytz.UTC), nullable=False)

    # Relacionamentos
    user = relationship("User", back_populates="transactions")
    account = relationship("Account", back_populates="transactions")
    category = relationship("Category", back_populates="transactions")
    receipt = relationship("Receipt", back_populates="transactions")

