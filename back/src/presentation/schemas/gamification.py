from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from decimal import Decimal


class BadgeResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    badge_type: str
    icon: Optional[str] = None
    color: Optional[str] = None
    points: int
    rarity: str

    class Config:
        from_attributes = True


class UserBadgeResponse(BaseModel):
    id: UUID
    badge: BadgeResponse
    earned_at: datetime
    progress: int

    class Config:
        from_attributes = True


class UserLevelResponse(BaseModel):
    id: UUID
    level: int
    experience_points: int
    total_points: int
    streak_days: int
    last_activity_date: Optional[datetime] = None
    next_level_points: int
    progress_to_next_level: float

    class Config:
        from_attributes = True


class ChallengeResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    challenge_type: str
    target_value: Optional[Decimal] = None
    target_metric: Optional[str] = None
    reward_points: int
    start_date: datetime
    end_date: datetime
    badge_id: Optional[UUID] = None

    class Config:
        from_attributes = True


class UserChallengeResponse(BaseModel):
    id: UUID
    challenge: ChallengeResponse
    current_value: Decimal
    progress_percentage: int
    is_completed: bool
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class LeaderboardEntry(BaseModel):
    user_id: UUID
    username: str
    level: int
    total_points: int
    rank: int

