from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime
from decimal import Decimal


class ScheduledTransactionCreate(BaseModel):
    description: str
    amount: Decimal = Field(..., gt=0)
    transaction_type: str  # income, expense
    account_id: UUID
    start_date: datetime
    recurrence_type: str = "none"  # none, daily, weekly, monthly, yearly
    end_date: Optional[datetime] = None
    max_executions: Optional[int] = Field(None, ge=1)
    auto_execute: bool = False
    category_id: Optional[UUID] = None
    workspace_id: Optional[UUID] = None
    notes: Optional[str] = None
    recurrence_day: Optional[int] = Field(None, ge=1, le=31)  # Para mensal
    recurrence_weekday: Optional[int] = Field(None, ge=0, le=6)  # Para semanal (0=segunda)


class ScheduledTransactionResponse(BaseModel):
    id: UUID
    description: str
    amount: Decimal
    transaction_type: str
    status: str
    start_date: datetime
    end_date: Optional[datetime]
    next_execution_date: datetime
    recurrence_type: str
    execution_count: int
    max_executions: Optional[int]
    auto_execute: bool
    account_id: UUID
    category_id: Optional[UUID]
    workspace_id: Optional[UUID]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

