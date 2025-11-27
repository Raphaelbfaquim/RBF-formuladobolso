from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from decimal import Decimal


# ========== Investment Account Schemas ==========

class InvestmentAccountBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    account_type: str  # stock_broker, bank, crypto_exchange, investment_platform, other
    institution_name: Optional[str] = None
    account_number: Optional[str] = None
    initial_balance: Decimal = Field(default=Decimal("0"), ge=0)
    currency: str = Field(default="BRL", max_length=3)


class InvestmentAccountCreate(InvestmentAccountBase):
    pass


class InvestmentAccountUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    account_type: Optional[str] = None
    institution_name: Optional[str] = None
    account_number: Optional[str] = None
    current_balance: Optional[Decimal] = None
    is_active: Optional[bool] = None


class InvestmentAccountResponse(InvestmentAccountBase):
    id: UUID
    current_balance: Decimal
    is_active: bool
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ========== Investment Transaction Schemas ==========

class InvestmentTransactionBase(BaseModel):
    investment_type: str  # stock, bond, fund, crypto, fixed_income, real_estate, other
    transaction_type: str  # buy, sell, dividend, interest, fee, transfer
    symbol: Optional[str] = None
    quantity: Decimal = Field(..., gt=0)
    unit_price: Decimal = Field(..., gt=0)
    total_amount: Decimal = Field(..., gt=0)
    fees: Decimal = Field(default=Decimal("0"), ge=0)
    transaction_date: datetime
    notes: Optional[str] = None


class InvestmentTransactionCreate(InvestmentTransactionBase):
    account_id: UUID


class InvestmentTransactionUpdate(BaseModel):
    investment_type: Optional[str] = None
    transaction_type: Optional[str] = None
    symbol: Optional[str] = None
    quantity: Optional[Decimal] = None
    unit_price: Optional[Decimal] = None
    total_amount: Optional[Decimal] = None
    fees: Optional[Decimal] = None
    transaction_date: Optional[datetime] = None
    notes: Optional[str] = None


class InvestmentTransactionResponse(InvestmentTransactionBase):
    id: UUID
    account_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ========== Performance Schemas ==========

class InvestmentPerformanceResponse(BaseModel):
    total_invested: Decimal
    current_value: Decimal
    total_return: Decimal
    return_percentage: float
    transactions_count: int


class PortfolioSummaryResponse(BaseModel):
    total_accounts: int
    total_invested: Decimal
    current_value: Decimal
    total_return: Decimal
    return_percentage: float
    day_variation: Decimal
    day_variation_percentage: float
    month_variation: Decimal
    month_variation_percentage: float
    year_variation: Decimal
    year_variation_percentage: float
    distribution_by_type: dict
    distribution_by_account: dict


# ========== Diversification Schemas ==========

class DiversificationResponse(BaseModel):
    by_type: dict
    by_account: dict
    by_institution: dict
    recommendations: List[str]


# ========== Simulator Schemas ==========

class InvestmentSimulatorRequest(BaseModel):
    initial_amount: Decimal = Field(..., gt=0)
    monthly_contribution: Decimal = Field(default=Decimal("0"), ge=0)
    annual_rate: float = Field(..., gt=0, le=100)
    period_months: int = Field(..., gt=0, le=600)
    inflation_rate: float = Field(default=0, ge=0, le=100)


class InvestmentSimulatorResponse(BaseModel):
    initial_amount: Decimal
    total_contributed: Decimal
    final_amount: Decimal
    total_return: Decimal
    return_percentage: float
    monthly_breakdown: List[dict]


# ========== Tax Calculation Schemas ==========

class TaxCalculationResponse(BaseModel):
    total_gain: Decimal
    taxable_amount: Decimal
    tax_amount: Decimal
    tax_rate: float
    darf_due_date: Optional[datetime] = None
    transactions: List[dict]

