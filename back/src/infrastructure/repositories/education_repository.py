from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import joinedload
from src.domain.repositories.education_repository import (
    EducationalContentRepository,
    UserProgressRepository,
    QuizRepository,
    QuizAttemptRepository,
)
from src.infrastructure.database.models.education import (
    EducationalContent,
    UserProgress,
    Quiz,
    QuizAttempt,
    ContentType,
)


class SQLAlchemyEducationalContentRepository(EducationalContentRepository):
    """Implementação do repositório de conteúdo educativo com SQLAlchemy"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, content: EducationalContent) -> EducationalContent:
        self.session.add(content)
        await self.session.commit()
        await self.session.refresh(content)
        return content

    async def get_by_id(self, content_id: UUID) -> Optional[EducationalContent]:
        result = await self.session.execute(
            select(EducationalContent).where(EducationalContent.id == content_id)
        )
        return result.scalar_one_or_none()

    async def get_all(
        self,
        content_type: Optional[str] = None,
        difficulty: Optional[int] = None,
        is_active: bool = True,
    ) -> List[EducationalContent]:
        query = select(EducationalContent).where(EducationalContent.is_active == is_active)

        if content_type:
            try:
                content_type_enum = ContentType(content_type)
                query = query.where(EducationalContent.content_type == content_type_enum)
            except ValueError:
                pass

        if difficulty:
            query = query.where(EducationalContent.difficulty_level == difficulty)

        query = query.order_by(EducationalContent.created_at.desc())
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def update(self, content: EducationalContent) -> EducationalContent:
        await self.session.commit()
        await self.session.refresh(content)
        return content

    async def delete(self, content_id: UUID) -> bool:
        content = await self.get_by_id(content_id)
        if content:
            await self.session.delete(content)
            await self.session.commit()
            return True
        return False


class SQLAlchemyUserProgressRepository(UserProgressRepository):
    """Implementação do repositório de progresso do usuário com SQLAlchemy"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, progress: UserProgress) -> UserProgress:
        self.session.add(progress)
        await self.session.commit()
        await self.session.refresh(progress)
        return progress

    async def get_by_user_and_content(
        self, user_id: UUID, content_id: UUID
    ) -> Optional[UserProgress]:
        result = await self.session.execute(
            select(UserProgress)
            .options(joinedload(UserProgress.content))
            .where(
                and_(
                    UserProgress.user_id == user_id,
                    UserProgress.content_id == content_id,
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_by_user_id(self, user_id: UUID) -> List[UserProgress]:
        result = await self.session.execute(
            select(UserProgress)
            .options(joinedload(UserProgress.content))
            .where(UserProgress.user_id == user_id)
            .order_by(UserProgress.updated_at.desc())
        )
        return list(result.scalars().all())

    async def update(self, progress: UserProgress) -> UserProgress:
        await self.session.commit()
        await self.session.refresh(progress)
        return progress


class SQLAlchemyQuizRepository(QuizRepository):
    """Implementação do repositório de quizzes com SQLAlchemy"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, quiz: Quiz) -> Quiz:
        self.session.add(quiz)
        await self.session.commit()
        await self.session.refresh(quiz)
        return quiz

    async def get_by_id(self, quiz_id: UUID) -> Optional[Quiz]:
        result = await self.session.execute(
            select(Quiz)
            .options(joinedload(Quiz.content))
            .where(Quiz.id == quiz_id)
        )
        return result.scalar_one_or_none()

    async def get_all(self, is_active: bool = True) -> List[Quiz]:
        result = await self.session.execute(
            select(Quiz)
            .options(joinedload(Quiz.content))
            .where(Quiz.is_active == is_active)
            .order_by(Quiz.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_by_content_id(self, content_id: UUID) -> List[Quiz]:
        result = await self.session.execute(
            select(Quiz)
            .options(joinedload(Quiz.content))
            .where(Quiz.content_id == content_id)
            .order_by(Quiz.created_at.desc())
        )
        return list(result.scalars().all())

    async def update(self, quiz: Quiz) -> Quiz:
        await self.session.commit()
        await self.session.refresh(quiz)
        return quiz


class SQLAlchemyQuizAttemptRepository(QuizAttemptRepository):
    """Implementação do repositório de tentativas de quiz com SQLAlchemy"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, attempt: QuizAttempt) -> QuizAttempt:
        self.session.add(attempt)
        await self.session.commit()
        await self.session.refresh(attempt)
        return attempt

    async def get_by_user_id(self, user_id: UUID) -> List[QuizAttempt]:
        result = await self.session.execute(
            select(QuizAttempt)
            .options(joinedload(QuizAttempt.quiz))
            .where(QuizAttempt.user_id == user_id)
            .order_by(QuizAttempt.completed_at.desc())
        )
        return list(result.scalars().all())

    async def get_by_quiz_id(self, quiz_id: UUID) -> List[QuizAttempt]:
        result = await self.session.execute(
            select(QuizAttempt)
            .options(joinedload(QuizAttempt.user))
            .where(QuizAttempt.quiz_id == quiz_id)
            .order_by(QuizAttempt.completed_at.desc())
        )
        return list(result.scalars().all())

    async def get_user_attempts_for_quiz(
        self, user_id: UUID, quiz_id: UUID
    ) -> List[QuizAttempt]:
        result = await self.session.execute(
            select(QuizAttempt)
            .options(joinedload(QuizAttempt.quiz))
            .where(
                and_(
                    QuizAttempt.user_id == user_id,
                    QuizAttempt.quiz_id == quiz_id,
                )
            )
            .order_by(QuizAttempt.completed_at.desc())
        )
        return list(result.scalars().all())

