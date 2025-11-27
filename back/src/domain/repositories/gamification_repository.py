from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from src.infrastructure.database.models.gamification import (
    Badge,
    UserBadge,
    UserLevel,
    Challenge,
    UserChallenge,
)


class BadgeRepository(ABC):
    """Interface do repositório de badges"""

    @abstractmethod
    async def create(self, badge: Badge) -> Badge:
        pass

    @abstractmethod
    async def get_by_id(self, badge_id: UUID) -> Optional[Badge]:
        pass

    @abstractmethod
    async def get_all(self) -> List[Badge]:
        pass

    @abstractmethod
    async def get_by_type(self, badge_type: str) -> List[Badge]:
        pass


class UserBadgeRepository(ABC):
    """Interface do repositório de badges de usuários"""

    @abstractmethod
    async def create(self, user_badge: UserBadge) -> UserBadge:
        pass

    @abstractmethod
    async def get_by_user_id(self, user_id: UUID) -> List[UserBadge]:
        pass

    @abstractmethod
    async def get_by_user_and_badge(self, user_id: UUID, badge_id: UUID) -> Optional[UserBadge]:
        pass

    @abstractmethod
    async def update(self, user_badge: UserBadge) -> UserBadge:
        pass


class UserLevelRepository(ABC):
    """Interface do repositório de níveis de usuários"""

    @abstractmethod
    async def create(self, user_level: UserLevel) -> UserLevel:
        pass

    @abstractmethod
    async def get_by_user_id(self, user_id: UUID) -> Optional[UserLevel]:
        pass

    @abstractmethod
    async def update(self, user_level: UserLevel) -> UserLevel:
        pass


class ChallengeRepository(ABC):
    """Interface do repositório de desafios"""

    @abstractmethod
    async def create(self, challenge: Challenge) -> Challenge:
        pass

    @abstractmethod
    async def get_by_id(self, challenge_id: UUID) -> Optional[Challenge]:
        pass

    @abstractmethod
    async def get_active(self) -> List[Challenge]:
        pass

    @abstractmethod
    async def update(self, challenge: Challenge) -> Challenge:
        pass


class UserChallengeRepository(ABC):
    """Interface do repositório de desafios de usuários"""

    @abstractmethod
    async def create(self, user_challenge: UserChallenge) -> UserChallenge:
        pass

    @abstractmethod
    async def get_by_user_id(self, user_id: UUID) -> List[UserChallenge]:
        pass

    @abstractmethod
    async def get_by_user_and_challenge(self, user_id: UUID, challenge_id: UUID) -> Optional[UserChallenge]:
        pass

    @abstractmethod
    async def update(self, user_challenge: UserChallenge) -> UserChallenge:
        pass

