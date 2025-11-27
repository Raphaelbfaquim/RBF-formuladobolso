from typing import List, Optional
from uuid import UUID
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.domain.repositories.planning_repository import (
    PlanningRepository,
    MonthlyPlanningRepository,
    WeeklyPlanningRepository,
    DailyPlanningRepository,
    AnnualPlanningRepository,
    QuarterlyGoalRepository,
)
from src.infrastructure.database.models.planning import (
    Planning,
    MonthlyPlanning,
    WeeklyPlanning,
    DailyPlanning,
    AnnualPlanning,
    QuarterlyGoal,
)


class SQLAlchemyPlanningRepository(PlanningRepository):
    """Implementação do repositório de planejamentos com SQLAlchemy"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, planning: Planning) -> Planning:
        self.session.add(planning)
        await self.session.commit()
        await self.session.refresh(planning)
        return planning

    async def get_by_id(self, planning_id: UUID) -> Optional[Planning]:
        result = await self.session.execute(select(Planning).where(Planning.id == planning_id))
        return result.scalar_one_or_none()

    async def get_by_user_id(self, user_id: UUID) -> List[Planning]:
        result = await self.session.execute(
            select(Planning).where(Planning.user_id == user_id, Planning.is_active == True)
            .order_by(Planning.created_at.desc())
        )
        return list(result.scalars().all())

    async def update(self, planning: Planning) -> Planning:
        await self.session.commit()
        await self.session.refresh(planning)
        return planning

    async def delete(self, planning_id: UUID) -> bool:
        planning = await self.get_by_id(planning_id)
        if planning:
            planning.is_active = False
            await self.session.commit()
            return True
        return False


class SQLAlchemyMonthlyPlanningRepository(MonthlyPlanningRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, monthly_planning: MonthlyPlanning) -> MonthlyPlanning:
        self.session.add(monthly_planning)
        await self.session.commit()
        await self.session.refresh(monthly_planning)
        return monthly_planning

    async def get_by_planning_id(self, planning_id: UUID) -> List[MonthlyPlanning]:
        result = await self.session.execute(
            select(MonthlyPlanning).where(MonthlyPlanning.planning_id == planning_id)
        )
        return list(result.scalars().all())

    async def get_by_id(self, monthly_planning_id: UUID) -> Optional[MonthlyPlanning]:
        result = await self.session.execute(
            select(MonthlyPlanning).where(MonthlyPlanning.id == monthly_planning_id)
        )
        return result.scalar_one_or_none()

    async def get_by_month_year(
        self, planning_id: UUID, month: int, year: int
    ) -> Optional[MonthlyPlanning]:
        result = await self.session.execute(
            select(MonthlyPlanning).where(
                MonthlyPlanning.planning_id == planning_id,
                MonthlyPlanning.month == month,
                MonthlyPlanning.year == year,
            )
        )
        return result.scalar_one_or_none()

    async def update(self, monthly_planning: MonthlyPlanning) -> MonthlyPlanning:
        await self.session.commit()
        await self.session.refresh(monthly_planning)
        return monthly_planning


class SQLAlchemyWeeklyPlanningRepository(WeeklyPlanningRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, weekly_planning: WeeklyPlanning) -> WeeklyPlanning:
        self.session.add(weekly_planning)
        await self.session.commit()
        await self.session.refresh(weekly_planning)
        return weekly_planning

    async def get_by_planning_id(self, planning_id: UUID) -> List[WeeklyPlanning]:
        result = await self.session.execute(
            select(WeeklyPlanning).where(WeeklyPlanning.planning_id == planning_id)
        )
        return list(result.scalars().all())

    async def update(self, weekly_planning: WeeklyPlanning) -> WeeklyPlanning:
        await self.session.commit()
        await self.session.refresh(weekly_planning)
        return weekly_planning


class SQLAlchemyDailyPlanningRepository(DailyPlanningRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, daily_planning: DailyPlanning) -> DailyPlanning:
        self.session.add(daily_planning)
        await self.session.commit()
        await self.session.refresh(daily_planning)
        return daily_planning

    async def get_by_planning_id(self, planning_id: UUID) -> List[DailyPlanning]:
        result = await self.session.execute(
            select(DailyPlanning).where(DailyPlanning.planning_id == planning_id)
        )
        return list(result.scalars().all())

    async def get_by_date(
        self, planning_id: UUID, date: datetime
    ) -> Optional[DailyPlanning]:
        result = await self.session.execute(
            select(DailyPlanning).where(
                DailyPlanning.planning_id == planning_id,
                DailyPlanning.date == date,
            )
        )
        return result.scalar_one_or_none()

    async def update(self, daily_planning: DailyPlanning) -> DailyPlanning:
        await self.session.commit()
        await self.session.refresh(daily_planning)
        return daily_planning


class SQLAlchemyAnnualPlanningRepository(AnnualPlanningRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, annual_planning: AnnualPlanning) -> AnnualPlanning:
        self.session.add(annual_planning)
        await self.session.commit()
        await self.session.refresh(annual_planning)
        return annual_planning

    async def get_by_planning_id(
        self, planning_id: UUID
    ) -> Optional[AnnualPlanning]:
        result = await self.session.execute(
            select(AnnualPlanning).where(AnnualPlanning.planning_id == planning_id)
        )
        return result.scalar_one_or_none()

    async def update(self, annual_planning: AnnualPlanning) -> AnnualPlanning:
        await self.session.commit()
        await self.session.refresh(annual_planning)
        return annual_planning


class SQLAlchemyQuarterlyGoalRepository(QuarterlyGoalRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, quarterly_goal: QuarterlyGoal) -> QuarterlyGoal:
        self.session.add(quarterly_goal)
        await self.session.commit()
        await self.session.refresh(quarterly_goal)
        return quarterly_goal

    async def get_by_annual_planning_id(
        self, annual_planning_id: UUID
    ) -> List[QuarterlyGoal]:
        result = await self.session.execute(
            select(QuarterlyGoal).where(
                QuarterlyGoal.annual_planning_id == annual_planning_id
            )
        )
        return list(result.scalars().all())

    async def get_by_id(self, quarterly_goal_id: UUID) -> Optional[QuarterlyGoal]:
        result = await self.session.execute(
            select(QuarterlyGoal).where(QuarterlyGoal.id == quarterly_goal_id)
        )
        return result.scalar_one_or_none()

    async def get_by_quarter(
        self, annual_planning_id: UUID, quarter: int
    ) -> Optional[QuarterlyGoal]:
        result = await self.session.execute(
            select(QuarterlyGoal).where(
                QuarterlyGoal.annual_planning_id == annual_planning_id,
                QuarterlyGoal.quarter == quarter,
            )
        )
        return result.scalar_one_or_none()

    async def update(self, quarterly_goal: QuarterlyGoal) -> QuarterlyGoal:
        await self.session.commit()
        await self.session.refresh(quarterly_goal)
        return quarterly_goal

