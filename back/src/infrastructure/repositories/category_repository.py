from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.domain.repositories.category_repository import CategoryRepository
from src.infrastructure.database.models.category import Category


class SQLAlchemyCategoryRepository(CategoryRepository):
    """Implementação do repositório de categorias com SQLAlchemy"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, category: Category) -> Category:
        self.session.add(category)
        await self.session.commit()
        await self.session.refresh(category)
        return category

    async def get_by_id(self, category_id: UUID) -> Optional[Category]:
        result = await self.session.execute(select(Category).where(Category.id == category_id))
        return result.scalar_one_or_none()

    async def get_by_user_id(self, user_id: UUID) -> List[Category]:
        result = await self.session.execute(
            select(Category).where(Category.user_id == user_id, Category.is_active == True)
        )
        return list(result.scalars().all())

    async def get_by_family_id(self, family_id: UUID) -> List[Category]:
        result = await self.session.execute(
            select(Category).where(Category.family_id == family_id, Category.is_active == True)
        )
        return list(result.scalars().all())

    async def update(self, category: Category) -> Category:
        await self.session.commit()
        await self.session.refresh(category)
        return category

    async def delete(self, category_id: UUID) -> bool:
        category = await self.get_by_id(category_id)
        if category:
            category.is_active = False
            await self.session.commit()
            return True
        return False

