from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from decimal import Decimal


class PlanningBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    planning_type: str
    start_date: datetime
    end_date: datetime
    target_amount: Optional[Decimal] = None
    category_id: Optional[UUID] = None


class PlanningCreate(PlanningBase):
    pass


class PlanningUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    target_amount: Optional[Decimal] = None
    is_active: Optional[bool] = None
    category_id: Optional[UUID] = None


class PlanningResponse(PlanningBase):
    id: UUID
    actual_amount: Decimal
    is_active: bool
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PlanningProgressResponse(BaseModel):
    planning_id: UUID
    target_amount: Decimal
    actual_amount: Decimal
    percentage: float
    remaining_amount: Decimal
    is_on_track: bool


class MonthlyPlanningResponse(BaseModel):
    id: UUID
    planning_id: UUID
    month: int
    year: int
    target_amount: Decimal
    actual_amount: Decimal
    percentage: float

    class Config:
        from_attributes = True


class WeeklyPlanningResponse(BaseModel):
    id: UUID
    planning_id: UUID
    week_number: int
    year: int
    start_date: datetime
    end_date: datetime
    target_amount: Decimal
    actual_amount: Decimal
    percentage: float

    class Config:
        from_attributes = True


class DailyPlanningResponse(BaseModel):
    id: UUID
    planning_id: UUID
    date: datetime
    target_amount: Decimal
    actual_amount: Decimal
    percentage: float

    class Config:
        from_attributes = True


class QuarterlyGoalCreate(BaseModel):
    quarter: int = Field(..., ge=1, le=4)
    target_amount: Decimal = Field(..., gt=0)
    description: Optional[str] = None


class QuarterlyGoalResponse(BaseModel):
    id: UUID
    annual_planning_id: UUID
    quarter: int
    target_amount: Decimal
    actual_amount: Decimal
    percentage: float
    description: Optional[str] = None

    class Config:
        from_attributes = True


class AnnualPlanningResponse(BaseModel):
    id: UUID
    planning_id: UUID
    year: int
    target_amount: Decimal
    actual_amount: Decimal
    percentage: float
    quarterly_goals: List[QuarterlyGoalResponse] = []

    class Config:
        from_attributes = True

