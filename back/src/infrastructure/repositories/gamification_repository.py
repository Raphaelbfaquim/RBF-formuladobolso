from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.domain.repositories.gamification_repository import (
    BadgeRepository,
    UserBadgeRepository,
    UserLevelRepository,
    ChallengeRepository,
    UserChallengeRepository,
)
from src.infrastructure.database.models.gamification import (
    Badge,
    UserBadge,
    UserLevel,
    Challenge,
    UserChallenge,
)


class SQLAlchemyBadgeRepository(BadgeRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, badge: Badge) -> Badge:
        self.session.add(badge)
        await self.session.commit()
        await self.session.refresh(badge)
        return badge

    async def get_by_id(self, badge_id: UUID) -> Optional[Badge]:
        result = await self.session.execute(select(Badge).where(Badge.id == badge_id))
        return result.scalar_one_or_none()

    async def get_all(self) -> List[Badge]:
        result = await self.session.execute(select(Badge).where(Badge.is_active == True))
        return list(result.scalars().all())

    async def get_by_type(self, badge_type: str) -> List[Badge]:
        result = await self.session.execute(
            select(Badge).where(Badge.badge_type == badge_type, Badge.is_active == True)
        )
        return list(result.scalars().all())


class SQLAlchemyUserBadgeRepository(UserBadgeRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user_badge: UserBadge) -> UserBadge:
        self.session.add(user_badge)
        await self.session.commit()
        await self.session.refresh(user_badge)
        return user_badge

    async def get_by_user_id(self, user_id: UUID) -> List[UserBadge]:
        result = await self.session.execute(
            select(UserBadge).where(UserBadge.user_id == user_id).order_by(UserBadge.earned_at.desc())
        )
        return list(result.scalars().all())

    async def get_by_user_and_badge(self, user_id: UUID, badge_id: UUID) -> Optional[UserBadge]:
        result = await self.session.execute(
            select(UserBadge).where(UserBadge.user_id == user_id, UserBadge.badge_id == badge_id)
        )
        return result.scalar_one_or_none()

    async def update(self, user_badge: UserBadge) -> UserBadge:
        await self.session.commit()
        await self.session.refresh(user_badge)
        return user_badge


class SQLAlchemyUserLevelRepository(UserLevelRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user_level: UserLevel) -> UserLevel:
        self.session.add(user_level)
        await self.session.commit()
        await self.session.refresh(user_level)
        return user_level

    async def get_by_user_id(self, user_id: UUID) -> Optional[UserLevel]:
        result = await self.session.execute(select(UserLevel).where(UserLevel.user_id == user_id))
        return result.scalar_one_or_none()

    async def update(self, user_level: UserLevel) -> UserLevel:
        await self.session.commit()
        await self.session.refresh(user_level)
        return user_level


class SQLAlchemyChallengeRepository(ChallengeRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, challenge: Challenge) -> Challenge:
        self.session.add(challenge)
        await self.session.commit()
        await self.session.refresh(challenge)
        return challenge

    async def get_by_id(self, challenge_id: UUID) -> Optional[Challenge]:
        result = await self.session.execute(select(Challenge).where(Challenge.id == challenge_id))
        return result.scalar_one_or_none()

    async def get_active(self) -> List[Challenge]:
        from datetime import datetime
        import pytz
        now = datetime.now(pytz.UTC)
        result = await self.session.execute(
            select(Challenge).where(
                Challenge.is_active == True,
                Challenge.start_date <= now,
                Challenge.end_date >= now,
            )
        )
        return list(result.scalars().all())

    async def update(self, challenge: Challenge) -> Challenge:
        await self.session.commit()
        await self.session.refresh(challenge)
        return challenge


class SQLAlchemyUserChallengeRepository(UserChallengeRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user_challenge: UserChallenge) -> UserChallenge:
        self.session.add(user_challenge)
        await self.session.commit()
        await self.session.refresh(user_challenge)
        return user_challenge

    async def get_by_user_id(self, user_id: UUID) -> List[UserChallenge]:
        result = await self.session.execute(
            select(UserChallenge).where(UserChallenge.user_id == user_id)
        )
        return list(result.scalars().all())

    async def get_by_user_and_challenge(self, user_id: UUID, challenge_id: UUID) -> Optional[UserChallenge]:
        result = await self.session.execute(
            select(UserChallenge).where(
                UserChallenge.user_id == user_id, UserChallenge.challenge_id == challenge_id
            )
        )
        return result.scalar_one_or_none()

    async def update(self, user_challenge: UserChallenge) -> UserChallenge:
        await self.session.commit()
        await self.session.refresh(user_challenge)
        return user_challenge

