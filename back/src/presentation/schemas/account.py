from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime
from decimal import Decimal


class AccountBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    account_type: str
    currency: str = Field(default="BRL", max_length=3)
    bank_name: Optional[str] = None
    account_number: Optional[str] = None


class AccountCreate(AccountBase):
    initial_balance: Decimal = Field(default=0, ge=0)


class AccountUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    bank_name: Optional[str] = None
    account_number: Optional[str] = None
    is_active: Optional[bool] = None


class AccountResponse(AccountBase):
    id: UUID
    balance: Decimal
    initial_balance: Decimal
    is_active: bool
    owner_id: Optional[UUID] = None
    family_id: Optional[UUID] = None
    workspace_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

