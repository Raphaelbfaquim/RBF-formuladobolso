from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, ENUM
import uuid
from datetime import datetime, timedelta
import pytz
import enum

from src.infrastructure.database.base import Base
from src.infrastructure.database.models.user import FamilyMemberRole


class FamilyInviteStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    
    def __str__(self):
        return self.value


class FamilyInvite(Base):
    """Convite para família com token de cadastro"""
    __tablename__ = "family_invites"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    family_id = Column(UUID(as_uuid=True), ForeignKey("families.id"), nullable=False)
    invited_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    email = Column(String(255), nullable=False, index=True)
    token = Column(String(255), unique=True, nullable=False, index=True)
    role = Column(SQLEnum(FamilyMemberRole), default=FamilyMemberRole.MEMBER, nullable=False)
    status = Column(ENUM(FamilyInviteStatus, name='familyinvitestatus', create_type=False, values_callable=lambda obj: [e.value for e in obj]), default=FamilyInviteStatus.PENDING, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    accepted_at = Column(DateTime(timezone=True), nullable=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)  # Preenchido quando aceito
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(pytz.UTC), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(pytz.UTC), onupdate=lambda: datetime.now(pytz.UTC), nullable=False)

    # Relacionamentos
    family = relationship("Family", backref="invites")
    inviter = relationship("User", foreign_keys=[invited_by], backref="sent_invites")
    user = relationship("User", foreign_keys=[user_id], backref="received_invites")

