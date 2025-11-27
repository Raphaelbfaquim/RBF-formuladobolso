from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from typing import Optional
from uuid import UUID
from datetime import datetime
from src.presentation.api.dependencies import get_current_active_user
from src.domain.repositories.transaction_repository import TransactionRepository
from src.domain.repositories.account_repository import AccountRepository
from src.domain.repositories.goal_repository import GoalRepository
from src.domain.repositories.planning_repository import PlanningRepository
from src.infrastructure.repositories.transaction_repository import SQLAlchemyTransactionRepository
from src.infrastructure.repositories.account_repository import SQLAlchemyAccountRepository
from src.infrastructure.repositories.goal_repository import SQLAlchemyGoalRepository
from src.infrastructure.repositories.planning_repository import SQLAlchemyPlanningRepository
from src.infrastructure.repositories.bill_repository import SQLAlchemyBillRepository
from src.application.services.report_service import ReportService
from src.infrastructure.database.base import get_db
from src.infrastructure.database.models.user import User
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


def get_report_service(
    db: AsyncSession = Depends(get_db),
) -> ReportService:
    transaction_repo = SQLAlchemyTransactionRepository(db)
    account_repo = SQLAlchemyAccountRepository(db)
    goal_repo = SQLAlchemyGoalRepository(db)
    planning_repo = SQLAlchemyPlanningRepository(db)
    bill_repo = SQLAlchemyBillRepository(db)
    return ReportService(transaction_repo, account_repo, goal_repo, planning_repo, bill_repo)


@router.get("/monthly/pdf")
async def get_monthly_report_pdf(
    year: int = Query(..., ge=2020, le=2100),
    month: int = Query(..., ge=1, le=12),
    report_service: ReportService = Depends(get_report_service),
    current_user: User = Depends(get_current_active_user),
):
    """Gera relatório mensal em PDF"""
    pdf_buffer = await report_service.generate_monthly_report_pdf(
        current_user.id, year, month
    )
    
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=relatorio_{month:02d}_{year}.pdf"
        },
    )


@router.get("/transactions/excel")
async def get_transactions_excel(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    report_service: ReportService = Depends(get_report_service),
    current_user: User = Depends(get_current_active_user),
):
    """Gera relatório de transações em Excel"""
    excel_buffer = await report_service.generate_transactions_excel(
        current_user.id, start_date, end_date
    )
    
    return StreamingResponse(
        excel_buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": "attachment; filename=transacoes.xlsx"
        },
    )


# ========== FASE 1 - MVP ==========

@router.get("/executive")
async def get_executive_report(
    start_date: datetime = Query(...),
    end_date: datetime = Query(...),
    report_service: ReportService = Depends(get_report_service),
    current_user: User = Depends(get_current_active_user),
):
    """Relatório Executivo - Dashboard com KPIs"""
    data = await report_service.get_executive_report(
        current_user.id, start_date, end_date
    )
    return data


@router.get("/income")
async def get_income_report(
    start_date: datetime = Query(...),
    end_date: datetime = Query(...),
    report_service: ReportService = Depends(get_report_service),
    current_user: User = Depends(get_current_active_user),
):
    """Relatório de Receitas"""
    data = await report_service.get_income_report(
        current_user.id, start_date, end_date
    )
    return data


@router.get("/expense")
async def get_expense_report(
    start_date: datetime = Query(...),
    end_date: datetime = Query(...),
    report_service: ReportService = Depends(get_report_service),
    current_user: User = Depends(get_current_active_user),
):
    """Relatório de Despesas"""
    data = await report_service.get_expense_report(
        current_user.id, start_date, end_date
    )
    return data


@router.get("/categories")
async def get_categories_report(
    start_date: datetime = Query(...),
    end_date: datetime = Query(...),
    report_service: ReportService = Depends(get_report_service),
    current_user: User = Depends(get_current_active_user),
):
    """Relatório de Categorias"""
    data = await report_service.get_categories_report(
        current_user.id, start_date, end_date
    )
    return data


# ========== FASE 2 - AVANÇADO ==========

@router.get("/planning-vs-real")
async def get_planning_vs_real_report(
    start_date: datetime = Query(...),
    end_date: datetime = Query(...),
    report_service: ReportService = Depends(get_report_service),
    current_user: User = Depends(get_current_active_user),
):
    """Relatório de Planejamento vs Real"""
    data = await report_service.get_planning_vs_real_report(
        current_user.id, start_date, end_date
    )
    return data


@router.get("/comparative")
async def get_comparative_report(
    start_date: datetime = Query(...),
    end_date: datetime = Query(...),
    compare_period: str = Query("previous", regex="^(previous|year)$"),
    report_service: ReportService = Depends(get_report_service),
    current_user: User = Depends(get_current_active_user),
):
    """Relatório Comparativo"""
    data = await report_service.get_comparative_report(
        current_user.id, start_date, end_date, compare_period
    )
    return data


@router.get("/trends")
async def get_trends_report(
    start_date: datetime = Query(...),
    end_date: datetime = Query(...),
    report_service: ReportService = Depends(get_report_service),
    current_user: User = Depends(get_current_active_user),
):
    """Relatório de Tendências"""
    data = await report_service.get_trends_report(
        current_user.id, start_date, end_date
    )
    return data


@router.get("/goals")
async def get_goals_report(
    report_service: ReportService = Depends(get_report_service),
    current_user: User = Depends(get_current_active_user),
):
    """Relatório de Metas"""
    data = await report_service.get_goals_report(current_user.id)
    return data


# ========== FASE 3 - PREMIUM ==========

@router.get("/temporal")
async def get_temporal_report(
    start_date: datetime = Query(...),
    end_date: datetime = Query(...),
    report_service: ReportService = Depends(get_report_service),
    current_user: User = Depends(get_current_active_user),
):
    """Relatório de Análise Temporal"""
    data = await report_service.get_temporal_report(
        current_user.id, start_date, end_date
    )
    return data


@router.get("/accounts")
async def get_accounts_report(
    start_date: datetime = Query(...),
    end_date: datetime = Query(...),
    report_service: ReportService = Depends(get_report_service),
    current_user: User = Depends(get_current_active_user),
):
    """Relatório de Contas"""
    data = await report_service.get_accounts_report(
        current_user.id, start_date, end_date
    )
    return data

