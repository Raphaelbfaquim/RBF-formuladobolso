from fastapi import APIRouter, Depends, status, HTTPException, Query
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from decimal import Decimal
import pytz
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import joinedload

from src.presentation.schemas.monthly_budget import (
    MonthlyBudgetSummaryResponse,
    MonthlyBudgetCreate,
    CategoryBudgetCreate,
    CategoryBudgetResponse,
    BudgetGroupUpdate,
    MonthlyIncomeUpdate,
)
from src.presentation.api.dependencies import get_current_active_user
from src.infrastructure.database.models.user import User
from src.infrastructure.database.models.category import Category, CategoryType
from src.infrastructure.database.models.transaction import Transaction, TransactionStatus, TransactionType
from src.infrastructure.database.base import get_db

router = APIRouter()


@router.get("/summary", response_model=MonthlyBudgetSummaryResponse)
async def get_monthly_budget_summary(
    month: int = Query(..., ge=1, le=12),
    year: int = Query(..., ge=2020, le=2100),
    rule_50_30_20_enabled: bool = Query(False),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Obtém resumo do planejamento mensal por categoria"""
    from src.infrastructure.database.models.planning import MonthlyPlanning, Planning, PlanningType
    
    # Calcular período do mês
    start_date = datetime(year, month, 1, tzinfo=pytz.UTC)
    if month == 12:
        end_date = datetime(year + 1, 1, 1, tzinfo=pytz.UTC)
    else:
        end_date = datetime(year, month + 1, 1, tzinfo=pytz.UTC)
    
    # Buscar todas as categorias de despesa do usuário (ativas)
    categories_query = select(Category).where(
        and_(
            Category.category_type == CategoryType.EXPENSE,
            Category.is_active == True,
            or_(
                Category.user_id == current_user.id,
                Category.user_id.is_(None)  # Categorias padrão
            )
        )
    ).order_by(Category.name)
    categories_result = await db.execute(categories_query)
    categories = list(categories_result.scalars().all())
    
    # Debug: verificar quantas categorias foram encontradas
    print(f"[DEBUG] Categorias encontradas: {len(categories)}")
    for cat in categories:
        print(f"[DEBUG] - {cat.name} (ID: {cat.id}, user_id: {cat.user_id})")
    
    # Buscar todos os planejamentos mensais do usuário
    planning_query = select(Planning).where(
        and_(
            Planning.user_id == current_user.id,
            Planning.planning_type == PlanningType.MONTHLY,
            Planning.is_active == True
        )
    )
    planning_result = await db.execute(planning_query)
    plannings = list(planning_result.scalars().all())
    
    # Buscar todos os planejamentos mensais detalhados
    planning_ids = [p.id for p in plannings]
    monthly_plannings = []
    if planning_ids:
        monthly_query = select(MonthlyPlanning).where(
            and_(
                MonthlyPlanning.planning_id.in_(planning_ids),
                MonthlyPlanning.month == month,
                MonthlyPlanning.year == year
            )
        )
        monthly_result = await db.execute(monthly_query)
        monthly_plannings = list(monthly_result.scalars().all())
    
    # Criar mapa de planejamentos por categoria
    planning_map = {}
    for planning in plannings:
        if planning.category_id:
            # Buscar monthly planning correspondente
            for mp in monthly_plannings:
                if mp.planning_id == planning.id:
                    planning_map[str(planning.category_id)] = mp
                    break
    
    # Buscar transações do período
    transactions_query = select(Transaction).where(
        and_(
            Transaction.user_id == current_user.id,
            Transaction.transaction_type == TransactionType.EXPENSE,
            Transaction.status == TransactionStatus.COMPLETED,
            Transaction.transaction_date >= start_date,
            Transaction.transaction_date < end_date
        )
    ).options(joinedload(Transaction.category))
    
    transactions_result = await db.execute(transactions_query)
    transactions = list(transactions_result.scalars().all())
    
    # Calcular gastos por categoria
    expenses_by_category = {}
    for transaction in transactions:
        if transaction.category_id:
            cat_id = str(transaction.category_id)
            if cat_id not in expenses_by_category:
                expenses_by_category[cat_id] = Decimal("0")
            expenses_by_category[cat_id] += transaction.amount
    
    # Calcular receitas do período (receita real)
    income_query = select(func.sum(Transaction.amount)).where(
        and_(
            Transaction.user_id == current_user.id,
            Transaction.transaction_type == TransactionType.INCOME,
            Transaction.status == TransactionStatus.COMPLETED,
            Transaction.transaction_date >= start_date,
            Transaction.transaction_date < end_date
        )
    )
    total_income_result = await db.execute(income_query)
    total_income = total_income_result.scalar() or Decimal("0")
    
    # Buscar receita planejada (armazenada em um Planning mensal geral sem categoria)
    planned_income_query = select(Planning).where(
        and_(
            Planning.user_id == current_user.id,
            Planning.planning_type == PlanningType.MONTHLY,
            Planning.category_id.is_(None),  # Planning geral mensal
            Planning.is_active == True
        )
    )
    planned_income_result = await db.execute(planned_income_query)
    planned_income_planning = planned_income_result.scalar_one_or_none()
    
    planned_income = None
    if planned_income_planning:
        # Buscar MonthlyPlanning correspondente ao mês/ano
        monthly_income_query = select(MonthlyPlanning).where(
            and_(
                MonthlyPlanning.planning_id == planned_income_planning.id,
                MonthlyPlanning.month == month,
                MonthlyPlanning.year == year
            )
        )
        monthly_income_result = await db.execute(monthly_income_query)
        monthly_income = monthly_income_result.scalar_one_or_none()
        if monthly_income:
            planned_income = monthly_income.target_amount
    
    # Calcular total de despesas
    total_actual_expenses = sum(expenses_by_category.values())
    
    # Construir resposta de orçamentos por categoria
    category_budgets = []
    total_planned = Decimal("0")
    
    print(f"[DEBUG] Processando {len(categories)} categorias")
    
    for category in categories:
        cat_id = str(category.id)
        target_amount = Decimal("0")
        
        # Buscar planejamento se existir
        if cat_id in planning_map:
            target_amount = planning_map[cat_id].target_amount
            print(f"[DEBUG] Categoria {category.name} tem planejamento: {target_amount}")
        
        actual_amount = expenses_by_category.get(cat_id, Decimal("0"))
        percentage = float((actual_amount / target_amount * 100)) if target_amount > 0 else 0.0
        remaining = target_amount - actual_amount
        is_over = actual_amount > target_amount if target_amount > 0 else False
        
        total_planned += target_amount
        
        # Obter budget_group da categoria
        budget_group = getattr(category, 'budget_group', None)
        
        category_budgets.append(CategoryBudgetResponse(
            category_id=category.id,
            category_name=category.name,
            category_type=category.category_type.value,
            budget_group=budget_group,
            target_amount=target_amount,
            actual_amount=actual_amount,
            percentage=round(percentage, 2),
            remaining_amount=remaining,
            is_over_budget=is_over
        ))
    
    print(f"[DEBUG] Total de category_budgets criados: {len(category_budgets)}")
    
    # Buscar metas ativas do usuário
    from src.infrastructure.database.models.goal import Goal, GoalStatus
    from src.presentation.schemas.monthly_budget import GoalSummary
    
    goals_query = select(Goal).where(
        and_(
            Goal.user_id == current_user.id,
            Goal.status == GoalStatus.ACTIVE
        )
    ).order_by(Goal.target_date.asc().nulls_last(), Goal.created_at.asc())
    goals_result = await db.execute(goals_query)
    user_goals = list(goals_result.scalars().all())
    
    # Calcular sugestões de contribuição mensal para cada meta
    goals_summary = []
    total_goals_amount = Decimal("0")
    total_goals_current = Decimal("0")
    
    # Calcular quanto sobra para metas (poupança planejada)
    income_for_goals = (planned_income if planned_income else total_income) - total_planned
    
    for goal in user_goals:
        total_goals_amount += goal.target_amount
        total_goals_current += goal.current_amount
        
        # Calcular sugestão de contribuição mensal baseada na data objetivo
        suggested_monthly = None
        if goal.target_date:
            now = datetime.now(pytz.UTC)
            days_remaining = (goal.target_date - now).days
            if days_remaining > 0:
                months_remaining = Decimal(str(days_remaining / 30.0))
                if months_remaining > 0:
                    suggested_monthly = (goal.target_amount - goal.current_amount) / months_remaining
        
        percentage = float((goal.current_amount / goal.target_amount * 100)) if goal.target_amount > 0 else 0.0
        
        goals_summary.append(GoalSummary(
            id=goal.id,
            name=goal.name,
            icon=goal.icon,
            target_amount=goal.target_amount,
            current_amount=goal.current_amount,
            remaining_amount=goal.target_amount - goal.current_amount,
            percentage=round(percentage, 2),
            suggested_monthly_contribution=suggested_monthly
        ))
    
    # Calcular regra 50-30-20 se ativada
    # Usar receita planejada se disponível, senão usar receita real
    income_for_rule = planned_income if planned_income and planned_income > 0 else total_income
    
    necessities_data = None
    wants_data = None
    savings_data = None
    alerts = []
    
    # Alerta se regra ativada mas receita planejada não cadastrada
    if rule_50_30_20_enabled and not planned_income:
        alerts.append("💡 Cadastre a receita planejada para calcular a regra 50-30-20 corretamente")
    
    if rule_50_30_20_enabled and income_for_rule > 0:
        necessities_limit = income_for_rule * Decimal("0.5")
        wants_limit = income_for_rule * Decimal("0.3")
        savings_limit = income_for_rule * Decimal("0.2")
        
        # Agrupar por budget_group
        necessities_planned = Decimal("0")
        necessities_actual = Decimal("0")
        wants_planned = Decimal("0")
        wants_actual = Decimal("0")
        savings_planned = Decimal("0")
        savings_actual = Decimal("0")
        
        for budget in category_budgets:
            if budget.budget_group == "necessities":
                necessities_planned += budget.target_amount
                necessities_actual += budget.actual_amount
            elif budget.budget_group == "wants":
                wants_planned += budget.target_amount
                wants_actual += budget.actual_amount
            elif budget.budget_group == "savings":
                savings_planned += budget.target_amount
                savings_actual += budget.actual_amount
        
        necessities_percentage = float((necessities_actual / necessities_limit * 100)) if necessities_limit > 0 else 0.0
        wants_percentage = float((wants_actual / wants_limit * 100)) if wants_limit > 0 else 0.0
        savings_percentage = float((savings_actual / savings_limit * 100)) if savings_limit > 0 else 0.0
        
        necessities_data = {
            "planned": float(necessities_planned),
            "actual": float(necessities_actual),
            "percentage": round(necessities_percentage, 2),
            "limit": float(necessities_limit)
        }
        
        wants_data = {
            "planned": float(wants_planned),
            "actual": float(wants_actual),
            "percentage": round(wants_percentage, 2),
            "limit": float(wants_limit)
        }
        
        savings_data = {
            "planned": float(savings_planned),
            "actual": float(savings_actual),
            "percentage": round(savings_percentage, 2),
            "limit": float(savings_limit)
        }
        
        # Gerar alertas
        if necessities_percentage > 100:
            alerts.append(f"⚠️ Necessidades ultrapassaram 50% da renda ({necessities_percentage:.1f}%)")
        elif necessities_percentage > 80:
            alerts.append(f"⚠️ Necessidades próximas do limite ({necessities_percentage:.1f}%)")
        
        if wants_percentage > 100:
            alerts.append(f"🔴 Desejos ultrapassaram 30% da renda ({wants_percentage:.1f}%)")
        elif wants_percentage > 80:
            alerts.append(f"⚠️ Desejos próximos do limite ({wants_percentage:.1f}%)")
        
        if savings_percentage < 80:
            alerts.append(f"💡 Poupança abaixo da meta de 20% ({savings_percentage:.1f}%)")
    
    # Alertas gerais
    for budget in category_budgets:
        if budget.is_over_budget:
            alerts.append(f"🔴 {budget.category_name} ultrapassou o orçamento")
        elif budget.percentage > 80:
            alerts.append(f"⚠️ {budget.category_name} próximo do limite ({budget.percentage:.1f}%)")
    
    # Alertas de metas
    for goal_summary in goals_summary:
        if goal_summary.is_below_target and goal_summary.suggested_monthly_contribution:
            alerts.append(f"⚠️ Meta '{goal_summary.name}' está abaixo da contribuição mensal sugerida ({goal_summary.suggested_monthly_contribution:.2f})")
    
    # Buscar metas ativas do usuário
    from src.infrastructure.database.models.goal import Goal, GoalStatus
    from src.presentation.schemas.monthly_budget import GoalSummary
    
    goals_query = select(Goal).where(
        and_(
            Goal.user_id == current_user.id,
            Goal.status == GoalStatus.ACTIVE
        )
    ).order_by(Goal.target_date.asc().nulls_last(), Goal.created_at.asc())
    goals_result = await db.execute(goals_query)
    user_goals = list(goals_result.scalars().all())
    
    # Calcular sugestões de contribuição mensal para cada meta
    goals_summary = []
    total_goals_amount = Decimal("0")
    total_goals_current = Decimal("0")
    
    # Calcular quanto sobra para metas (poupança planejada)
    income_for_goals = (planned_income if planned_income else total_income) - total_planned
    
    for goal in user_goals:
        total_goals_amount += goal.target_amount
        total_goals_current += goal.current_amount
        
        # Calcular sugestão de contribuição mensal baseada na data objetivo
        suggested_monthly = None
        if goal.target_date:
            now = datetime.now(pytz.UTC)
            days_remaining = (goal.target_date - now).days
            if days_remaining > 0:
                months_remaining = Decimal(str(days_remaining / 30.0))
                if months_remaining > 0:
                    remaining = goal.target_amount - goal.current_amount
                    suggested_monthly = remaining / months_remaining
        
        percentage = float((goal.current_amount / goal.target_amount * 100)) if goal.target_amount > 0 else 0.0
        
        # Verificar se está no caminho certo (contribuições do mês atual)
        from src.infrastructure.repositories.goal_repository import SQLAlchemyGoalContributionRepository
        contribution_repo = SQLAlchemyGoalContributionRepository(db)
        current_month_contributions = await contribution_repo.get_by_goal_id(goal.id)
        
        # Filtrar contribuições do mês atual
        current_month_total = Decimal("0")
        for contrib in current_month_contributions:
            contrib_date = contrib.contribution_date
            if contrib_date.year == year and contrib_date.month == month:
                current_month_total += contrib.amount
        
        # Verificar se está abaixo da sugestão mensal
        is_below_target = False
        if suggested_monthly and suggested_monthly > 0:
            is_below_target = current_month_total < suggested_monthly * Decimal("0.8")  # 80% da sugestão
        
        goals_summary.append(GoalSummary(
            id=goal.id,
            name=goal.name,
            icon=goal.icon,
            target_amount=goal.target_amount,
            current_amount=goal.current_amount,
            remaining_amount=goal.target_amount - goal.current_amount,
            percentage=round(percentage, 2),
            suggested_monthly_contribution=suggested_monthly,
            is_below_target=is_below_target,
            current_month_contribution=current_month_total
        ))
    
    return MonthlyBudgetSummaryResponse(
        month=month,
        year=year,
        total_income=total_income,
        planned_income=planned_income,
        total_planned_expenses=total_planned,
        total_actual_expenses=total_actual_expenses,
        balance=(planned_income if planned_income else total_income) - total_actual_expenses,
        rule_50_30_20_enabled=rule_50_30_20_enabled,
        necessities=necessities_data,
        wants=wants_data,
        savings=savings_data,
        category_budgets=category_budgets,
        goals=goals_summary,
        total_goals_amount=total_goals_amount,
        total_goals_current=total_goals_current,
        alerts=alerts
    )


@router.post("/category", status_code=status.HTTP_201_CREATED)
async def create_or_update_category_budget(
    budget_data: CategoryBudgetCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Cria ou atualiza orçamento de uma categoria para um mês"""
    from src.infrastructure.database.models.planning import Planning, MonthlyPlanning, PlanningType
    
    # Verificar se categoria existe
    category = await db.get(Category, budget_data.category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")
    
    # Calcular período do mês
    start_date = datetime(budget_data.year, budget_data.month, 1, tzinfo=pytz.UTC)
    if budget_data.month == 12:
        end_date = datetime(budget_data.year + 1, 1, 1, tzinfo=pytz.UTC)
    else:
        end_date = datetime(budget_data.year, budget_data.month + 1, 1, tzinfo=pytz.UTC)
    
    # Buscar planejamento mensal para esta categoria
    planning_query = select(Planning).where(
        and_(
            Planning.user_id == current_user.id,
            Planning.planning_type == PlanningType.MONTHLY,
            Planning.category_id == budget_data.category_id,
            Planning.is_active == True
        )
    )
    planning_result = await db.execute(planning_query)
    planning = planning_result.scalar_one_or_none()
    
    if not planning:
        # Criar novo planejamento mensal para esta categoria
        planning = Planning(
            name=f"Planejamento {category.name} - {budget_data.month}/{budget_data.year}",
            planning_type=PlanningType.MONTHLY,
            start_date=start_date,
            end_date=end_date,
            category_id=budget_data.category_id,
            user_id=current_user.id,
            is_active=True
        )
        db.add(planning)
        await db.flush()
    
    # Buscar ou criar planejamento mensal específico
    monthly_query = select(MonthlyPlanning).where(
        and_(
            MonthlyPlanning.planning_id == planning.id,
            MonthlyPlanning.month == budget_data.month,
            MonthlyPlanning.year == budget_data.year
        )
    )
    monthly_result = await db.execute(monthly_query)
    monthly = monthly_result.scalar_one_or_none()
    
    if monthly:
        monthly.target_amount = budget_data.target_amount
    else:
        monthly = MonthlyPlanning(
            planning_id=planning.id,
            month=budget_data.month,
            year=budget_data.year,
            target_amount=budget_data.target_amount,
            actual_amount=Decimal("0")
        )
        db.add(monthly)
    
    await db.commit()
    await db.refresh(monthly)
    
    return {"message": "Orçamento criado/atualizado com sucesso", "id": monthly.id}


@router.put("/category/{category_id}/budget-group", status_code=status.HTTP_200_OK)
async def update_category_budget_group(
    category_id: UUID,
    update_data: BudgetGroupUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Atualiza o grupo de orçamento de uma categoria (necessities, wants, savings)"""
    # Verificar se categoria existe
    category = await db.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")
    
    # Validar budget_group se fornecido
    if update_data.budget_group and update_data.budget_group not in ['necessities', 'wants', 'savings']:
        raise HTTPException(
            status_code=400, 
            detail="budget_group deve ser 'necessities', 'wants', 'savings' ou null"
        )
    
    # Atualizar budget_group
    category.budget_group = update_data.budget_group
    await db.commit()
    await db.refresh(category)
    
    return {"message": "Grupo de orçamento atualizado com sucesso", "budget_group": category.budget_group}


@router.put("/income", status_code=status.HTTP_200_OK)
async def update_monthly_income(
    income_data: MonthlyIncomeUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Atualiza a receita planejada do mês"""
    from src.infrastructure.database.models.planning import Planning, MonthlyPlanning, PlanningType
    
    # Calcular período do mês
    start_date = datetime(income_data.year, income_data.month, 1, tzinfo=pytz.UTC)
    if income_data.month == 12:
        end_date = datetime(income_data.year + 1, 1, 1, tzinfo=pytz.UTC)
    else:
        end_date = datetime(income_data.year, income_data.month + 1, 1, tzinfo=pytz.UTC)
    
    # Buscar planejamento mensal geral (sem categoria)
    planning_query = select(Planning).where(
        and_(
            Planning.user_id == current_user.id,
            Planning.planning_type == PlanningType.MONTHLY,
            Planning.category_id.is_(None),  # Planning geral para receita
            Planning.is_active == True
        )
    )
    planning_result = await db.execute(planning_query)
    planning = planning_result.scalar_one_or_none()
    
    if not planning:
        # Criar novo planejamento mensal geral para receita
        planning = Planning(
            name=f"Receita Planejada - {income_data.month}/{income_data.year}",
            planning_type=PlanningType.MONTHLY,
            start_date=start_date,
            end_date=end_date,
            category_id=None,  # Sem categoria = planejamento geral
            user_id=current_user.id,
            is_active=True
        )
        db.add(planning)
        await db.flush()
    
    # Buscar ou criar planejamento mensal específico
    monthly_query = select(MonthlyPlanning).where(
        and_(
            MonthlyPlanning.planning_id == planning.id,
            MonthlyPlanning.month == income_data.month,
            MonthlyPlanning.year == income_data.year
        )
    )
    monthly_result = await db.execute(monthly_query)
    monthly = monthly_result.scalar_one_or_none()
    
    if monthly:
        monthly.target_amount = income_data.planned_income
    else:
        monthly = MonthlyPlanning(
            planning_id=planning.id,
            month=income_data.month,
            year=income_data.year,
            target_amount=income_data.planned_income,
            actual_amount=Decimal("0")
        )
        db.add(monthly)
    
    await db.commit()
    await db.refresh(monthly)
    
    return {"message": "Receita planejada atualizada com sucesso", "planned_income": monthly.target_amount}

