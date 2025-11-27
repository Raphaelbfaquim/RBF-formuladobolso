from sqlalchemy import Column, String, Numeric, Boolean, DateTime, ForeignKey, Enum as SQLEnum, Text, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
import pytz
import enum

from src.infrastructure.database.base import Base


class BillType(str, enum.Enum):
    EXPENSE = "expense"  # Conta a pagar
    INCOME = "income"  # Conta a receber


class BillStatus(str, enum.Enum):
    PENDING = "pending"  # Pendente
    PAID = "paid"  # Paga
    RECEIVED = "received"  # Recebida
    OVERDUE = "overdue"  # Vencida
    CANCELLED = "cancelled"  # Cancelada


class RecurrenceType(str, enum.Enum):
    NONE = "none"  # Sem recorrência
    DAILY = "daily"  # Diária
    WEEKLY = "weekly"  # Semanal
    MONTHLY = "monthly"  # Mensal
    YEARLY = "yearly"  # Anual


class Bill(Base):
    __tablename__ = "bills"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    bill_type = Column(SQLEnum(BillType), nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    due_date = Column(DateTime(timezone=True), nullable=False)
    payment_date = Column(DateTime(timezone=True), nullable=True)  # Data de pagamento/recebimento
    status = Column(SQLEnum(BillStatus), default=BillStatus.PENDING, nullable=False)
    
    # Recorrência
    is_recurring = Column(Boolean, default=False, nullable=False)
    recurrence_type = Column(SQLEnum(RecurrenceType), default=RecurrenceType.NONE, nullable=False)
    recurrence_day = Column(Integer, nullable=True)  # Dia do mês para recorrência mensal
    recurrence_end_date = Column(DateTime(timezone=True), nullable=True)  # Data fim da recorrência
    
    # Relacionamentos
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=True)
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"), nullable=True)
    transaction_id = Column(UUID(as_uuid=True), ForeignKey("transactions.id"), nullable=True)  # Transação gerada
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(pytz.UTC), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(pytz.UTC), onupdate=lambda: datetime.now(pytz.UTC), nullable=False)

    # Relacionamentos
    user = relationship("User", back_populates="bills")
    account = relationship("Account")
    category = relationship("Category")
    transaction = relationship("Transaction")

