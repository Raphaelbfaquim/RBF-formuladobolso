from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
import pytz
import enum

from src.infrastructure.database.base import Base


class CategoryType(str, enum.Enum):
    INCOME = "income"  # Receita
    EXPENSE = "expense"  # Despesa
    TRANSFER = "transfer"  # Transferência


class Category(Base):
    __tablename__ = "categories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(String(500), nullable=True)
    category_type = Column(SQLEnum(CategoryType), nullable=False)
    icon = Column(String(50), nullable=True)
    color = Column(String(7), nullable=True)  # Hex color
    is_active = Column(Boolean, default=True, nullable=False)
    budget_group = Column(String(20), nullable=True)  # 'necessities', 'wants', 'savings', ou NULL
    
    # Relacionamentos
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    family_id = Column(UUID(as_uuid=True), ForeignKey("families.id"), nullable=True)
    parent_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"), nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(pytz.UTC), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(pytz.UTC), onupdate=lambda: datetime.now(pytz.UTC), nullable=False)

    # Relacionamentos
    parent = relationship("Category", remote_side=[id], backref="subcategories")
    transactions = relationship("Transaction", back_populates="category")

