from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from decimal import Decimal


class CategoryBudgetCreate(BaseModel):
    """Cria ou atualiza orçamento de uma categoria para um mês"""
    category_id: UUID
    target_amount: Decimal = Field(..., gt=0)
    month: int = Field(..., ge=1, le=12)
    year: int = Field(..., ge=2020, le=2100)


class CategoryBudgetResponse(BaseModel):
    """Resposta com orçamento de categoria"""
    category_id: UUID
    category_name: str
    category_type: str
    budget_group: Optional[str] = None  # necessities, wants, savings
    target_amount: Decimal
    actual_amount: Decimal
    percentage: float
    remaining_amount: Decimal
    is_over_budget: bool


class GoalSummary(BaseModel):
    """Resumo de uma meta para o planejamento"""
    id: UUID
    name: str
    icon: Optional[str] = None
    target_amount: Decimal
    current_amount: Decimal
    remaining_amount: Decimal
    percentage: float
    suggested_monthly_contribution: Optional[Decimal] = None  # Sugestão baseada no planejamento
    is_below_target: bool = False  # Se está abaixo da meta mensal
    current_month_contribution: Decimal = Decimal("0")  # Contribuições do mês atual


class MonthlyBudgetSummaryResponse(BaseModel):
    """Resumo do planejamento mensal"""
    month: int
    year: int
    total_income: Decimal  # Receita real (das transações)
    planned_income: Optional[Decimal] = None  # Receita planejada (cadastrada pelo usuário)
    total_planned_expenses: Decimal
    total_actual_expenses: Decimal
    balance: Decimal
    rule_50_30_20_enabled: bool
    necessities: Optional[dict] = None  # {planned, actual, percentage, limit}
    wants: Optional[dict] = None
    savings: Optional[dict] = None
    category_budgets: List[CategoryBudgetResponse]
    goals: List[GoalSummary] = []  # Metas ativas do usuário
    total_goals_amount: Decimal = Decimal("0")  # Total necessário para todas as metas
    total_goals_current: Decimal = Decimal("0")  # Total já economizado nas metas
    alerts: List[str] = []


class MonthlyIncomeUpdate(BaseModel):
    """Atualiza receita planejada do mês"""
    month: int = Field(..., ge=1, le=12)
    year: int = Field(..., ge=2020, le=2100)
    planned_income: Decimal = Field(..., gt=0)


class MonthlyBudgetCreate(BaseModel):
    """Cria planejamento mensal completo"""
    month: int = Field(..., ge=1, le=12)
    year: int = Field(..., ge=2020, le=2100)
    total_income: Decimal = Field(..., gt=0)
    rule_50_30_20_enabled: bool = False
    category_budgets: List[CategoryBudgetCreate] = []


class BudgetGroupUpdate(BaseModel):
    """Atualiza grupo de orçamento de uma categoria"""
    category_id: UUID
    budget_group: Optional[str] = None  # necessities, wants, savings, null

