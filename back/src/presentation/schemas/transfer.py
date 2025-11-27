from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime
from decimal import Decimal


class TransferCreate(BaseModel):
    from_account_id: UUID
    to_account_id: UUID
    amount: Decimal = Field(..., gt=0)
    description: Optional[str] = None
    transfer_date: datetime
    workspace_id: Optional[UUID] = None
    scheduled_date: Optional[datetime] = None  # Para agendamentos
    notes: Optional[str] = None


class TransferResponse(BaseModel):
    id: UUID
    description: Optional[str]
    amount: Decimal
    status: str
    transfer_date: datetime
    scheduled_date: Optional[datetime]
    notes: Optional[str]
    from_account_id: UUID
    to_account_id: UUID
    user_id: UUID
    workspace_id: Optional[UUID]
    from_account_name: Optional[str] = None
    to_account_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

