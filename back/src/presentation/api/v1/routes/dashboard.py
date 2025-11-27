from fastapi import APIRouter, Depends, Query
from typing import Optional
from datetime import datetime, timedelta
from src.presentation.api.dependencies import get_current_active_user
from src.domain.repositories.transaction_repository import TransactionRepository
from src.domain.repositories.account_repository import AccountRepository
from src.domain.repositories.goal_repository import GoalRepository
from src.domain.repositories.planning_repository import PlanningRepository
from src.domain.repositories.bill_repository import BillRepository
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


@router.get("/summary")
async def get_dashboard_summary(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    report_service: ReportService = Depends(get_report_service),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Obtém resumo para dashboard (incluindo dados da família se aplicável)"""
    from src.infrastructure.repositories.family_repository import SQLAlchemyFamilyRepository, SQLAlchemyFamilyMemberRepository
    from src.infrastructure.repositories.family_permission_repository import SQLAlchemyFamilyPermissionRepository
    from src.infrastructure.database.models.family_permission import ModulePermission
    
    # Se não fornecido, usar último mês
    if not start_date:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
    elif not end_date:
        end_date = datetime.now()

    # Buscar dados do usuário
    print(f"📊 Buscando dados do dashboard para usuário: {current_user.id}")
    summary = await report_service.generate_summary_data(
        current_user.id, start_date, end_date
    )
    print(f"📊 Dados do usuário: saldo={summary.get('total_balance', 0)}, receitas={summary.get('monthly_income', 0)}, despesas={summary.get('monthly_expenses', 0)}")
    
    # Verificar se usuário está em alguma família e tem permissão para ver dashboard
    try:
        from sqlalchemy import text
        family_repo = SQLAlchemyFamilyRepository(db)
        member_repo = SQLAlchemyFamilyMemberRepository(db)
        permission_repo = SQLAlchemyFamilyPermissionRepository(db)
        
        # Buscar IDs das famílias usando SQL direto (evita greenlet error)
        family_ids_result = await db.execute(
            text("""
                SELECT DISTINCT f.id 
                FROM families f
                INNER JOIN family_members fm ON f.id = fm.family_id
                WHERE fm.user_id = :user_id
            """),
            {"user_id": str(current_user.id)}
        )
        family_ids = [row[0] for row in family_ids_result.fetchall()]
        print(f"📊 Usuário está em {len(family_ids)} família(s)")
        
        # Para cada família, incluir dados se tiver permissão
        for family_id in family_ids:
            try:
                print(f"📊 Processando família: {family_id}")
                
                # Buscar member_id usando SQL direto para evitar greenlet error
                member_result = await db.execute(
                    text("SELECT id FROM family_members WHERE user_id = :user_id AND family_id = :family_id"),
                    {"user_id": str(current_user.id), "family_id": str(family_id)}
                )
                member_row = member_result.fetchone()
                
                if member_row:
                    member_id = member_row[0]
                    print(f"📊 Membro encontrado: {member_id}")
                    
                    # Verificar permissão para ver dashboard usando SQL direto
                    permission_result = await db.execute(
                        text("""
                            SELECT can_view, can_edit, can_delete 
                            FROM family_member_permissions 
                            WHERE family_member_id = :member_id AND module = :module
                        """),
                        {"member_id": str(member_id), "module": "dashboard"}
                    )
                    permission_row = permission_result.fetchone()
                    
                    if permission_row and permission_row[0]:  # can_view
                        print(f"📊 Permissão dashboard: OK")
                        # Buscar dados da família e agregar ao resumo
                        print(f"📊 Buscando dados da família {family_id}...")
                        family_summary = await report_service.generate_summary_data_for_family(
                            family_id, start_date, end_date, db
                        )
                        print(f"📊 Dados da família: saldo={family_summary.get('total_balance', 0) if family_summary else 0}, receitas={family_summary.get('monthly_income', 0) if family_summary else 0}")
                        # Agregar dados (somar valores, combinar listas, etc)
                        if family_summary:
                            summary["total_balance"] = float(summary.get("total_balance", 0)) + float(family_summary.get("total_balance", 0))
                            summary["monthly_income"] = float(summary.get("monthly_income", 0)) + float(family_summary.get("monthly_income", 0))
                            summary["monthly_expenses"] = float(summary.get("monthly_expenses", 0)) + float(family_summary.get("monthly_expenses", 0))
                            summary["monthly_savings"] = float(summary.get("monthly_savings", 0)) + float(family_summary.get("monthly_savings", 0))
                            # Combinar transações recentes
                            if "recent_transactions" in family_summary:
                                existing_ids = {t.get("id") for t in summary.get("recent_transactions", [])}
                                for trans in family_summary.get("recent_transactions", []):
                                    if trans.get("id") not in existing_ids:
                                        summary.setdefault("recent_transactions", []).append(trans)
                    else:
                        print(f"⚠️ Usuário não tem permissão para ver dashboard da família {family_id}")
                else:
                    print(f"⚠️ Membro não encontrado na família {family_id}")
            except Exception as e:
                # Se houver erro com uma família específica, continuar com as outras
                print(f"⚠️ Erro ao processar família {family_id}: {e}")
                import traceback
                traceback.print_exc()
                continue
    except Exception as e:
        # Se houver erro ao buscar dados da família, apenas logar e continuar com dados do usuário
        print(f"⚠️ Erro ao buscar dados da família: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"📊 Resumo final: saldo={summary.get('total_balance', 0)}, receitas={summary.get('monthly_income', 0)}, despesas={summary.get('monthly_expenses', 0)}")
    
    return summary


@router.get("/stats")
async def get_dashboard_stats(
    current_user: User = Depends(get_current_active_user),
):
    """Obtém estatísticas gerais do dashboard"""
    # TODO: Implementar estatísticas mais detalhadas
    return {
        "total_accounts": 0,
        "active_goals": 0,
        "active_plannings": 0,
        "this_month_income": 0,
        "this_month_expense": 0,
    }

