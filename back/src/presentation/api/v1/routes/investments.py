from fastapi import APIRouter, Depends, Query, status
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from src.presentation.api.dependencies import get_current_active_user
from src.domain.repositories.investment_repository import (
    InvestmentAccountRepository,
    InvestmentTransactionRepository,
)
from src.infrastructure.repositories.investment_repository import (
    SQLAlchemyInvestmentAccountRepository,
    SQLAlchemyInvestmentTransactionRepository,
)
from src.application.use_cases.investment_use_cases import InvestmentUseCases
from src.application.services.investment_analysis_service import InvestmentAnalysisService
from src.presentation.schemas.investment import (
    InvestmentAccountCreate,
    InvestmentAccountUpdate,
    InvestmentAccountResponse,
    InvestmentTransactionCreate,
    InvestmentTransactionUpdate,
    InvestmentTransactionResponse,
    PortfolioSummaryResponse,
    DiversificationResponse,
    InvestmentSimulatorRequest,
    InvestmentSimulatorResponse,
    TaxCalculationResponse,
)
from src.infrastructure.database.base import get_db
from src.infrastructure.database.models.user import User
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


def get_investment_account_repository(
    db: AsyncSession = Depends(get_db),
) -> InvestmentAccountRepository:
    return SQLAlchemyInvestmentAccountRepository(db)


def get_investment_transaction_repository(
    db: AsyncSession = Depends(get_db),
) -> InvestmentTransactionRepository:
    return SQLAlchemyInvestmentTransactionRepository(db)


def get_investment_use_cases(
    account_repo: InvestmentAccountRepository = Depends(get_investment_account_repository),
    transaction_repo: InvestmentTransactionRepository = Depends(
        get_investment_transaction_repository
    ),
) -> InvestmentUseCases:
    return InvestmentUseCases(account_repo, transaction_repo)


def get_investment_analysis_service(
    account_repo: InvestmentAccountRepository = Depends(get_investment_account_repository),
    transaction_repo: InvestmentTransactionRepository = Depends(
        get_investment_transaction_repository
    ),
) -> InvestmentAnalysisService:
    return InvestmentAnalysisService(account_repo, transaction_repo)


# ========== Investment Accounts ==========

@router.post("/accounts", status_code=status.HTTP_201_CREATED, response_model=InvestmentAccountResponse)
async def create_investment_account(
    account_data: InvestmentAccountCreate,
    use_cases: InvestmentUseCases = Depends(get_investment_use_cases),
    current_user: User = Depends(get_current_active_user),
):
    """Cria uma nova conta de investimento"""
    account = await use_cases.create_investment_account(
        user_id=current_user.id,
        name=account_data.name,
        account_type=account_data.account_type,
        description=account_data.description,
        institution_name=account_data.institution_name,
        account_number=account_data.account_number,
        initial_balance=account_data.initial_balance,
        currency=account_data.currency,
    )
    return account


@router.get("/accounts", response_model=List[InvestmentAccountResponse])
async def list_investment_accounts(
    use_cases: InvestmentUseCases = Depends(get_investment_use_cases),
    current_user: User = Depends(get_current_active_user),
):
    """Lista todas as contas de investimento do usuário"""
    accounts = await use_cases.get_user_investment_accounts(current_user.id)
    return accounts


@router.get("/accounts/{account_id}", response_model=InvestmentAccountResponse)
async def get_investment_account(
    account_id: UUID,
    use_cases: InvestmentUseCases = Depends(get_investment_use_cases),
    current_user: User = Depends(get_current_active_user),
):
    """Obtém uma conta de investimento específica"""
    account = await use_cases.get_investment_account(account_id, current_user.id)
    return account


@router.put("/accounts/{account_id}", response_model=InvestmentAccountResponse)
async def update_investment_account(
    account_id: UUID,
    account_data: InvestmentAccountUpdate,
    use_cases: InvestmentUseCases = Depends(get_investment_use_cases),
    current_user: User = Depends(get_current_active_user),
):
    """Atualiza uma conta de investimento"""
    account = await use_cases.update_investment_account(
        account_id=account_id,
        user_id=current_user.id,
        name=account_data.name,
        description=account_data.description,
        account_type=account_data.account_type,
        institution_name=account_data.institution_name,
        account_number=account_data.account_number,
        is_active=account_data.is_active,
    )
    return account


@router.delete("/accounts/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_investment_account(
    account_id: UUID,
    use_cases: InvestmentUseCases = Depends(get_investment_use_cases),
    current_user: User = Depends(get_current_active_user),
):
    """Deleta uma conta de investimento"""
    await use_cases.delete_investment_account(account_id, current_user.id)
    return None


# ========== Investment Transactions ==========

@router.post(
    "/transactions",
    status_code=status.HTTP_201_CREATED,
    response_model=InvestmentTransactionResponse,
)
async def create_investment_transaction(
    transaction_data: InvestmentTransactionCreate,
    use_cases: InvestmentUseCases = Depends(get_investment_use_cases),
    current_user: User = Depends(get_current_active_user),
):
    """Cria uma nova transação de investimento"""
    transaction = await use_cases.create_investment_transaction(
        account_id=transaction_data.account_id,
        user_id=current_user.id,
        investment_type=transaction_data.investment_type,
        transaction_type=transaction_data.transaction_type,
        quantity=transaction_data.quantity,
        unit_price=transaction_data.unit_price,
        total_amount=transaction_data.total_amount,
        transaction_date=transaction_data.transaction_date,
        symbol=transaction_data.symbol,
        fees=transaction_data.fees,
        notes=transaction_data.notes,
    )
    return transaction


@router.get("/transactions", response_model=List[InvestmentTransactionResponse])
async def list_investment_transactions(
    account_id: Optional[UUID] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    use_cases: InvestmentUseCases = Depends(get_investment_use_cases),
    current_user: User = Depends(get_current_active_user),
):
    """Lista transações de investimento"""
    if account_id:
        transactions = await use_cases.get_account_transactions(
            account_id, current_user.id, start_date, end_date
        )
    else:
        transactions = await use_cases.get_user_transactions(
            current_user.id, start_date, end_date
        )
    return transactions


@router.get("/transactions/{transaction_id}", response_model=InvestmentTransactionResponse)
async def get_investment_transaction(
    transaction_id: UUID,
    use_cases: InvestmentUseCases = Depends(get_investment_use_cases),
    current_user: User = Depends(get_current_active_user),
):
    """Obtém uma transação de investimento específica"""
    transaction = await use_cases.get_investment_transaction(
        transaction_id, current_user.id
    )
    return transaction


@router.put("/transactions/{transaction_id}", response_model=InvestmentTransactionResponse)
async def update_investment_transaction(
    transaction_id: UUID,
    transaction_data: InvestmentTransactionUpdate,
    use_cases: InvestmentUseCases = Depends(get_investment_use_cases),
    current_user: User = Depends(get_current_active_user),
):
    """Atualiza uma transação de investimento"""
    transaction = await use_cases.update_investment_transaction(
        transaction_id=transaction_id,
        user_id=current_user.id,
        investment_type=transaction_data.investment_type,
        transaction_type=transaction_data.transaction_type,
        symbol=transaction_data.symbol,
        quantity=transaction_data.quantity,
        unit_price=transaction_data.unit_price,
        total_amount=transaction_data.total_amount,
        fees=transaction_data.fees,
        transaction_date=transaction_data.transaction_date,
        notes=transaction_data.notes,
    )
    return transaction


@router.delete("/transactions/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_investment_transaction(
    transaction_id: UUID,
    use_cases: InvestmentUseCases = Depends(get_investment_use_cases),
    current_user: User = Depends(get_current_active_user),
):
    """Deleta uma transação de investimento"""
    await use_cases.delete_investment_transaction(transaction_id, current_user.id)
    return None


# ========== Analysis & Reports ==========

@router.get("/summary", response_model=PortfolioSummaryResponse)
async def get_portfolio_summary(
    analysis_service: InvestmentAnalysisService = Depends(get_investment_analysis_service),
    current_user: User = Depends(get_current_active_user),
):
    """Resumo completo da carteira de investimentos"""
    summary = await analysis_service.get_portfolio_summary(current_user.id)
    return summary


@router.get("/performance")
async def get_portfolio_performance(
    period_days: int = Query(365, ge=1, le=3650),
    analysis_service: InvestmentAnalysisService = Depends(get_investment_analysis_service),
    current_user: User = Depends(get_current_active_user),
):
    """Performance da carteira"""
    performance = await analysis_service.calculate_portfolio_performance(
        current_user.id, period_days
    )
    return performance


@router.get("/diversification", response_model=DiversificationResponse)
async def get_diversification(
    analysis_service: InvestmentAnalysisService = Depends(get_investment_analysis_service),
    current_user: User = Depends(get_current_active_user),
):
    """Análise de diversificação da carteira"""
    diversification = await analysis_service.get_diversification(current_user.id)
    return diversification


@router.post("/simulator", response_model=InvestmentSimulatorResponse)
async def simulate_investment(
    simulator_data: InvestmentSimulatorRequest,
    analysis_service: InvestmentAnalysisService = Depends(get_investment_analysis_service),
    current_user: User = Depends(get_current_active_user),
):
    """Simula um investimento"""
    result = await analysis_service.simulate_investment(
        initial_amount=simulator_data.initial_amount,
        monthly_contribution=simulator_data.monthly_contribution,
        annual_rate=simulator_data.annual_rate,
        period_months=simulator_data.period_months,
        inflation_rate=simulator_data.inflation_rate,
    )
    return result


@router.get("/taxes", response_model=TaxCalculationResponse)
async def calculate_taxes(
    start_date: datetime = Query(...),
    end_date: datetime = Query(...),
    analysis_service: InvestmentAnalysisService = Depends(get_investment_analysis_service),
    current_user: User = Depends(get_current_active_user),
):
    """Calcula impostos sobre investimentos"""
    taxes = await analysis_service.calculate_taxes(
        current_user.id, start_date, end_date
    )
    return taxes
