from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from src.infrastructure.database.models.goal import Goal, GoalContribution


class GoalRepository(ABC):
    """Interface do repositório de metas"""

    @abstractmethod
    async def create(self, goal: Goal) -> Goal:
        """Cria uma nova meta"""
        pass

    @abstractmethod
    async def get_by_id(self, goal_id: UUID) -> Optional[Goal]:
        """Obtém meta por ID"""
        pass

    @abstractmethod
    async def get_by_user_id(self, user_id: UUID) -> List[Goal]:
        """Obtém todas as metas de um usuário"""
        pass

    @abstractmethod
    async def update(self, goal: Goal) -> Goal:
        """Atualiza uma meta"""
        pass

    @abstractmethod
    async def delete(self, goal_id: UUID) -> bool:
        """Deleta uma meta"""
        pass


class GoalContributionRepository(ABC):
    """Interface do repositório de contribuições para metas"""

    @abstractmethod
    async def create(self, contribution: GoalContribution) -> GoalContribution:
        """Cria uma nova contribuição"""
        pass

    @abstractmethod
    async def get_by_goal_id(self, goal_id: UUID) -> List[GoalContribution]:
        """Obtém todas as contribuições de uma meta"""
        pass

    @abstractmethod
    async def get_by_id(self, contribution_id: UUID) -> Optional[GoalContribution]:
        """Obtém contribuição por ID"""
        pass

    @abstractmethod
    async def delete(self, contribution_id: UUID) -> bool:
        """Deleta uma contribuição"""
        pass

