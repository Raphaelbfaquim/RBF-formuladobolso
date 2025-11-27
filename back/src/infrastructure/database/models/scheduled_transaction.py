from sqlalchemy import Column, String, Numeric, DateTime, ForeignKey, Enum as SQLEnum, Text, Boolean, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
import pytz
import enum

from src.infrastructure.database.base import Base


class RecurrenceType(str, enum.Enum):
    NONE = "none"  # Não recorrente
    DAILY = "daily"  # Diária
    WEEKLY = "weekly"  # Semanal
    MONTHLY = "monthly"  # Mensal
    YEARLY = "yearly"  # Anual


class ScheduledTransactionStatus(str, enum.Enum):
    ACTIVE = "active"  # Ativa
    PAUSED = "paused"  # Pausada
    COMPLETED = "completed"  # Concluída
    CANCELLED = "cancelled"  # Cancelada


class ScheduledTransaction(Base):
    __tablename__ = "scheduled_transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    description = Column(String(500), nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    transaction_type = Column(String(20), nullable=False)  # income, expense, transfer (usando string para evitar dependência circular)
    status = Column(SQLEnum(ScheduledTransactionStatus), default=ScheduledTransactionStatus.ACTIVE, nullable=False)
    
    # Data e recorrência
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=True)  # Data final (opcional)
    next_execution_date = Column(DateTime(timezone=True), nullable=False)
    recurrence_type = Column(SQLEnum(RecurrenceType), default=RecurrenceType.NONE, nullable=False)
    recurrence_day = Column(Integer, nullable=True)  # Dia do mês para mensal
    recurrence_weekday = Column(Integer, nullable=True)  # Dia da semana para semanal
    
    # Execução
    execution_count = Column(Integer, default=0, nullable=False)
    max_executions = Column(Integer, nullable=True)  # Limite de execuções (None = infinito)
    last_execution_date = Column(DateTime(timezone=True), nullable=True)
    
    # Relacionamentos
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=False)
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"), nullable=True)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id"), nullable=True)
    
    # Configurações
    auto_execute = Column(Boolean, default=False, nullable=False)  # Executar automaticamente
    notes = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(pytz.UTC), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(pytz.UTC), onupdate=lambda: datetime.now(pytz.UTC), nullable=False)

    # Relacionamentos
    user = relationship("User", backref="scheduled_transactions")
    account = relationship("Account", backref="scheduled_transactions")
    category = relationship("Category", backref="scheduled_transactions")
    workspace = relationship("Workspace", backref="scheduled_transactions")


class TransactionExecution(Base):
    """Histórico de execuções de transações agendadas"""
    __tablename__ = "transaction_executions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    scheduled_transaction_id = Column(UUID(as_uuid=True), ForeignKey("scheduled_transactions.id"), nullable=False)
    transaction_id = Column(UUID(as_uuid=True), ForeignKey("transactions.id"), nullable=True)  # Transação criada
    execution_date = Column(DateTime(timezone=True), nullable=False)
    status = Column(String(20), default="success", nullable=False)  # success, failed
    error_message = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(pytz.UTC), nullable=False)

    # Relacionamentos
    scheduled_transaction = relationship("ScheduledTransaction", backref="executions")
    transaction = relationship("Transaction", backref="execution_history")

