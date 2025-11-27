from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from src.infrastructure.database.models.planning import (
    Planning,
    MonthlyPlanning,
    WeeklyPlanning,
    DailyPlanning,
    AnnualPlanning,
    QuarterlyGoal,
)


class PlanningRepository(ABC):
    """Interface do repositório de planejamentos"""

    @abstractmethod
    async def create(self, planning: Planning) -> Planning:
        """Cria um novo planejamento"""
        pass

    @abstractmethod
    async def get_by_id(self, planning_id: UUID) -> Optional[Planning]:
        """Obtém planejamento por ID"""
        pass

    @abstractmethod
    async def get_by_user_id(self, user_id: UUID) -> List[Planning]:
        """Obtém planejamentos de um usuário"""
        pass

    @abstractmethod
    async def update(self, planning: Planning) -> Planning:
        """Atualiza um planejamento"""
        pass

    @abstractmethod
    async def delete(self, planning_id: UUID) -> bool:
        """Deleta um planejamento"""
        pass


class MonthlyPlanningRepository(ABC):
    """Interface do repositório de planejamentos mensais"""

    @abstractmethod
    async def create(self, monthly_planning: MonthlyPlanning) -> MonthlyPlanning:
        pass

    @abstractmethod
    async def get_by_planning_id(self, planning_id: UUID) -> List[MonthlyPlanning]:
        pass

    @abstractmethod
    async def get_by_month_year(
        self, planning_id: UUID, month: int, year: int
    ) -> Optional[MonthlyPlanning]:
        pass

    @abstractmethod
    async def get_by_id(self, monthly_planning_id: UUID) -> Optional[MonthlyPlanning]:
        pass

    @abstractmethod
    async def update(self, monthly_planning: MonthlyPlanning) -> MonthlyPlanning:
        pass


class WeeklyPlanningRepository(ABC):
    """Interface do repositório de planejamentos semanais"""

    @abstractmethod
    async def create(self, weekly_planning: WeeklyPlanning) -> WeeklyPlanning:
        pass

    @abstractmethod
    async def get_by_planning_id(self, planning_id: UUID) -> List[WeeklyPlanning]:
        pass

    @abstractmethod
    async def update(self, weekly_planning: WeeklyPlanning) -> WeeklyPlanning:
        pass


class DailyPlanningRepository(ABC):
    """Interface do repositório de planejamentos diários"""

    @abstractmethod
    async def create(self, daily_planning: DailyPlanning) -> DailyPlanning:
        pass

    @abstractmethod
    async def get_by_planning_id(self, planning_id: UUID) -> List[DailyPlanning]:
        pass

    @abstractmethod
    async def get_by_date(
        self, planning_id: UUID, date: datetime
    ) -> Optional[DailyPlanning]:
        pass

    @abstractmethod
    async def update(self, daily_planning: DailyPlanning) -> DailyPlanning:
        pass


class AnnualPlanningRepository(ABC):
    """Interface do repositório de planejamentos anuais"""

    @abstractmethod
    async def create(self, annual_planning: AnnualPlanning) -> AnnualPlanning:
        pass

    @abstractmethod
    async def get_by_planning_id(
        self, planning_id: UUID
    ) -> Optional[AnnualPlanning]:
        pass

    @abstractmethod
    async def update(self, annual_planning: AnnualPlanning) -> AnnualPlanning:
        pass


class QuarterlyGoalRepository(ABC):
    """Interface do repositório de metas trimestrais"""

    @abstractmethod
    async def create(self, quarterly_goal: QuarterlyGoal) -> QuarterlyGoal:
        pass

    @abstractmethod
    async def get_by_annual_planning_id(
        self, annual_planning_id: UUID
    ) -> List[QuarterlyGoal]:
        pass

    @abstractmethod
    async def get_by_id(self, quarterly_goal_id: UUID) -> Optional[QuarterlyGoal]:
        pass

    @abstractmethod
    async def get_by_quarter(
        self, annual_planning_id: UUID, quarter: int
    ) -> Optional[QuarterlyGoal]:
        pass

    @abstractmethod
    async def update(self, quarterly_goal: QuarterlyGoal) -> QuarterlyGoal:
        pass

