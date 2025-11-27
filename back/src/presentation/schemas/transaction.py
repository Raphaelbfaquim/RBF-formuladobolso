from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime
from decimal import Decimal


class TransactionBase(BaseModel):
    description: str = Field(..., min_length=1, max_length=500)
    amount: Decimal = Field(..., gt=0)
    transaction_type: str
    transaction_date: datetime
    notes: Optional[str] = None


class TransactionCreate(TransactionBase):
    account_id: UUID
    category_id: Optional[UUID] = None
    receipt_id: Optional[UUID] = None
    status: str = "completed"
    workspace_id: Optional[UUID] = None


class TransactionUpdate(BaseModel):
    description: Optional[str] = Field(None, min_length=1, max_length=500)
    amount: Optional[Decimal] = Field(None, gt=0)
    transaction_date: Optional[datetime] = None
    status: Optional[str] = None
    category_id: Optional[UUID] = None
    notes: Optional[str] = None


class TransactionResponse(TransactionBase):
    id: UUID
    status: str
    user_id: UUID
    account_id: UUID
    category_id: Optional[UUID] = None
    receipt_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

