from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from src.infrastructure.database.models.education import (
    EducationalContent,
    UserProgress,
    Quiz,
    QuizAttempt,
)


class EducationalContentRepository(ABC):
    """Interface para repositório de conteúdo educativo"""

    @abstractmethod
    async def create(self, content: EducationalContent) -> EducationalContent:
        pass

    @abstractmethod
    async def get_by_id(self, content_id: UUID) -> Optional[EducationalContent]:
        pass

    @abstractmethod
    async def get_all(
        self,
        content_type: Optional[str] = None,
        difficulty: Optional[int] = None,
        is_active: bool = True,
    ) -> List[EducationalContent]:
        pass

    @abstractmethod
    async def update(self, content: EducationalContent) -> EducationalContent:
        pass

    @abstractmethod
    async def delete(self, content_id: UUID) -> bool:
        pass


class UserProgressRepository(ABC):
    """Interface para repositório de progresso do usuário"""

    @abstractmethod
    async def create(self, progress: UserProgress) -> UserProgress:
        pass

    @abstractmethod
    async def get_by_user_and_content(
        self, user_id: UUID, content_id: UUID
    ) -> Optional[UserProgress]:
        pass

    @abstractmethod
    async def get_by_user_id(self, user_id: UUID) -> List[UserProgress]:
        pass

    @abstractmethod
    async def update(self, progress: UserProgress) -> UserProgress:
        pass


class QuizRepository(ABC):
    """Interface para repositório de quizzes"""

    @abstractmethod
    async def create(self, quiz: Quiz) -> Quiz:
        pass

    @abstractmethod
    async def get_by_id(self, quiz_id: UUID) -> Optional[Quiz]:
        pass

    @abstractmethod
    async def get_all(self, is_active: bool = True) -> List[Quiz]:
        pass

    @abstractmethod
    async def get_by_content_id(self, content_id: UUID) -> List[Quiz]:
        pass

    @abstractmethod
    async def update(self, quiz: Quiz) -> Quiz:
        pass


class QuizAttemptRepository(ABC):
    """Interface para repositório de tentativas de quiz"""

    @abstractmethod
    async def create(self, attempt: QuizAttempt) -> QuizAttempt:
        pass

    @abstractmethod
    async def get_by_user_id(self, user_id: UUID) -> List[QuizAttempt]:
        pass

    @abstractmethod
    async def get_by_quiz_id(self, quiz_id: UUID) -> List[QuizAttempt]:
        pass

    @abstractmethod
    async def get_user_attempts_for_quiz(
        self, user_id: UUID, quiz_id: UUID
    ) -> List[QuizAttempt]:
        pass

