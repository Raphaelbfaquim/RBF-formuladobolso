from pydantic import BaseModel
from typing import Optional, List, Dict
from uuid import UUID
from datetime import datetime


class AdminDashboardStats(BaseModel):
    total_users: int
    active_users: int
    inactive_users: int
    new_users_last_7_days: int
    new_users_last_30_days: int
    total_families: int
    total_transactions: int
    total_volume: float
    users_with_2fa: int
    unverified_users: int


class AdminDashboardResponse(BaseModel):
    stats: AdminDashboardStats
    recent_users: List[Dict]
    security_alerts_count: int
    recent_activities: List[Dict]


class UserListFilters(BaseModel):
    search: Optional[str] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None
    role: Optional[str] = None
    page: int = 1
    page_size: int = 20


class UserDetailResponse(BaseModel):
    id: UUID
    email: str
    username: str
    full_name: Optional[str]
    is_active: bool
    is_verified: bool
    role: str
    created_at: datetime
    updated_at: datetime
    families_count: int
    accounts_count: int
    transactions_count: int
    last_login: Optional[datetime]
    has_2fa: bool


class UpdateUserRequest(BaseModel):
    email: Optional[str] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None
    role: Optional[str] = None

