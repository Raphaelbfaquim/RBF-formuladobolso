from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Enum as SQLEnum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
import pytz
import enum

from src.infrastructure.database.base import Base


class WorkspaceType(str, enum.Enum):
    PERSONAL = "personal"  # Pessoal - só o dono vê
    FAMILY = "family"  # Familiar - compartilhado com família
    SHARED = "shared"  # Compartilhado (futuro)


class Workspace(Base):
    __tablename__ = "workspaces"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    workspace_type = Column(SQLEnum(WorkspaceType), nullable=False, default=WorkspaceType.PERSONAL)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    family_id = Column(UUID(as_uuid=True), ForeignKey("families.id"), nullable=True)  # Se for tipo FAMILY
    is_active = Column(Boolean, default=True, nullable=False)
    color = Column(String(7), nullable=True)  # Cor para identificação visual
    icon = Column(String(50), nullable=True)  # Ícone para identificação
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(pytz.UTC), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(pytz.UTC), onupdate=lambda: datetime.now(pytz.UTC), nullable=False)

    # Relacionamentos
    owner = relationship("User", backref="owned_workspaces")
    family = relationship("Family", backref="workspaces")


class WorkspaceMember(Base):
    """Membros com acesso ao workspace (para workspaces compartilhados)"""
    __tablename__ = "workspace_members"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    can_edit = Column(Boolean, default=True, nullable=False)  # Pode editar ou só visualizar
    can_delete = Column(Boolean, default=False, nullable=False)  # Pode deletar
    joined_at = Column(DateTime(timezone=True), default=lambda: datetime.now(pytz.UTC), nullable=False)

    # Relacionamentos
    workspace = relationship("Workspace", backref="members")
    user = relationship("User", backref="workspace_memberships")

