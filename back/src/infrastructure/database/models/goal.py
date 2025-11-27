from sqlalchemy import Column, String, Numeric, Boolean, DateTime, ForeignKey, Enum as SQLEnum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
import pytz
import enum

from src.infrastructure.database.base import Base


class GoalType(str, enum.Enum):
    HOUSE = "house"  # Comprar casa
    CAR = "car"  # Comprar carro
    TRIP = "trip"  # Viagem
    WEDDING = "wedding"  # Casamento
    EDUCATION = "education"  # Educação
    EMERGENCY = "emergency"  # Emergência
    RETIREMENT = "retirement"  # Aposentadoria
    OTHER = "other"  # Outros


class GoalStatus(str, enum.Enum):
    ACTIVE = "active"  # Ativa
    PAUSED = "paused"  # Pausada
    COMPLETED = "completed"  # Concluída
    CANCELLED = "cancelled"  # Cancelada


class Goal(Base):
    __tablename__ = "goals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    goal_type = Column(SQLEnum(GoalType), nullable=False)
    target_amount = Column(Numeric(15, 2), nullable=False)
    current_amount = Column(Numeric(15, 2), default=0, nullable=False)
    target_date = Column(DateTime(timezone=True), nullable=True)  # Data objetivo
    status = Column(SQLEnum(GoalStatus), default=GoalStatus.ACTIVE, nullable=False)
    icon = Column(String(50), nullable=True)  # Emoji ou ícone
    color = Column(String(7), nullable=True)  # Cor em hex
    
    # Vinculação com categoria de poupança para contribuições automáticas
    savings_category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"), nullable=True)
    auto_contribution_percentage = Column(Numeric(5, 2), nullable=True)  # % da poupança que vai para esta meta (0-100)
    
    # Relacionamentos
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    savings_category = relationship("Category", foreign_keys=[savings_category_id])
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(pytz.UTC), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(pytz.UTC), onupdate=lambda: datetime.now(pytz.UTC), nullable=False)

    # Relacionamentos
    user = relationship("User", back_populates="goals")
    contributions = relationship("GoalContribution", back_populates="goal", cascade="all, delete-orphan")


class GoalContribution(Base):
    __tablename__ = "goal_contributions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    goal_id = Column(UUID(as_uuid=True), ForeignKey("goals.id"), nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    contribution_date = Column(DateTime(timezone=True), nullable=False)
    notes = Column(Text, nullable=True)
    
    # Relacionamento com transação (opcional)
    transaction_id = Column(UUID(as_uuid=True), ForeignKey("transactions.id"), nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(pytz.UTC), nullable=False)

    # Relacionamentos
    goal = relationship("Goal", back_populates="contributions")
    transaction = relationship("Transaction")

