from sqlalchemy import Column, String, Numeric, DateTime, ForeignKey, Enum as SQLEnum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
import pytz
import enum

from src.infrastructure.database.base import Base


class TransferStatus(str, enum.Enum):
    PENDING = "pending"  # Pendente
    COMPLETED = "completed"  # Concluída
    CANCELLED = "cancelled"  # Cancelada
    FAILED = "failed"  # Falhou


class Transfer(Base):
    __tablename__ = "transfers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    description = Column(String(500), nullable=True)
    amount = Column(Numeric(15, 2), nullable=False)
    status = Column(SQLEnum(TransferStatus), default=TransferStatus.PENDING, nullable=False)
    transfer_date = Column(DateTime(timezone=True), nullable=False)
    scheduled_date = Column(DateTime(timezone=True), nullable=True)  # Para agendamentos
    notes = Column(Text, nullable=True)
    
    # Contas envolvidas
    from_account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=False)
    to_account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=False)
    
    # Usuário e workspace
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id"), nullable=True)
    
    # Transações criadas (para rastreamento)
    from_transaction_id = Column(UUID(as_uuid=True), ForeignKey("transactions.id"), nullable=True)
    to_transaction_id = Column(UUID(as_uuid=True), ForeignKey("transactions.id"), nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(pytz.UTC), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(pytz.UTC), onupdate=lambda: datetime.now(pytz.UTC), nullable=False)

    # Relacionamentos
    from_account = relationship("Account", foreign_keys=[from_account_id], backref="outgoing_transfers")
    to_account = relationship("Account", foreign_keys=[to_account_id], backref="incoming_transfers")
    user = relationship("User", backref="transfers")
    workspace = relationship("Workspace", backref="transfers")
    from_transaction = relationship("Transaction", foreign_keys=[from_transaction_id])
    to_transaction = relationship("Transaction", foreign_keys=[to_transaction_id])

