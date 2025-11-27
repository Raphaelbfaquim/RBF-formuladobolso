from sqlalchemy import Column, String, Numeric, DateTime, ForeignKey, Enum as SQLEnum, Text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
import pytz
import enum

from src.infrastructure.database.base import Base


class InvestmentAccountType(str, enum.Enum):
    STOCK_BROKER = "stock_broker"  # Corretora de ações
    BANK = "bank"  # Banco
    CRYPTO_EXCHANGE = "crypto_exchange"  # Exchange de criptomoedas
    INVESTMENT_PLATFORM = "investment_platform"  # Plataforma de investimentos
    OTHER = "other"  # Outros


class InvestmentType(str, enum.Enum):
    STOCK = "stock"  # Ações
    BOND = "bond"  # Títulos
    FUND = "fund"  # Fundos
    CRYPTO = "crypto"  # Criptomoedas
    FIXED_INCOME = "fixed_income"  # Renda fixa
    REAL_ESTATE = "real_estate"  # Imóveis
    OTHER = "other"  # Outros


class InvestmentTransactionType(str, enum.Enum):
    BUY = "buy"  # Compra
    SELL = "sell"  # Venda
    DIVIDEND = "dividend"  # Dividendo
    INTEREST = "interest"  # Juros
    FEE = "fee"  # Taxa
    TRANSFER = "transfer"  # Transferência


class InvestmentAccount(Base):
    __tablename__ = "investment_accounts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    account_type = Column(SQLEnum(InvestmentAccountType), nullable=False)
    institution_name = Column(String(255), nullable=True)  # Nome da instituição
    account_number = Column(String(100), nullable=True)
    current_balance = Column(Numeric(15, 2), default=0, nullable=False)  # Saldo atual
    initial_balance = Column(Numeric(15, 2), default=0, nullable=False)  # Saldo inicial
    currency = Column(String(3), default="BRL", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relacionamentos
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(pytz.UTC), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(pytz.UTC), onupdate=lambda: datetime.now(pytz.UTC), nullable=False)

    # Relacionamentos
    user = relationship("User", back_populates="investment_accounts")
    transactions = relationship("InvestmentTransaction", back_populates="account", cascade="all, delete-orphan")


class InvestmentTransaction(Base):
    __tablename__ = "investment_transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    investment_type = Column(SQLEnum(InvestmentType), nullable=False)
    transaction_type = Column(SQLEnum(InvestmentTransactionType), nullable=False)
    symbol = Column(String(20), nullable=True)  # Símbolo do ativo (ex: PETR4, BTC)
    quantity = Column(Numeric(15, 6), nullable=False)  # Quantidade
    unit_price = Column(Numeric(15, 6), nullable=False)  # Preço unitário
    total_amount = Column(Numeric(15, 2), nullable=False)  # Valor total
    fees = Column(Numeric(15, 2), default=0, nullable=False)  # Taxas
    transaction_date = Column(DateTime(timezone=True), nullable=False)
    notes = Column(Text, nullable=True)
    
    # Relacionamentos
    account_id = Column(UUID(as_uuid=True), ForeignKey("investment_accounts.id"), nullable=False)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(pytz.UTC), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(pytz.UTC), onupdate=lambda: datetime.now(pytz.UTC), nullable=False)

    # Relacionamentos
    account = relationship("InvestmentAccount", back_populates="transactions")

