from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime
from decimal import Decimal


class BillBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    bill_type: str
    amount: Decimal = Field(..., gt=0)
    due_date: datetime
    account_id: Optional[UUID] = None
    category_id: Optional[UUID] = None


class BillCreate(BillBase):
    is_recurring: bool = False
    recurrence_type: str = "none"
    recurrence_day: Optional[int] = None
    recurrence_end_date: Optional[datetime] = None


class BillUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    amount: Optional[Decimal] = Field(None, gt=0)
    due_date: Optional[datetime] = None
    status: Optional[str] = None
    payment_date: Optional[datetime] = None
    account_id: Optional[UUID] = None
    category_id: Optional[UUID] = None


class BillResponse(BillBase):
    id: UUID
    status: str
    payment_date: Optional[datetime] = None
    is_recurring: bool
    recurrence_type: str
    recurrence_day: Optional[int] = None
    recurrence_end_date: Optional[datetime] = None
    transaction_id: Optional[UUID] = None
    user_id: UUID
    days_until_due: Optional[int] = None
    is_overdue: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

