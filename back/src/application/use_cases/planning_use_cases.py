from typing import List, Optional
from uuid import UUID
from datetime import datetime, date
from decimal import Decimal
from src.domain.repositories.planning_repository import (
    PlanningRepository,
    MonthlyPlanningRepository,
    WeeklyPlanningRepository,
    DailyPlanningRepository,
    AnnualPlanningRepository,
    QuarterlyGoalRepository,
)
from src.domain.repositories.transaction_repository import TransactionRepository
from src.infrastructure.database.models.planning import (
    Planning,
    PlanningType,
    MonthlyPlanning,
    WeeklyPlanning,
    DailyPlanning,
    AnnualPlanning,
    QuarterlyGoal,
)
from src.shared.exceptions import NotFoundException, ValidationException


class PlanningUseCases:
    """Casos de uso para gerenciamento de planejamentos"""

    def __init__(
        self,
        planning_repository: PlanningRepository,
        monthly_repository: MonthlyPlanningRepository,
        weekly_repository: WeeklyPlanningRepository,
        daily_repository: DailyPlanningRepository,
        annual_repository: AnnualPlanningRepository,
        quarterly_repository: QuarterlyGoalRepository,
        transaction_repository: TransactionRepository,
    ):
        self.planning_repository = planning_repository
        self.monthly_repository = monthly_repository
        self.weekly_repository = weekly_repository
        self.daily_repository = daily_repository
        self.annual_repository = annual_repository
        self.quarterly_repository = quarterly_repository
        self.transaction_repository = transaction_repository

    async def create_planning(
        self,
        name: str,
        planning_type: str,
        start_date: datetime,
        end_date: datetime,
        user_id: UUID,
        target_amount: Optional[Decimal] = None,
        description: Optional[str] = None,
        category_id: Optional[UUID] = None,
    ) -> Planning:
        """Cria um novo planejamento"""
        try:
            PlanningType(planning_type)
        except ValueError:
            raise ValidationException(f"Tipo de planejamento inválido: {planning_type}")

        planning = Planning(
            name=name,
            description=description,
            planning_type=PlanningType(planning_type),
            start_date=start_date,
            end_date=end_date,
            target_amount=target_amount,
            actual_amount=Decimal("0"),
            is_active=True,
            user_id=user_id,
            category_id=category_id,
        )

        return await self.planning_repository.create(planning)

    async def get_planning(self, planning_id: UUID) -> Planning:
        """Obtém um planejamento por ID"""
        planning = await self.planning_repository.get_by_id(planning_id)
        if not planning:
            raise NotFoundException("Planejamento", str(planning_id))
        return planning

    async def calculate_planning_progress(self, planning_id: UUID) -> dict:
        """Calcula o progresso de um planejamento"""
        planning = await self.get_planning(planning_id)

        # Calcular valor atual baseado em transações
        actual_amount = await self.transaction_repository.get_sum_by_period(
            user_id=planning.user_id,
            start_date=planning.start_date,
            end_date=planning.end_date,
            transaction_type="expense" if planning.target_amount else None,
        )

        planning.actual_amount = Decimal(str(actual_amount))
        await self.planning_repository.update(planning)

        target = planning.target_amount or Decimal("0")
        percentage = (
            float((planning.actual_amount / target) * 100) if target > 0 else 0.0
        )
        remaining = target - planning.actual_amount

        return {
            "planning_id": planning_id,
            "target_amount": target,
            "actual_amount": planning.actual_amount,
            "percentage": round(percentage, 2),
            "remaining_amount": remaining,
            "is_on_track": planning.actual_amount <= target,
        }

    async def create_monthly_planning(
        self,
        planning_id: UUID,
        month: int,
        year: int,
        target_amount: Decimal,
    ) -> MonthlyPlanning:
        """Cria planejamento mensal"""
        if month < 1 or month > 12:
            raise ValidationException("Mês deve estar entre 1 e 12")

        planning = await self.get_planning(planning_id)

        monthly = MonthlyPlanning(
            planning_id=planning_id,
            month=month,
            year=year,
            target_amount=target_amount,
            actual_amount=Decimal("0"),
        )

        monthly = await self.monthly_repository.create(monthly)
        await self.update_monthly_progress(monthly.id)
        return monthly

    async def update_monthly_progress(self, monthly_planning_id: UUID) -> MonthlyPlanning:
        """Atualiza progresso de planejamento mensal"""
        monthly = await self.monthly_repository.get_by_id(monthly_planning_id)
        if not monthly:
            raise NotFoundException("Planejamento mensal", str(monthly_planning_id))
        
        planning = await self.get_planning(monthly.planning_id)
        
        # Calcular período do mês
        from datetime import date
        start_date = datetime(monthly.year, monthly.month, 1)
        if monthly.month == 12:
            end_date = datetime(monthly.year + 1, 1, 1)
        else:
            end_date = datetime(monthly.year, monthly.month + 1, 1)
        
        actual_amount = await self.transaction_repository.get_sum_by_period(
            user_id=planning.user_id,
            start_date=start_date,
            end_date=end_date,
            transaction_type="expense",
        )
        
        monthly.actual_amount = Decimal(str(actual_amount))
        return await self.monthly_repository.update(monthly)

    async def create_quarterly_goal(
        self,
        annual_planning_id: UUID,
        quarter: int,
        target_amount: Decimal,
        description: Optional[str] = None,
    ) -> QuarterlyGoal:
        """Cria meta trimestral"""
        if quarter < 1 or quarter > 4:
            raise ValidationException("Trimestre deve estar entre 1 e 4")

        annual = await self.annual_repository.get_by_planning_id(annual_planning_id)
        if not annual:
            raise NotFoundException("Planejamento anual", str(annual_planning_id))

        goal = QuarterlyGoal(
            annual_planning_id=annual.id,
            quarter=quarter,
            target_amount=target_amount,
            actual_amount=Decimal("0"),
            description=description,
        )

        goal = await self.quarterly_repository.create(goal)
        await self.update_quarterly_progress(goal.id)
        return goal

    async def update_quarterly_progress(self, quarterly_goal_id: UUID) -> dict:
        """Calcula e atualiza progresso de meta trimestral"""
        goal = await self.quarterly_repository.get_by_id(quarterly_goal_id)
        if not goal:
            raise NotFoundException("Meta trimestral", str(quarterly_goal_id))
        
        annual = await self.annual_repository.get_by_id(goal.annual_planning_id)
        if not annual:
            raise NotFoundException("Planejamento anual", str(goal.annual_planning_id))
        
        planning = await self.get_planning(annual.planning_id)
        
        # Calcular período do trimestre
        quarter_start_month = (goal.quarter - 1) * 3 + 1
        start_date = datetime(annual.year, quarter_start_month, 1)
        
        if goal.quarter == 4:
            end_date = datetime(annual.year + 1, 1, 1)
        else:
            end_date = datetime(annual.year, quarter_start_month + 3, 1)
        
        actual_amount = await self.transaction_repository.get_sum_by_period(
            user_id=planning.user_id,
            start_date=start_date,
            end_date=end_date,
            transaction_type="expense",
        )
        
        goal.actual_amount = Decimal(str(actual_amount))
        goal = await self.quarterly_repository.update(goal)
        
        target = goal.target_amount
        percentage = float((goal.actual_amount / target) * 100) if target > 0 else 0.0
        
        return {
            "quarterly_goal_id": quarterly_goal_id,
            "quarter": goal.quarter,
            "target_amount": target,
            "actual_amount": goal.actual_amount,
            "percentage": round(percentage, 2),
            "remaining_amount": target - goal.actual_amount,
        }

