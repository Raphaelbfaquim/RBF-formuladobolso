from pydantic import BaseModel, EmailStr
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from src.infrastructure.database.models.user import FamilyMemberRole
from src.infrastructure.database.models.family_permission import ModulePermission


class FamilyCreate(BaseModel):
    name: str
    description: Optional[str] = None


class FamilyResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    created_by: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class FamilyMemberInvite(BaseModel):
    user_email: EmailStr
    role: FamilyMemberRole = FamilyMemberRole.MEMBER


class FamilyMemberResponse(BaseModel):
    id: UUID
    family_id: UUID
    user_id: UUID
    role: FamilyMemberRole
    joined_at: datetime
    user_username: Optional[str] = None
    user_email: Optional[str] = None

    class Config:
        from_attributes = True


class ChatMessageCreate(BaseModel):
    family_id: UUID
    message: str


class ChatMessageResponse(BaseModel):
    id: UUID
    family_id: UUID
    user_id: UUID
    message: str
    is_system_message: bool
    created_at: datetime
    user_username: Optional[str] = None

    class Config:
        from_attributes = True


class PermissionUpdate(BaseModel):
    module: ModulePermission
    can_view: bool = True
    can_edit: bool = False
    can_delete: bool = False
    
    @classmethod
    def model_validate(cls, obj, **kwargs):
        """Valida e converte o módulo para o enum correto"""
        if isinstance(obj, dict) and 'module' in obj:
            module = obj['module']
            if isinstance(module, str):
                # Converter string para enum (case-insensitive)
                module_lower = module.lower()
                try:
                    obj['module'] = ModulePermission(module_lower)
                except ValueError:
                    # Tentar pelo nome do enum (ex: "TRANSACTIONS" -> ModulePermission.TRANSACTIONS)
                    module_upper = module.upper()
                    if hasattr(ModulePermission, module_upper):
                        obj['module'] = getattr(ModulePermission, module_upper)
                    else:
                        raise ValueError(f"Módulo inválido: {module}")
        return super().model_validate(obj, **kwargs)


class MemberPermissionResponse(BaseModel):
    id: UUID
    family_member_id: UUID
    module: str
    can_view: bool
    can_edit: bool
    can_delete: bool

    class Config:
        from_attributes = True


class FamilyMemberWithPermissionsResponse(BaseModel):
    id: UUID
    family_id: UUID
    user_id: UUID
    role: FamilyMemberRole
    joined_at: datetime
    user_username: Optional[str] = None
    user_email: Optional[str] = None
    permissions: List[MemberPermissionResponse] = []

    class Config:
        from_attributes = True


class InviteTokenResponse(BaseModel):
    valid: bool
    email: Optional[str] = None
    family_name: Optional[str] = None
    inviter_name: Optional[str] = None
    role: Optional[str] = None
    expires_at: Optional[datetime] = None
    message: Optional[str] = None


class InviteRegisterRequest(BaseModel):
    token: str
    username: str
    password: str
    full_name: Optional[str] = None
    two_factor_code: Optional[str] = None  # Código 2FA se necessário

