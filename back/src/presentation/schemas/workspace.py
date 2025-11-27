from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from src.infrastructure.database.models.workspace import WorkspaceType


class WorkspaceCreate(BaseModel):
    name: str
    description: Optional[str] = None
    workspace_type: WorkspaceType = WorkspaceType.PERSONAL
    family_id: Optional[UUID] = None  # Se for tipo FAMILY
    color: Optional[str] = None
    icon: Optional[str] = None


class WorkspaceUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    color: Optional[str] = None
    icon: Optional[str] = None


class WorkspaceResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    workspace_type: WorkspaceType
    owner_id: UUID
    family_id: Optional[UUID]
    is_active: bool
    color: Optional[str]
    icon: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WorkspaceShareRequest(BaseModel):
    user_id: UUID
    can_edit: bool = True
    can_delete: bool = False

