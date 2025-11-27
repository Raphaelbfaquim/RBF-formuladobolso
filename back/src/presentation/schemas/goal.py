from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from decimal import Decimal


class GoalBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    goal_type: str
    target_amount: Decimal = Field(..., gt=0)
    target_date: Optional[datetime] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    savings_category_id: Optional[UUID] = None  # Categoria de poupança vinculada
    auto_contribution_percentage: Optional[Decimal] = Field(None, ge=0, le=100)  # % da poupança (0-100)


class GoalCreate(GoalBase):
    pass


class GoalUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    target_amount: Optional[Decimal] = Field(None, gt=0)
    target_date: Optional[datetime] = None
    status: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    savings_category_id: Optional[UUID] = None
    auto_contribution_percentage: Optional[Decimal] = Field(None, ge=0, le=100)


class GoalResponse(GoalBase):
    id: UUID
    current_amount: Decimal
    status: str
    user_id: UUID
    percentage: float
    remaining_amount: Decimal
    days_remaining: Optional[int] = None
    estimated_completion_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class GoalContributionCreate(BaseModel):
    amount: Decimal = Field(..., gt=0)
    contribution_date: datetime
    notes: Optional[str] = None
    transaction_id: Optional[UUID] = None


class GoalContributionResponse(BaseModel):
    id: UUID
    goal_id: UUID
    amount: Decimal
    contribution_date: datetime
    notes: Optional[str] = None
    transaction_id: Optional[UUID] = None
    created_at: datetime

    class Config:
        from_attributes = True


class GoalProgressResponse(BaseModel):
    goal_id: UUID
    name: str
    target_amount: Decimal
    current_amount: Decimal
    percentage: float
    remaining_amount: Decimal
    days_remaining: Optional[int] = None
    estimated_completion_date: Optional[datetime] = None
    is_on_track: bool
    monthly_savings_needed: Optional[Decimal] = None

