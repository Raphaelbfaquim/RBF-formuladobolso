from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.domain.repositories.goal_repository import GoalRepository, GoalContributionRepository
from src.infrastructure.database.models.goal import Goal, GoalContribution


class SQLAlchemyGoalRepository(GoalRepository):
    """Implementação do repositório de metas com SQLAlchemy"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, goal: Goal) -> Goal:
        self.session.add(goal)
        await self.session.commit()
        await self.session.refresh(goal)
        return goal

    async def get_by_id(self, goal_id: UUID) -> Optional[Goal]:
        result = await self.session.execute(select(Goal).where(Goal.id == goal_id))
        return result.scalar_one_or_none()

    async def get_by_user_id(self, user_id: UUID) -> List[Goal]:
        result = await self.session.execute(
            select(Goal).where(Goal.user_id == user_id).order_by(Goal.created_at.desc())
        )
        return list(result.scalars().all())

    async def update(self, goal: Goal) -> Goal:
        await self.session.commit()
        await self.session.refresh(goal)
        return goal

    async def delete(self, goal_id: UUID) -> bool:
        goal = await self.get_by_id(goal_id)
        if goal:
            await self.session.delete(goal)
            await self.session.commit()
            return True
        return False


class SQLAlchemyGoalContributionRepository(GoalContributionRepository):
    """Implementação do repositório de contribuições com SQLAlchemy"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, contribution: GoalContribution) -> GoalContribution:
        self.session.add(contribution)
        await self.session.commit()
        await self.session.refresh(contribution)
        return contribution

    async def get_by_goal_id(self, goal_id: UUID) -> List[GoalContribution]:
        result = await self.session.execute(
            select(GoalContribution)
            .where(GoalContribution.goal_id == goal_id)
            .order_by(GoalContribution.contribution_date.desc())
        )
        return list(result.scalars().all())

    async def get_by_id(self, contribution_id: UUID) -> Optional[GoalContribution]:
        result = await self.session.execute(
            select(GoalContribution).where(GoalContribution.id == contribution_id)
        )
        return result.scalar_one_or_none()

    async def delete(self, contribution_id: UUID) -> bool:
        contribution = await self.get_by_id(contribution_id)
        if contribution:
            await self.session.delete(contribution)
            await self.session.commit()
            return True
        return False

