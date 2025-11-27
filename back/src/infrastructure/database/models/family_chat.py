from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
import pytz

from src.infrastructure.database.base import Base


class FamilyChatMessage(Base):
    __tablename__ = "family_chat_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    family_id = Column(UUID(as_uuid=True), ForeignKey("families.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    message = Column(Text, nullable=False)
    is_system_message = Column(Boolean, default=False, nullable=False)  # Mensagens do sistema
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(pytz.UTC), nullable=False)

    # Relacionamentos
    family = relationship("Family", backref="chat_messages")
    user = relationship("User", backref="family_chat_messages")


class FamilyApproval(Base):
    __tablename__ = "family_approvals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    family_id = Column(UUID(as_uuid=True), ForeignKey("families.id"), nullable=False)
    transaction_id = Column(UUID(as_uuid=True), ForeignKey("transactions.id"), nullable=True)
    requested_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    amount = Column(String(50), nullable=False)  # Valor da transação que precisa aprovação
    description = Column(Text, nullable=True)
    status = Column(String(20), default="pending", nullable=False)  # pending, approved, rejected
    approved_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(pytz.UTC), nullable=False)

    # Relacionamentos
    family = relationship("Family", backref="approvals")
    transaction = relationship("Transaction")
    requester = relationship("User", foreign_keys=[requested_by], backref="requested_approvals")
    approver = relationship("User", foreign_keys=[approved_by], backref="approved_requests")

