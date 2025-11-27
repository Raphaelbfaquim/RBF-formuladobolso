from sqlalchemy import Column, String, Numeric, DateTime, ForeignKey, Enum as SQLEnum, Text, Integer, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime, date
import pytz
import enum

from src.infrastructure.database.base import Base


class PlanningType(str, enum.Enum):
    MONTHLY = "monthly"  # Mensal
    WEEKLY = "weekly"  # Semanal
    DAILY = "daily"  # Diário
    ANNUAL = "annual"  # Anual


class Planning(Base):
    __tablename__ = "plannings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    planning_type = Column(SQLEnum(PlanningType), nullable=False)
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)
    target_amount = Column(Numeric(15, 2), nullable=True)  # Valor alvo (para receitas/despesas)
    actual_amount = Column(Numeric(15, 2), default=0, nullable=False)  # Valor atual alcançado
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relacionamentos
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"), nullable=True)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id"), nullable=True)  # Workspace/Contexto
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(pytz.UTC), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(pytz.UTC), onupdate=lambda: datetime.now(pytz.UTC), nullable=False)

    # Relacionamentos
    user = relationship("User", back_populates="plannings")
    category = relationship("Category")
    monthly_details = relationship("MonthlyPlanning", back_populates="planning", cascade="all, delete-orphan")
    weekly_details = relationship("WeeklyPlanning", back_populates="planning", cascade="all, delete-orphan")
    daily_details = relationship("DailyPlanning", back_populates="planning", cascade="all, delete-orphan")
    annual_details = relationship("AnnualPlanning", back_populates="planning", cascade="all, delete-orphan")


class MonthlyPlanning(Base):
    __tablename__ = "monthly_plannings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    planning_id = Column(UUID(as_uuid=True), ForeignKey("plannings.id"), nullable=False)
    month = Column(Integer, nullable=False)  # 1-12
    year = Column(Integer, nullable=False)
    target_amount = Column(Numeric(15, 2), nullable=False)
    actual_amount = Column(Numeric(15, 2), default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(pytz.UTC), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(pytz.UTC), onupdate=lambda: datetime.now(pytz.UTC), nullable=False)

    planning = relationship("Planning", back_populates="monthly_details")


class WeeklyPlanning(Base):
    __tablename__ = "weekly_plannings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    planning_id = Column(UUID(as_uuid=True), ForeignKey("plannings.id"), nullable=False)
    week_number = Column(Integer, nullable=False)  # Semana do ano (1-52)
    year = Column(Integer, nullable=False)
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)
    target_amount = Column(Numeric(15, 2), nullable=False)
    actual_amount = Column(Numeric(15, 2), default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(pytz.UTC), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(pytz.UTC), onupdate=lambda: datetime.now(pytz.UTC), nullable=False)

    planning = relationship("Planning", back_populates="weekly_details")


class DailyPlanning(Base):
    __tablename__ = "daily_plannings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    planning_id = Column(UUID(as_uuid=True), ForeignKey("plannings.id"), nullable=False)
    date = Column(DateTime(timezone=True), nullable=False)
    target_amount = Column(Numeric(15, 2), nullable=False)
    actual_amount = Column(Numeric(15, 2), default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(pytz.UTC), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(pytz.UTC), onupdate=lambda: datetime.now(pytz.UTC), nullable=False)

    planning = relationship("Planning", back_populates="daily_details")


class AnnualPlanning(Base):
    __tablename__ = "annual_plannings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    planning_id = Column(UUID(as_uuid=True), ForeignKey("plannings.id"), nullable=False)
    year = Column(Integer, nullable=False)
    target_amount = Column(Numeric(15, 2), nullable=False)
    actual_amount = Column(Numeric(15, 2), default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(pytz.UTC), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(pytz.UTC), onupdate=lambda: datetime.now(pytz.UTC), nullable=False)

    planning = relationship("Planning", back_populates="annual_details")
    quarterly_goals = relationship("QuarterlyGoal", back_populates="annual_planning", cascade="all, delete-orphan")


class QuarterlyGoal(Base):
    __tablename__ = "quarterly_goals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    annual_planning_id = Column(UUID(as_uuid=True), ForeignKey("annual_plannings.id"), nullable=False)
    quarter = Column(Integer, nullable=False)  # 1-4
    target_amount = Column(Numeric(15, 2), nullable=False)
    actual_amount = Column(Numeric(15, 2), default=0, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(pytz.UTC), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(pytz.UTC), onupdate=lambda: datetime.now(pytz.UTC), nullable=False)

    annual_planning = relationship("AnnualPlanning", back_populates="quarterly_goals")

