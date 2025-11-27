from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
import pytz
import enum

from src.infrastructure.database.base import Base


class ModulePermission(str, enum.Enum):
    """Módulos disponíveis para permissão"""
    DASHBOARD = "dashboard"
    TRANSACTIONS = "transactions"
    ACCOUNTS = "accounts"
    CATEGORIES = "categories"
    PLANNING = "planning"
    GOALS = "goals"
    BILLS = "bills"
    TRANSFERS = "transfers"
    CALENDAR = "calendar"
    INVESTMENTS = "investments"
    RECEIPTS = "receipts"
    REPORTS = "reports"
    WORKSPACES = "workspaces"
    AI = "ai"
    INSIGHTS = "insights"
    OPEN_BANKING = "open_banking"
    EDUCATION = "education"
    GAMIFICATION = "gamification"
    FAMILY = "family"
    SETTINGS = "settings"


class FamilyMemberPermission(Base):
    """Permissões de módulos para membros da família"""
    __tablename__ = "family_member_permissions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    family_member_id = Column(UUID(as_uuid=True), ForeignKey("family_members.id"), nullable=False)
    module = Column(
        SQLEnum(
            ModulePermission,
            values_callable=lambda obj: [e.value for e in obj],
            name='modulepermission',
            create_type=False
        ),
        nullable=False
    )
    can_view = Column(Boolean, default=True, nullable=False)
    can_edit = Column(Boolean, default=False, nullable=False)
    can_delete = Column(Boolean, default=False, nullable=False)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(pytz.UTC), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(pytz.UTC), onupdate=lambda: datetime.now(pytz.UTC), nullable=False)

    # Relacionamentos
    family_member = relationship("FamilyMember", backref="permissions")

