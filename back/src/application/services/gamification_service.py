from typing import Optional, List
from uuid import UUID
from datetime import datetime, timedelta
import pytz
from decimal import Decimal
from src.domain.repositories.gamification_repository import (
    BadgeRepository,
    UserBadgeRepository,
    UserLevelRepository,
    ChallengeRepository,
    UserChallengeRepository,
)
from src.domain.repositories.transaction_repository import TransactionRepository
from src.domain.repositories.goal_repository import GoalRepository
from src.infrastructure.database.models.gamification import (
    Badge,
    UserBadge,
    UserLevel,
    Challenge,
    UserChallenge,
    BadgeType,
)
from src.shared.exceptions import NotFoundException


class GamificationService:
    """Serviço de gamificação - gerencia badges, níveis e desafios"""

    def __init__(
        self,
        badge_repository: BadgeRepository,
        user_badge_repository: UserBadgeRepository,
        user_level_repository: UserLevelRepository,
        challenge_repository: ChallengeRepository,
        user_challenge_repository: UserChallengeRepository,
        transaction_repository: TransactionRepository,
        goal_repository: GoalRepository,
    ):
        self.badge_repository = badge_repository
        self.user_badge_repository = user_badge_repository
        self.user_level_repository = user_level_repository
        self.challenge_repository = challenge_repository
        self.user_challenge_repository = user_challenge_repository
        self.transaction_repository = transaction_repository
        self.goal_repository = goal_repository

    async def initialize_user_level(self, user_id: UUID) -> UserLevel:
        """Inicializa nível do usuário"""
        existing = await self.user_level_repository.get_by_user_id(user_id)
        if existing:
            return existing

        user_level = UserLevel(
            user_id=user_id,
            level=1,
            experience_points=0,
            total_points=0,
            streak_days=0,
        )
        return await self.user_level_repository.create(user_level)

    async def add_points(self, user_id: UUID, points: int, reason: str = "") -> UserLevel:
        """Adiciona pontos ao usuário"""
        user_level = await self.user_level_repository.get_by_user_id(user_id)
        if not user_level:
            user_level = await self.initialize_user_level(user_id)

        user_level.total_points += points
        user_level.experience_points += points

        # Calcular novo nível (fórmula: nível * 100 + nível * 50)
        new_level = 1
        xp_accumulated = 0
        while xp_accumulated <= user_level.experience_points:
            xp_for_level = new_level * 100 + new_level * 50
            if xp_accumulated + xp_for_level > user_level.experience_points:
                break
            xp_accumulated += xp_for_level
            new_level += 1
        
        if new_level > user_level.level:
            user_level.level = new_level

        return await self.user_level_repository.update(user_level)

    async def award_badge(self, user_id: UUID, badge_id: UUID, progress: int = 100) -> UserBadge:
        """Concede um badge ao usuário"""
        # Verificar se já tem o badge
        existing = await self.user_badge_repository.get_by_user_and_badge(user_id, badge_id)
        if existing and existing.progress >= 100:
            return existing  # Já tem o badge completo

        badge = await self.badge_repository.get_by_id(badge_id)
        if not badge:
            raise NotFoundException("Badge", str(badge_id))

        if existing:
            existing.progress = progress
            if progress >= 100:
                existing.earned_at = datetime.now(pytz.UTC)
                # Adicionar pontos
                await self.add_points(user_id, badge.points, f"Badge: {badge.name}")
            return await self.user_badge_repository.update(existing)
        else:
            user_badge = UserBadge(
                user_id=user_id,
                badge_id=badge_id,
                progress=progress,
            )
            if progress >= 100:
                user_badge.earned_at = datetime.now(pytz.UTC)
                await self.add_points(user_id, badge.points, f"Badge: {badge.name}")
            return await self.user_badge_repository.create(user_badge)

    async def update_streak(self, user_id: UUID) -> UserLevel:
        """Atualiza streak de dias consecutivos"""
        user_level = await self.user_level_repository.get_by_user_id(user_id)
        if not user_level:
            user_level = await self.initialize_user_level(user_id)

        now = datetime.now(pytz.UTC).date()
        last_activity = user_level.last_activity_date.date() if user_level.last_activity_date else None

        if last_activity:
            days_diff = (now - last_activity).days
            if days_diff == 1:
                # Dia consecutivo
                user_level.streak_days += 1
            elif days_diff > 1:
                # Quebrou a sequência
                user_level.streak_days = 1
            # Se days_diff == 0, já atualizou hoje
        else:
            # Primeira vez
            user_level.streak_days = 1

        user_level.last_activity_date = datetime.now(pytz.UTC)

        # Badge por streak
        if user_level.streak_days == 7:
            await self._check_and_award_streak_badge(user_id, 7)
        elif user_level.streak_days == 30:
            await self._check_and_award_streak_badge(user_id, 30)
        elif user_level.streak_days == 100:
            await self._check_and_award_streak_badge(user_id, 100)

        return await self.user_level_repository.update(user_level)

    async def _check_and_award_streak_badge(self, user_id: UUID, days: int):
        """Verifica e concede badge de streak"""
        # Buscar badge de streak correspondente
        badges = await self.badge_repository.get_by_type(BadgeType.ACHIEVEMENT)
        for badge in badges:
            if f"{days}" in badge.name.lower() or "streak" in badge.name.lower():
                await self.award_badge(user_id, badge.id)

    async def check_achievements(self, user_id: UUID) -> List[UserBadge]:
        """Verifica e concede achievements automaticamente"""
        awarded = []

        # Verificar achievements baseados em transações
        transactions = await self.transaction_repository.get_by_user_id(user_id)
        total_transactions = len(transactions)
        
        # Badge "Primeiro Passo" - primeira transação
        if total_transactions == 1:
            badge = await self._find_badge_by_name("Primeiro Passo")
            if badge:
                awarded.append(await self.award_badge(user_id, badge.id))
        
        # Badge "Organizado" - 10 transações
        if total_transactions >= 10:
            badge = await self._find_badge_by_name("Organizado")
            if badge:
                awarded.append(await self.award_badge(user_id, badge.id))
        
        # Badge "Mestre das Transações" - 100 transações
        if total_transactions >= 100:
            badge = await self._find_badge_by_name("Mestre das Transações")
            if badge:
                awarded.append(await self.award_badge(user_id, badge.id))

        # Verificar achievements baseados em metas
        goals = await self.goal_repository.get_by_user_id(user_id)
        completed_goals = [g for g in goals if g.status.value == "completed"]
        
        # Badge "Sonhador" - criar primeira meta
        if len(goals) >= 1:
            badge = await self._find_badge_by_name("Sonhador")
            if badge:
                awarded.append(await self.award_badge(user_id, badge.id))
        
        # Badge "Realizador" - alcançar primeira meta
        if len(completed_goals) >= 1:
            badge = await self._find_badge_by_name("Realizador")
            if badge:
                awarded.append(await self.award_badge(user_id, badge.id))

        return awarded

    async def _find_badge_by_name(self, name: str) -> Optional[Badge]:
        """Encontra badge por nome"""
        badges = await self.badge_repository.get_all()
        for badge in badges:
            if name.lower() in badge.name.lower():
                return badge
        return None

    async def join_challenge(self, user_id: UUID, challenge_id: UUID) -> UserChallenge:
        """Usuário entra em um desafio"""
        existing = await self.user_challenge_repository.get_by_user_and_challenge(user_id, challenge_id)
        if existing:
            return existing

        challenge = await self.challenge_repository.get_by_id(challenge_id)
        if not challenge:
            raise NotFoundException("Desafio", str(challenge_id))

        user_challenge = UserChallenge(
            user_id=user_id,
            challenge_id=challenge_id,
            current_value=Decimal("0"),
            progress_percentage=0,
            is_completed=False,
        )

        return await self.user_challenge_repository.create(user_challenge)

    async def update_challenge_progress(
        self, user_id: UUID, challenge_id: UUID, value: Decimal
    ) -> UserChallenge:
        """Atualiza progresso de um desafio"""
        user_challenge = await self.user_challenge_repository.get_by_user_and_challenge(
            user_id, challenge_id
        )
        if not user_challenge:
            user_challenge = await self.join_challenge(user_id, challenge_id)

        challenge = await self.challenge_repository.get_by_id(challenge_id)
        if not challenge:
            raise NotFoundException("Desafio", str(challenge_id))

        user_challenge.current_value = value

        if challenge.target_value:
            progress = float((value / challenge.target_value) * 100)
            user_challenge.progress_percentage = min(int(progress), 100)

            if progress >= 100 and not user_challenge.is_completed:
                user_challenge.is_completed = True
                user_challenge.completed_at = datetime.now(pytz.UTC)
                # Adicionar pontos
                await self.add_points(user_id, challenge.reward_points, f"Desafio: {challenge.name}")
                # Conceder badge se houver
                if challenge.badge_id:
                    await self.award_badge(user_id, challenge.badge_id)

        return await self.user_challenge_repository.update(user_challenge)

