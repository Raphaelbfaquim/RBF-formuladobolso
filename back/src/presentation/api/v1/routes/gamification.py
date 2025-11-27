from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from sqlalchemy.orm import joinedload
from src.presentation.schemas.gamification import (
    BadgeResponse,
    UserBadgeResponse,
    UserLevelResponse,
    ChallengeResponse,
    UserChallengeResponse,
    LeaderboardEntry,
)
from src.presentation.api.dependencies import get_current_active_user
from src.infrastructure.database.models.user import User
from src.infrastructure.database.base import get_db
from src.domain.repositories.gamification_repository import (
    BadgeRepository,
    UserBadgeRepository,
    UserLevelRepository,
    ChallengeRepository,
    UserChallengeRepository,
)
from src.domain.repositories.transaction_repository import TransactionRepository
from src.domain.repositories.goal_repository import GoalRepository
from src.infrastructure.repositories.gamification_repository import (
    SQLAlchemyBadgeRepository,
    SQLAlchemyUserBadgeRepository,
    SQLAlchemyUserLevelRepository,
    SQLAlchemyChallengeRepository,
    SQLAlchemyUserChallengeRepository,
)
from src.infrastructure.repositories.transaction_repository import SQLAlchemyTransactionRepository
from src.infrastructure.repositories.goal_repository import SQLAlchemyGoalRepository
from src.application.services.gamification_service import GamificationService
from src.infrastructure.database.models.gamification import Badge, UserBadge, UserLevel, Challenge, UserChallenge, BadgeType

router = APIRouter()


def get_badge_repository(db: AsyncSession = Depends(get_db)) -> BadgeRepository:
    return SQLAlchemyBadgeRepository(db)


def get_user_badge_repository(db: AsyncSession = Depends(get_db)) -> UserBadgeRepository:
    return SQLAlchemyUserBadgeRepository(db)


def get_user_level_repository(db: AsyncSession = Depends(get_db)) -> UserLevelRepository:
    return SQLAlchemyUserLevelRepository(db)


def get_challenge_repository(db: AsyncSession = Depends(get_db)) -> ChallengeRepository:
    return SQLAlchemyChallengeRepository(db)


def get_user_challenge_repository(db: AsyncSession = Depends(get_db)) -> UserChallengeRepository:
    return SQLAlchemyUserChallengeRepository(db)


def get_transaction_repository(db: AsyncSession = Depends(get_db)) -> TransactionRepository:
    return SQLAlchemyTransactionRepository(db)


def get_goal_repository(db: AsyncSession = Depends(get_db)) -> GoalRepository:
    return SQLAlchemyGoalRepository(db)


def get_gamification_service(
    badge_repo: BadgeRepository = Depends(get_badge_repository),
    user_badge_repo: UserBadgeRepository = Depends(get_user_badge_repository),
    user_level_repo: UserLevelRepository = Depends(get_user_level_repository),
    challenge_repo: ChallengeRepository = Depends(get_challenge_repository),
    user_challenge_repo: UserChallengeRepository = Depends(get_user_challenge_repository),
    transaction_repo: TransactionRepository = Depends(get_transaction_repository),
    goal_repo: GoalRepository = Depends(get_goal_repository),
) -> GamificationService:
    return GamificationService(
        badge_repo,
        user_badge_repo,
        user_level_repo,
        challenge_repo,
        user_challenge_repo,
        transaction_repo,
        goal_repo,
    )


@router.get("/level", response_model=UserLevelResponse)
async def get_user_level(
    gamification_service: GamificationService = Depends(get_gamification_service),
    current_user: User = Depends(get_current_active_user),
):
    """Obtém nível e pontos do usuário"""
    user_level = await gamification_service.initialize_user_level(current_user.id)
    
    # Calcular XP necessário para próximo nível (fórmula: nível * 100 + nível * 50)
    current_level = user_level.level
    xp_for_current_level = 0
    for level in range(1, current_level):
        xp_for_current_level += level * 100 + level * 50
    
    xp_for_next_level = xp_for_current_level + (current_level * 100 + current_level * 50)
    xp_needed = xp_for_next_level - user_level.experience_points
    xp_in_current_level = user_level.experience_points - xp_for_current_level
    xp_needed_for_next = xp_for_next_level - xp_for_current_level
    progress = (xp_in_current_level / xp_needed_for_next * 100) if xp_needed_for_next > 0 else 100
    
    return {
        "id": user_level.id,
        "level": user_level.level,
        "experience_points": user_level.experience_points,
        "total_points": user_level.total_points,
        "streak_days": user_level.streak_days,
        "last_activity_date": user_level.last_activity_date,
        "next_level_points": xp_for_next_level,
        "progress_to_next_level": max(0, min(100, progress)),
    }


@router.get("/badges", response_model=List[UserBadgeResponse])
async def get_user_badges(
    gamification_service: GamificationService = Depends(get_gamification_service),
    current_user: User = Depends(get_current_active_user),
):
    """Lista badges do usuário"""
    user_badges = await gamification_service.user_badge_repository.get_by_user_id(current_user.id)
    
    result = []
    for user_badge in user_badges:
        badge = await gamification_service.badge_repository.get_by_id(user_badge.badge_id)
        if badge:
            result.append({
                "id": user_badge.id,
                "badge": {
                    "id": badge.id,
                    "name": badge.name,
                    "description": badge.description,
                    "badge_type": badge.badge_type.value if hasattr(badge.badge_type, 'value') else str(badge.badge_type),
                    "icon": badge.icon,
                    "color": badge.color,
                    "points": badge.points,
                    "rarity": badge.rarity,
                },
                "earned_at": user_badge.earned_at,
                "progress": user_badge.progress,
            })
    
    return result


@router.get("/badges/available", response_model=List[BadgeResponse])
async def get_available_badges(
    gamification_service: GamificationService = Depends(get_gamification_service),
    current_user: User = Depends(get_current_active_user),
):
    """Lista todos os badges disponíveis"""
    badges = await gamification_service.badge_repository.get_all()
    user_badges = await gamification_service.user_badge_repository.get_by_user_id(current_user.id)
    earned_badge_ids = {ub.badge_id for ub in user_badges if ub.progress >= 100}
    
    result = []
    for badge in badges:
        result.append({
            "id": badge.id,
            "name": badge.name,
            "description": badge.description,
            "badge_type": badge.badge_type.value if hasattr(badge.badge_type, 'value') else str(badge.badge_type),
            "icon": badge.icon,
            "color": badge.color,
            "points": badge.points,
            "rarity": badge.rarity,
        })
    
    return result


@router.get("/challenges", response_model=List[ChallengeResponse])
async def get_active_challenges(
    gamification_service: GamificationService = Depends(get_gamification_service),
    current_user: User = Depends(get_current_active_user),
):
    """Lista desafios ativos"""
    challenges = await gamification_service.challenge_repository.get_active()
    
    result = []
    for challenge in challenges:
        result.append({
            "id": challenge.id,
            "name": challenge.name,
            "description": challenge.description,
            "challenge_type": challenge.challenge_type,
            "target_value": float(challenge.target_value) if challenge.target_value else None,
            "target_metric": challenge.target_metric,
            "reward_points": challenge.reward_points,
            "start_date": challenge.start_date,
            "end_date": challenge.end_date,
            "badge_id": challenge.badge_id,
        })
    
    return result


@router.get("/challenges/my", response_model=List[UserChallengeResponse])
async def get_my_challenges(
    gamification_service: GamificationService = Depends(get_gamification_service),
    current_user: User = Depends(get_current_active_user),
):
    """Lista desafios do usuário"""
    user_challenges = await gamification_service.user_challenge_repository.get_by_user_id(current_user.id)
    
    result = []
    for user_challenge in user_challenges:
        challenge = await gamification_service.challenge_repository.get_by_id(user_challenge.challenge_id)
        if challenge:
            result.append({
                "id": user_challenge.id,
                "challenge": {
                    "id": challenge.id,
                    "name": challenge.name,
                    "description": challenge.description,
                    "challenge_type": challenge.challenge_type,
                    "target_value": float(challenge.target_value) if challenge.target_value else None,
                    "target_metric": challenge.target_metric,
                    "reward_points": challenge.reward_points,
                    "start_date": challenge.start_date,
                    "end_date": challenge.end_date,
                    "badge_id": challenge.badge_id,
                },
                "current_value": float(user_challenge.current_value),
                "progress_percentage": user_challenge.progress_percentage,
                "is_completed": user_challenge.is_completed,
                "completed_at": user_challenge.completed_at,
            })
    
    return result


@router.post("/challenges/{challenge_id}/join", response_model=UserChallengeResponse)
async def join_challenge(
    challenge_id: UUID,
    gamification_service: GamificationService = Depends(get_gamification_service),
    current_user: User = Depends(get_current_active_user),
):
    """Entra em um desafio"""
    user_challenge = await gamification_service.join_challenge(current_user.id, challenge_id)
    challenge = await gamification_service.challenge_repository.get_by_id(challenge_id)
    
    return {
        "id": user_challenge.id,
        "challenge": {
            "id": challenge.id,
            "name": challenge.name,
            "description": challenge.description,
            "challenge_type": challenge.challenge_type,
            "target_value": float(challenge.target_value) if challenge.target_value else None,
            "target_metric": challenge.target_metric,
            "reward_points": challenge.reward_points,
            "start_date": challenge.start_date,
            "end_date": challenge.end_date,
            "badge_id": challenge.badge_id,
        },
        "current_value": float(user_challenge.current_value),
        "progress_percentage": user_challenge.progress_percentage,
        "is_completed": user_challenge.is_completed,
        "completed_at": user_challenge.completed_at,
    }


@router.get("/leaderboard", response_model=List[LeaderboardEntry])
async def get_leaderboard(
    limit: int = Query(10, ge=1, le=100),
    scope: str = Query("global", regex="^(global|family|workspace)$"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Obtém ranking de usuários"""
    from src.infrastructure.database.models.user import User
    from src.infrastructure.database.models.gamification import UserLevel
    
    try:
        # Query começando de UserLevel e fazendo join com User
        query = select(
            UserLevel.user_id,
            User.name.label("username"),
            UserLevel.level,
            UserLevel.total_points,
        ).select_from(UserLevel).join(User, UserLevel.user_id == User.id)
        
        # Filtrar por escopo (futuro: family, workspace)
        if scope == "global":
            pass  # Todos os usuários
        # TODO: Adicionar filtros para family e workspace
        
        # Ordenar por total_points e limitar
        query = query.order_by(desc(UserLevel.total_points)).limit(limit)
        
        result = await db.execute(query)
        rows = result.all()
        
        leaderboard = []
        for idx, row in enumerate(rows, 1):
            leaderboard.append({
                "user_id": row.user_id,
                "username": row.username or "Usuário",
                "level": row.level or 1,
                "total_points": row.total_points or 0,
                "rank": idx,
            })
        
        return leaderboard
    except Exception as e:
        # Se não houver UserLevels, retornar lista vazia
        print(f"[DEBUG] Erro ao buscar leaderboard: {e}")
        import traceback
        traceback.print_exc()
        return []


@router.post("/update-streak")
async def update_streak(
    gamification_service: GamificationService = Depends(get_gamification_service),
    current_user: User = Depends(get_current_active_user),
):
    """Atualiza streak do usuário (chamado ao fazer login)"""
    user_level = await gamification_service.update_streak(current_user.id)
    
    # Adicionar XP por login diário
    await gamification_service.add_points(current_user.id, 5, "Login diário")
    
    return {
        "streak_days": user_level.streak_days,
        "message": f"Streak atualizado! {user_level.streak_days} dias consecutivos"
    }


@router.post("/seed-badges")
async def seed_badges(
    force: bool = Query(False),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Popula o banco com badges padrão"""
    badge_repo = SQLAlchemyBadgeRepository(db)
    
    existing = await badge_repo.get_all()
    if len(existing) > 0 and not force:
        return {
            "message": f"Já existem {len(existing)} badges no banco.",
            "existing_count": len(existing),
            "hint": "Use ?force=true para recriar todos os badges"
        }
    
    if force:
        for badge in existing:
            await db.delete(badge)
        await db.commit()
    
    badges_data = [
        # Conquistas de Uso
        {"name": "Primeiro Passo", "description": "Registrar primeira transação", "badge_type": BadgeType.ACHIEVEMENT, "icon": "🎯", "color": "#10b981", "points": 10, "rarity": "common"},
        {"name": "Organizado", "description": "Registrar 10 transações", "badge_type": BadgeType.ACHIEVEMENT, "icon": "📝", "color": "#3b82f6", "points": 25, "rarity": "common"},
        {"name": "Mestre das Transações", "description": "Registrar 100 transações", "badge_type": BadgeType.MILESTONE, "icon": "👑", "color": "#8b5cf6", "points": 100, "rarity": "epic"},
        {"name": "Consistente", "description": "7 dias consecutivos usando o app", "badge_type": BadgeType.ACHIEVEMENT, "icon": "🔥", "color": "#f59e0b", "points": 50, "rarity": "rare"},
        {"name": "Veterano", "description": "30 dias consecutivos", "badge_type": BadgeType.MILESTONE, "icon": "⭐", "color": "#ef4444", "points": 200, "rarity": "epic"},
        {"name": "Lendário", "description": "365 dias consecutivos", "badge_type": BadgeType.MILESTONE, "icon": "🏆", "color": "#fbbf24", "points": 1000, "rarity": "legendary"},
        
        # Conquistas Financeiras
        {"name": "Primeiro Verde", "description": "Primeiro mês com economia positiva", "badge_type": BadgeType.ACHIEVEMENT, "icon": "💚", "color": "#10b981", "points": 50, "rarity": "rare"},
        {"name": "Economista Júnior", "description": "Economizar R$ 1.000", "badge_type": BadgeType.MILESTONE, "icon": "💰", "color": "#3b82f6", "points": 100, "rarity": "rare"},
        {"name": "Economista Sênior", "description": "Economizar R$ 10.000", "badge_type": BadgeType.MILESTONE, "icon": "💎", "color": "#8b5cf6", "points": 500, "rarity": "epic"},
        {"name": "Milionário", "description": "Economizar R$ 100.000", "badge_type": BadgeType.MILESTONE, "icon": "💵", "color": "#fbbf24", "points": 2000, "rarity": "legendary"},
        {"name": "Sem Dívidas", "description": "Ficar 30 dias sem dívidas", "badge_type": BadgeType.ACHIEVEMENT, "icon": "✅", "color": "#10b981", "points": 150, "rarity": "epic"},
        {"name": "Reserva Completa", "description": "Ter reserva de emergência completa", "badge_type": BadgeType.ACHIEVEMENT, "icon": "🏦", "color": "#3b82f6", "points": 200, "rarity": "epic"},
        
        # Conquistas de Metas
        {"name": "Sonhador", "description": "Criar primeira meta", "badge_type": BadgeType.ACHIEVEMENT, "icon": "🎯", "color": "#10b981", "points": 25, "rarity": "common"},
        {"name": "Realizador", "description": "Alcançar primeira meta", "badge_type": BadgeType.ACHIEVEMENT, "icon": "🎉", "color": "#3b82f6", "points": 100, "rarity": "rare"},
        {"name": "Campeão", "description": "Alcançar 5 metas", "badge_type": BadgeType.MILESTONE, "icon": "🏅", "color": "#8b5cf6", "points": 300, "rarity": "epic"},
        {"name": "Conquistador", "description": "Alcançar 10 metas", "badge_type": BadgeType.MILESTONE, "icon": "👑", "color": "#f59e0b", "points": 500, "rarity": "epic"},
        {"name": "Mestre dos Sonhos", "description": "Alcançar 20 metas", "badge_type": BadgeType.MILESTONE, "icon": "🌟", "color": "#fbbf24", "points": 1000, "rarity": "legendary"},
        
        # Conquistas de Educação
        {"name": "Estudante", "description": "Completar primeiro curso", "badge_type": BadgeType.ACHIEVEMENT, "icon": "📚", "color": "#10b981", "points": 30, "rarity": "common"},
        {"name": "Aprendiz", "description": "Completar 5 cursos", "badge_type": BadgeType.MILESTONE, "icon": "🎓", "color": "#3b82f6", "points": 150, "rarity": "rare"},
        {"name": "Mestre do Conhecimento", "description": "Completar 10 cursos", "badge_type": BadgeType.MILESTONE, "icon": "🧠", "color": "#8b5cf6", "points": 400, "rarity": "epic"},
        {"name": "Sábio Financeiro", "description": "Completar todos os cursos", "badge_type": BadgeType.MILESTONE, "icon": "✨", "color": "#fbbf24", "points": 1000, "rarity": "legendary"},
        {"name": "Quiz Master", "description": "Acertar 90%+ em 10 quizzes", "badge_type": BadgeType.ACHIEVEMENT, "icon": "🎯", "color": "#ef4444", "points": 300, "rarity": "epic"},
        
        # Conquistas de Investimentos
        {"name": "Investidor Iniciante", "description": "Registrar primeiro investimento", "badge_type": BadgeType.ACHIEVEMENT, "icon": "📈", "color": "#10b981", "points": 20, "rarity": "common"},
        {"name": "Diversificador", "description": "Ter 5 tipos diferentes de investimentos", "badge_type": BadgeType.ACHIEVEMENT, "icon": "🎯", "color": "#3b82f6", "points": 150, "rarity": "rare"},
        {"name": "Portfolio Master", "description": "Ter R$ 50.000 investidos", "badge_type": BadgeType.MILESTONE, "icon": "💼", "color": "#8b5cf6", "points": 500, "rarity": "epic"},
        {"name": "Warren Buffett", "description": "Ter R$ 500.000 investidos", "badge_type": BadgeType.MILESTONE, "icon": "💰", "color": "#fbbf24", "points": 2000, "rarity": "legendary"},
        
        # Conquistas de Planejamento
        {"name": "Planejador", "description": "Criar primeiro planejamento", "badge_type": BadgeType.ACHIEVEMENT, "icon": "📅", "color": "#10b981", "points": 25, "rarity": "common"},
        {"name": "Disciplinado", "description": "Seguir planejamento por 3 meses", "badge_type": BadgeType.MILESTONE, "icon": "📊", "color": "#3b82f6", "points": 200, "rarity": "rare"},
        {"name": "Mestre do Orçamento", "description": "Seguir planejamento por 12 meses", "badge_type": BadgeType.MILESTONE, "icon": "👑", "color": "#8b5cf6", "points": 800, "rarity": "epic"},
        {"name": "50-30-20 Master", "description": "Usar regra 50-30-20 por 6 meses", "badge_type": BadgeType.ACHIEVEMENT, "icon": "🎯", "color": "#f59e0b", "points": 400, "rarity": "epic"},
        
        # Conquistas Especiais
        {"name": "Aniversário", "description": "1 ano usando o app", "badge_type": BadgeType.SPECIAL, "icon": "🎂", "color": "#ec4899", "points": 500, "rarity": "epic"},
        {"name": "Família Unida", "description": "Todos os membros da família ativos", "badge_type": BadgeType.SPECIAL, "icon": "👨‍👩‍👧‍👦", "color": "#8b5cf6", "points": 300, "rarity": "epic"},
        {"name": "Compartilhador", "description": "Compartilhar 10 eventos no calendário", "badge_type": BadgeType.ACHIEVEMENT, "icon": "📅", "color": "#3b82f6", "points": 100, "rarity": "rare"},
        {"name": "Analista", "description": "Gerar 50 relatórios", "badge_type": BadgeType.MILESTONE, "icon": "📊", "color": "#8b5cf6", "points": 250, "rarity": "epic"},
    ]
    
    created = []
    for badge_data in badges_data:
        existing_badges = await badge_repo.get_all()
        exists = any(b.name == badge_data["name"] for b in existing_badges)
        
        if not exists:
            badge = Badge(**badge_data)
            badge = await badge_repo.create(badge)
            created.append(badge.name)
    
    if len(created) == 0:
        return {
            "message": "Todos os badges já existem no banco.",
            "created": [],
            "total": 0,
            "existing_count": len(existing)
        }
    
    return {
        "message": f"{len(created)} badges criados com sucesso!",
        "created": created,
        "total": len(created)
    }

