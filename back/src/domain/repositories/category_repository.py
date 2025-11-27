from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from src.infrastructure.database.models.category import Category


class CategoryRepository(ABC):
    """Interface do repositório de categorias"""

    @abstractmethod
    async def create(self, category: Category) -> Category:
        pass

    @abstractmethod
    async def get_by_id(self, category_id: UUID) -> Optional[Category]:
        pass

    @abstractmethod
    async def get_by_user_id(self, user_id: UUID) -> List[Category]:
        pass

    @abstractmethod
    async def update(self, category: Category) -> Category:
        pass

    @abstractmethod
    async def delete(self, category_id: UUID) -> bool:
        pass

